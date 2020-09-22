"""
insar_gamma processing for HyP3
"""
import glob
import logging
import os
import shutil
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from mimetypes import guess_type
from shutil import make_archive

import boto3
from PIL import Image
from hyp3proclib import (
    build_output_name_pair,
    earlier_granule_first,
    extra_arg_is,
    failure,
    success,
    upload_product,
)
from hyp3proclib.db import get_db_connection
from hyp3proclib.file_system import cleanup_workdir
from hyp3proclib.logger import log
from hyp3proclib.proc_base import Processor
from pkg_resources import load_entry_point

import hyp3_insar_gamma
from hyp3_insar_gamma.stack_sentinel import procS1StackGAMMA


S3_CLIENT = boto3.client('s3')


def entry():
    parser = ArgumentParser(prefix_chars='+', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '++entrypoint', choices=['hyp3_insar_gamma', 'hyp3_insar_gamma_v2'], default='hyp3_insar_gamma',
        help='Select the HyP3 entrypoint version to use'
    )
    args, unknowns = parser.parse_known_args()

    sys.argv = [args.entrypoint, *unknowns]
    sys.exit(
        load_entry_point('hyp3_insar_gamma', 'console_scripts', args.entrypoint)()
    )


# Hyp3 V2 entrypoints
def get_content_type(filename):
    content_type = guess_type(filename)[0]
    if not content_type:
        content_type = 'application/octet-stream'
    return content_type


def upload_file_to_s3(path_to_file, file_type, bucket, prefix=''):
    key = os.path.join(prefix, os.path.basename(path_to_file))
    extra_args = {'ContentType': get_content_type(key)}

    logging.info(f'Uploading s3://{bucket}/{key}')
    S3_CLIENT.upload_file(path_to_file, bucket, key, extra_args)
    tag_set = {
        'TagSet': [
            {
                'Key': 'file_type',
                'Value': file_type
            }
        ]
    }
    S3_CLIENT.put_object_tagging(Bucket=bucket, Key=key, Tagging=tag_set)


def create_thumbnail(input_image, size=(100, 100)):
    filename, ext = os.path.splitext(input_image)
    thumbnail_name = f'{filename}_thumb{ext}'

    output_image = Image.open(input_image)
    output_image.thumbnail(size)
    output_image.save(thumbnail_name)
    return thumbnail_name


def string_is_true(s: str) -> bool:
    return s.lower() == 'true'


def main_v2():
    parser = ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('--include-inc-map', type=string_is_true, default=False)
    parser.add_argument('--include-los-displacement', type=string_is_true, default=False)
    parser.add_argument('--looks', choices=['20x4', '10x2'], default='20x4')
    parser.add_argument('granules', type=str.split, nargs='+')
    args = parser.parse_args()

    args.granules = [item for sublist in args.granules for item in sublist]
    if len(args.granules) != 2:
        parser.error('Must provide exactly two granules')

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    rlooks, alooks = (20, 4) if args.looks == '20x4' else (10, 2)

    granule_file = 'granules.txt'
    g1, g2 = earlier_granule_first(args.granules[0], args.granules[1])
    write_list_file(granule_file, g1, g2)

    with open('get_asf.cfg', 'w') as f:
        f.write(f'[general]\nusername={args.username}\npassword={args.password}')

    procS1StackGAMMA(
        alooks=alooks,
        rlooks=rlooks,
        csvFile=granule_file,
        inc_flag=args.include_inc_map,
        los_flag=args.include_los_displacement,
    )

    product_name = build_output_name_pair(g1, g2, os.getcwd(), f'-{args.looks}-int-gamma')
    log.info('Output product name: ' + product_name)
    os.rename('PRODUCTS', product_name)
    zip_file = make_archive(base_name=product_name, format='zip', base_dir=product_name)

    if args.bucket:
        upload_file_to_s3(zip_file, 'product', args.bucket, args.bucket_prefix)
        browse_images = glob.glob(f'{product_name}/*.png')
        for browse in browse_images:
            thumbnail = create_thumbnail(browse)
            upload_file_to_s3(browse, 'browse', args.bucket, args.bucket_prefix)
            upload_file_to_s3(thumbnail, 'thumbnail', args.bucket, args.bucket_prefix)
# End v2 entrypoints


def find_color_phase_png(dir_):
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith("color_phase.png"):
                log.info('Browse image: ' + filepath)
                return filepath

    return None


def write_list_file(list_file, g1, g2):
    with open(list_file, 'w') as f:
        f.write(g1 + '\n')
        f.write(g2 + '\n')


def find_product(dir_):
    for subdir, dirs, files in os.walk(dir_):
        for d in dirs:
            if d == "PRODUCTS":
                return os.path.join(subdir, d)

    return None


def hyp3_process(cfg, n):
    try:
        log.info(f'Processing GAMMA InSAR pair "{cfg["sub_name"]}" for "{cfg["username"]}"')
        g1, g2 = earlier_granule_first(cfg['granule'], cfg['other_granules'][0])

        list_file = 'list.csv'
        write_list_file(list_file, g1, g2)

        rlooks, alooks = (10, 2) if extra_arg_is(cfg, 'looks', '10x2') else (20, 4)

        procS1StackGAMMA(
            alooks=alooks,
            rlooks=rlooks,
            csvFile=list_file,
            look_flag=extra_arg_is(cfg, 'include_look', 'yes'),
            los_flag=extra_arg_is(cfg, 'include_los_disp', 'yes'),
            mask=extra_arg_is(cfg, 'water_mask', 'yes'),
        )

        out_name = build_output_name_pair(g1, g2, '.', f'{rlooks}x{alooks}{cfg["suffix"]}')
        log.info(f'Output name: {out_name}')

        product_dir = 'PRODUCTS'
        log.debug(f'Renaming {product_dir} to {out_name}')
        os.rename(product_dir, out_name)

        zip_file = make_archive(base_name=out_name, format='zip', base_dir=out_name)

        browse_img = find_color_phase_png(out_name)
        new_browse_img_name = f'{out_name}.browse.png'
        shutil.copy(browse_img, new_browse_img_name)

        cfg['attachment'] = new_browse_img_name
        cfg['final_product_size'] = [os.stat(zip_file).st_size, ]
        cfg['email_text'] = ' '

        with get_db_connection('hyp3-db') as conn:
            upload_product(zip_file, cfg, conn)
            success(conn, cfg)

    except Exception as e:
        log.exception('Processing failed')
        log.info('Notifying user')
        failure(cfg, str(e))

    cleanup_workdir(cfg)

    log.info('Done')


def main():
    """
    Main entrypoint for hyp3_insar_gamma
    """
    processor = Processor(
        'insar_gamma', hyp3_process, sci_version=hyp3_insar_gamma.__version__
    )
    processor.run()


if __name__ == '__main__':
    main()

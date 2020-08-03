"""
rtc_gamma processing for HyP3
"""
import glob
import logging
import os
import re
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from mimetypes import guess_type
from shutil import make_archive

import boto3
from PIL import Image
from hyp3lib import GranuleError
from hyp3lib.fetch import download_file
from hyp3proclib import (
    extra_arg_is,
    failure,
    get_extra_arg,
    success,
    upload_product,
)
from hyp3proclib.db import get_db_connection
from hyp3proclib.file_system import cleanup_workdir
from hyp3proclib.logger import log
from hyp3proclib.proc_base import Processor
from pkg_resources import load_entry_point

import hyp3_rtc_gamma
from hyp3_rtc_gamma.rtc_sentinel import rtc_sentinel_gamma

# v2 constants
SENTINEL_DISTRIBUTION_URL = 'https://d2jcx4uuy4zbnt.cloudfront.net'
EARTHDATA_LOGIN_DOMAIN = 'urs.earthdata.nasa.gov'
S3_CLIENT = boto3.client('s3')


def entry():
    parser = ArgumentParser(prefix_chars='+', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '++entrypoint', choices=['hyp3_rtc_gamma', 'hyp3_rtc_gamma_v2'], default='hyp3_rtc_gamma',
        help='Select the HyP3 entrypoint version to use'
    )
    args, unknowns = parser.parse_known_args()

    sys.argv = [args.entrypoint, *unknowns]
    sys.exit(
        load_entry_point('hyp3_rtc_gamma', 'console_scripts', args.entrypoint)()
    )


# v2 functions
def write_netrc_file(username, password):
    netrc_file = os.path.join(os.environ['HOME'], '.netrc')
    if os.path.isfile(netrc_file):
        logging.warning(f'Using existing .netrc file: {netrc_file}')
    else:
        with open(netrc_file, 'w') as f:
            f.write(f'machine {EARTHDATA_LOGIN_DOMAIN} login {username} password {password}')


def get_content_type(filename):
    content_type = guess_type(filename)[0]
    if not content_type:
        content_type = 'application/octet-stream'
    return content_type


def upload_file_to_s3(path_to_file, bucket, prefix=''):
    key = os.path.join(prefix, os.path.basename(path_to_file))
    extra_args = {'ContentType': get_content_type(key)}

    logging.info(f'Uploading s3://{bucket}/{key}')
    S3_CLIENT.upload_file(path_to_file, bucket, key, extra_args)


def get_download_url(granule):
    mission = granule[0] + granule[2]
    product_type = granule[7:10]
    if product_type == 'GRD':
        product_type += '_' + granule[10] + granule[14]
    url = f'{SENTINEL_DISTRIBUTION_URL}/{product_type}/{mission}/{granule}.zip'
    return url


def create_thumbnail(input_image, size=(100, 100)):
    filename, ext = os.path.splitext(input_image)
    thumbnail_name = f'{filename}_thumb{ext}'

    output_image = Image.open(input_image)
    output_image.thumbnail(size)
    output_image.save(thumbnail_name)
    return thumbnail_name


def main_v2():
    parser = ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('--resolution', type=float, choices=[10.0, 30.0])
    parser.add_argument('--radiometry', choices=['gamma0', 'sigma0'])
    parser.add_argument('--scale', choices=['power', 'amplitude'])
    parser.add_argument('--speckle-filter', action='store_true')
    parser.add_argument('--dem-matching', action='store_true')
    parser.add_argument('--include-dem', action='store_true')
    parser.add_argument('--include-inc-map', action='store_true')
    parser.add_argument('granule')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    write_netrc_file(args.username, args.password)

    granule_url = get_download_url(args.granule)
    granule_zip_file = download_file(granule_url, chunk_size=5242880)

    output_folder, product_name = rtc_sentinel_gamma(
                                      in_file=granule_zip_file,
                                      res=args.resolution,
                                      match_flag=args.dem_matching,
                                      pwr_flag=(args.scale=='power'),
                                      gamma_flag=(args.radiometry=='gamma0'),
                                      lo_flag=(args.resolution==30.0),
                                      filter_flag=args.speckle_filter,
                                  )

    os.rename(output_folder, product_name)

    if not args.include_dem:
        find_and_remove(product_name, '*_dem.tif*')
    if not args.include_inc_map:
        find_and_remove(product_name, '*_inc_map.tif*')

    output_zip = make_archive(base_name=product_name, format='zip', base_dir=product_name)
    if args.bucket:
        upload_file_to_s3(output_zip, args.bucket, args.bucket_prefix)
        browse_images = glob.glob(f'{product_name}/*.png')
        for browse in browse_images:
            thumbnail = create_thumbnail(browse)
            upload_file_to_s3(browse, args.bucket, args.bucket_prefix + '/browse')
            upload_file_to_s3(thumbnail, args.bucket, args.bucket_prefix + '/thumbnail')
# end v2 functions


def find_png(product_dir):
    pattern = os.path.join(product_dir, '*.png')
    png_files = glob.glob(pattern)

    for png_file in png_files:
        if 'rgb' in png_file:
            return png_file

    if png_files:
        return png_files[0]

    return None


def find_and_remove(directory, file_pattern):
    pattern = os.path.join(directory, file_pattern)
    for filename in glob.glob(pattern):
        logging.info(f'Removing {filename}')
        os.remove(filename)


def process_rtc_gamma(cfg, n):
    try:
        logging.info(f'Processing GAMMA RTC "{cfg["sub_name"]}" for "{cfg["username"]}"')

        granule = cfg['granule']
        if not re.match('S1[AB]_.._[SLC|GRD]', granule):
            raise GranuleError(f'Invalid granule, only S1 SLC and GRD data are supported: {granule}')

        res = get_extra_arg(cfg, 'resolution', '30m')
        if res not in ('10m', '30m'):
            raise ValueError(f'Invalid resolution, valid options are 10m or 30m: {res}')

        granule_url = get_download_url(granule)
        granule_zip_file = download_file(granule_url, chunk_size=5242880)

        args = {
            'in_file': granule_zip_file,
            'res': float(res.rstrip('m')),
            'match_flag': extra_arg_is(cfg, 'matching', 'yes'),
            'pwr_flag': extra_arg_is(cfg, 'power', 'yes'),
            'gamma_flag': extra_arg_is(cfg, 'gamma0', 'yes'),
            'lo_flag': res == '30m',
            'filter_flag': extra_arg_is(cfg, 'filter', 'yes'),
        }
        product_dir, product_name = rtc_sentinel_gamma(**args)

        logging.info(f'Renaming {product_dir} to {product_name}')
        os.rename(product_dir, product_name)
        product_dir = product_name

        if extra_arg_is(cfg, 'include_dem', 'no'):
            find_and_remove(product_dir, '*_dem.tif*')
        if extra_arg_is(cfg, 'include_inc', 'no'):
            find_and_remove(product_dir, '*_inc_map.tif*')

        zip_file = make_archive(base_name=product_dir, format='zip', base_dir=product_dir)
        cfg['final_product_size'] = [os.stat(zip_file).st_size, ]
        cfg['attachment'] = find_png(product_dir)
        cfg['email_text'] = ' '

        with get_db_connection('hyp3-db') as conn:
            upload_product(zip_file, cfg, conn)
            success(conn, cfg)

    except Exception as e:
        logging.exception('Processing failed')
        logging.info('Notifying user')
        failure(cfg, str(e))

    cleanup_workdir(cfg)


def main():
    """
    Main entrypoint for hyp3_rtc_gamma
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    log.propagate = False

    processor = Processor(
        'rtc_gamma', process_rtc_gamma, sci_version=hyp3_rtc_gamma.__version__
    )
    processor.run()


if __name__ == '__main__':
    main()

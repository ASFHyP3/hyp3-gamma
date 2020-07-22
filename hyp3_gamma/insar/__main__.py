"""
insar_gamma processing for HyP3
"""

import os
import shutil
from datetime import datetime

from hyp3lib.metadata import add_esa_citation
from hyp3proclib import (
    build_output_name_pair,
    earlier_granule_first,
    execute,
    extra_arg_is,
    failure,
    find_browses,
    get_extra_arg,
    get_looks,
    process,
    record_metrics,
    success,
    unzip,
    upload_product,
    zip_dir
)
from hyp3proclib.db import get_db_connection
from hyp3proclib.file_system import cleanup_workdir
from hyp3proclib.logger import log
from hyp3proclib.proc_base import Processor

import hyp3_insar_gamma


def find_color_phase_png(dir_):
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith("color_phase_large.png"):
                log.info('Browse image: ' + filepath)
                return filepath

    return None


def download_palsar(cfg, granule):
    full_subdir = cfg['workdir']
    unzipped_dir = os.path.join(full_subdir, granule + '-L1.0')
    zip_file = os.path.join(full_subdir, granule + '-L1.0.zip')

    if not os.path.isdir(full_subdir):
        os.mkdir(full_subdir)
    os.chdir(full_subdir)

    if os.path.isdir(unzipped_dir):
        log.info('Unzipped directory already exists, skipping download')
        return

    log.info('Downloading {0} with get_asf.py'.format(granule))

    execute(cfg, 'get_asf.py --l0 --dir=' + full_subdir + ' ' + granule)

    if not os.path.isfile(zip_file):
        raise Exception('Could not find expected download file: ' + zip_file)
    else:
        log.info('Download complete')
        log.info('Unzipping ' + zip_file)

        unzip(zip_file, full_subdir)
        if not os.path.isdir(unzipped_dir):
            raise Exception(
                'Failed to unzip, unzipped directory not found: ' + unzipped_dir)
        else:
            log.info('Unzip completed.')

    log.info("Ready: " + unzipped_dir)
    return granule + '-L1.0'


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
    cfg['PALSAR'] = False
    try:
        log.info('Processing GAMMA InSAR pair "{0}" for "{1}"'.format(cfg['sub_name'], cfg['username']))
        g1, g2 = earlier_granule_first(
            cfg['granule'], cfg['other_granules'][0])

        if cfg['PALSAR']:
            u1 = download_palsar(cfg, g1)
            u2 = download_palsar(cfg, g2)

            process(cfg, 'processAlosPair', [u1, u2])
            cfg["email_text"] = ""

        else:
            list_file = 'list.csv'
            write_list_file(os.path.join(cfg['workdir'], list_file), g1, g2)

            d1 = g1[17:25]
            d2 = g2[17:25]
            delta = (datetime.strptime(d2, '%Y%m%d') -
                     datetime.strptime(d1, '%Y%m%d')).days

            ifm_dir = d1 + '_' + d2
            cfg['ifm'] = ifm_dir
            log.debug('IFM dir is: ' + ifm_dir)

            sd1 = d1[0:4] + '-' + d1[4:6] + '-' + d1[6:8]
            sd2 = d2[0:4] + '-' + d2[4:6] + '-' + d2[6:8]
            cfg["email_text"] = "This is a {0}-day InSAR pair from {1} to {2}.".format(
                delta, sd1, sd2)

            rlooks = 20
            alooks = 4

            if extra_arg_is(cfg, 'looks', '10x2'):
                rlooks = 10
                alooks = 2

            args = ["--rlooks", str(rlooks), "--alooks",
                    str(alooks), "-f", list_file]

            if get_extra_arg(cfg, 'include_look', 'yes') == 'yes':
                args.extend(["-l"])
            if get_extra_arg(cfg, 'include_los_disp', 'no') == 'yes':
                args.extend(["-s"])
            if get_extra_arg(cfg, 'water_mask', 'no') == 'yes':
                args.extend(["-m"])

            process(cfg, 'procS1StackGAMMA.py', args)

        product = find_product(cfg['workdir'])
        if product is None:
            log.info('PRODUCT directory not found!')
            log.error('Processing failed')
            raise Exception("Processing failed: PRODUCT directory not found")
        else:
            looks = get_looks(product)
            out_name = build_output_name_pair(
                g1, g2, cfg['workdir'], looks + cfg['suffix'])
            log.info('Output name: ' + out_name)

            out_path = os.path.join(cfg['workdir'], out_name)
            zip_file = out_path + '.zip'
            if os.path.isdir(out_path):
                shutil.rmtree(out_path)
            if os.path.isfile(zip_file):
                os.unlink(zip_file)
            cfg['out_path'] = out_path

            log.debug('Renaming ' + product + ' to ' + out_path)
            os.rename(product, out_path)

            add_esa_citation(g1, out_path)
            zip_dir(out_path, zip_file)

            browse_img = find_color_phase_png(out_path)
            new_browse_img_name = out_path + '.browse.png'
            os.rename(browse_img, new_browse_img_name)

            cfg['attachment'] = new_browse_img_name
            cfg['final_product_size'] = [os.stat(zip_file).st_size, ]
            cfg['original_product_size'] = 0

            find_browses(cfg, out_path)

            with get_db_connection('hyp3-db') as conn:
                record_metrics(cfg, conn)
                if 'lag' in cfg and len(str(cfg['lag'])) > 0:
                    cfg['email_text'] += f"\nYou are receiving this product {cfg['lag']} after it was acquired."

                upload_product(zip_file, cfg, conn,
                               browse_path=new_browse_img_name)
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

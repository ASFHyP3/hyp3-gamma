"""
geocode processing for HyP3
"""

import os
import shutil
from datetime import datetime

from hyp3proclib import (
    add_browse,
    build_output_name,
    clip_tiffs_to_roi,
    execute,
    extra_arg_is,
    failure,
    find_browses,
    get_extra_arg,
    process,
    record_metrics,
    success,
    unzip,
    upload_product,
    zip_dir
)
from hyp3proclib.db import get_db_connection
from hyp3proclib.file_system import add_citation, cleanup_workdir
from hyp3proclib.logger import log
from hyp3proclib.proc_base import Processor

import hyp3_geocode


def find_png(dir_):
    # First try to find RGB
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".png") and 'rgb' in filepath and 'large' not in filepath:
                log.info('Browse image: ' + filepath)
                return filepath

    # No RGB, see if we can find a grescale browse
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".png") and 'large' not in filepath:
                log.info('Browse image: ' + filepath)
                return filepath

    return None


def find_zip(dir_):
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".zip") and ('GRD' in file or 'SLC' in file or 'L0' in file):
                log.info('Found zip: ' + filepath)
                return filepath

    return None


def find_raw(dir_):
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".raw") and 'L0' in file:
                log.info('Found L0 data file: ' + filepath)
                return filepath

    return None


def find_and_remove(dir_, s):
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if s in file:
                log.info('Removing from PRODUCT dir: ' + filepath)
                os.remove(filepath)


def find_product(dir_):
    for subdir, dirs, files in os.walk(dir_):
        for d in dirs:
            if d == "PRODUCT":
                return os.path.join(subdir, d)

    return None


def download(cfg, granule):
    if granule.startswith('S1'):
        if 'GRD' in granule:
            typ = "GRD"
        elif 'SLC' in granule:
            typ = "SLC"
        else:
            raise Exception("Unsupported Sentinel-1: " + granule)
    else:
        typ = "l0"

    log.info('Downloading {granule} with get_asf.py'.format(granule=granule))
    execute(cfg, "get_asf.py --{typ} --dir={dir} {granule}".format(typ=typ, dir=cfg['workdir'], granule=granule))

    if 'GRD' in granule or 'SLC' in granule:
        zip_file = os.path.join(cfg['workdir'], granule + '.zip')
    else:
        zip_file = find_zip(cfg['workdir'])
        if zip_file:
            granule = os.path.splitext(os.path.basename(zip_file))[0]
        else:
            log.info('Nothing found for {granule}'.format(granule=granule))
            return granule

    if not os.path.isfile(zip_file):
        raise Exception('Could not find expected download file: ' + zip_file)
    else:
        log.info('Download complete')
        log.info('Unzipping ' + zip_file)

        unzip(zip_file, cfg['workdir'])

        if granule.startswith('S1'):
            safe_file = os.path.join(cfg['workdir'], '{granule}.SAFE'.format(granule=granule))
            if not os.path.isdir(safe_file):
                raise Exception('Failed to unzip, SAFE directory not found: {safe_file}'.format(safe_file=safe_file))

    log.info('Unzip completed.')

    return granule


def process_geocode_gamma(cfg, n):
    try:
        log.info('Processing GAMMA Geocode "{}" for "{}"'.format(cfg["sub_name"], cfg["username"]))

        in_granule = cfg['granule']

        cfg['log'] = "Processing started at {}\n\n".format(datetime.now())
        g = download(cfg, in_granule)

        if in_granule.startswith('S1'):

            if 'RAW' in g:
                raise Exception('Sentinel RAW data is not supported: ' + in_granule)
            d = g[17:25]
            sd = d[0:4]+'-'+d[4:6]+'-'+d[6:8]
            cfg["email_text"] = "This is an RTC product from {sd}.".format(sd=sd)

            hi_res = extra_arg_is(cfg, 'resolution', '10m')
            if hi_res:
                args = ['-s', '10']
                opts_str = '-10m'
            else:
                args = ['-s', '30']
                opts_str = '-30m'

            args += ['-p', '30']

            height = get_extra_arg(cfg, 'height', '0')
            args += ['-t', height]

            out_name = build_output_name(g, cfg['workdir'], opts_str + cfg['suffix'])
            log.info('Output name: {out_name}'.format(out_name=out_name))

            args += [g + '.SAFE', out_name]

            process(cfg, 'geocode_sentinel.py', args)

        else:
            raise Exception('Unrecognized: '+in_granule)

        product = find_product(cfg['workdir'])
        if not os.path.isdir(product):
            log.info('PRODUCT directory not found: {product}'.format(product=product))
            log.error('Processing failed')
            raise Exception("Processing failed: PRODUCT directory not found")
        else:

            out_path = os.path.join(cfg['workdir'], out_name)
            log.info('Output path: ' + out_path)

            zip_file = out_path + '.zip'
            if os.path.isdir(out_path):
                shutil.rmtree(out_path)
            if os.path.isfile(zip_file):
                os.unlink(zip_file)
            cfg['out_path'] = out_path

            with get_db_connection('hyp3-db') as conn:
                clip_tiffs_to_roi(cfg, conn, product)

                log.debug('Renaming '+product+' to '+out_path)
                os.rename(product, out_path)

                browse_path = find_png(out_path)
                cfg['attachment'] = browse_path
                add_browse(cfg, 'LOW-RES', browse_path)

                find_browses(cfg, out_path)
                add_citation(cfg, out_path)
                zip_dir(out_path, zip_file)

                cfg['final_product_size'] = [os.stat(zip_file).st_size, ]
                cfg['original_product_size'] = 0

                record_metrics(cfg, conn)
                if 'lag' in cfg and 'email_text' in cfg:
                    cfg['email_text'] += "\nYou are receiving this product {} after it was acquired.".format(cfg['lag'])

                upload_product(zip_file, cfg, conn, browse_path=browse_path)
                success(conn, cfg)

    except Exception as e:
        log.exception('Processing failed')
        log.info('Notifying user')

        failure(cfg, str(e))

    cleanup_workdir(cfg)

    log.info('Done')


def main():
    """
    Main entrypoint for hyp3_geocode
    """
    processor = Processor(
        'geocode_gamma', process_geocode_gamma, sleep_time=3, sci_version=hyp3_geocode.__version__
    )
    processor.run()


if __name__ == '__main__':
    main()

"""
rtc_gamma processing for HyP3
"""

import os
import shutil
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from datetime import datetime
from glob import iglob
from mimetypes import guess_type

import boto3
import requests
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
    user_ok_for_jers,
    zip_dir,
)
from hyp3proclib.db import get_db_connection
from hyp3proclib.file_system import cleanup_workdir
from hyp3proclib.logger import log
from hyp3proclib.proc_base import Processor
from pkg_resources import load_entry_point

import hyp3_rtc_gamma
from hyp3_rtc_gamma.rtc_sentinel import rtc_sentinel_gamma

# v2 constants
CHUNK_SIZE = 5242880
DATAPOOL_URL = 'https://datapool.asf.alaska.edu'
EARTHDATA_LOGIN_DOMAIN = 'urs.earthdata.nasa.gov'


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
        print(f'WARNING - using existing .netrc file: {netrc_file}')
    else:
        with open(netrc_file, 'w') as f:
            f.write(f'machine {EARTHDATA_LOGIN_DOMAIN} login {username} password {password}')


def get_content_type(filename):
    content_type = guess_type(filename)[0]
    if not content_type:
        content_type = 'application/octet-stream'
    return content_type


def upload_folder_to_s3(folder, bucket, prefix=''):
    s3 = boto3.client('s3')
    for filename in iglob(f'{folder}/**'):
        if os.path.isfile(filename):
            key = os.path.join(prefix, filename)
            extra_args = {'ContentType': get_content_type(filename)}
            s3.upload_file(filename, bucket, key, extra_args)


def get_download_url(granule):
    mission = granule[0] + granule[2]
    product_type = granule[7:10]
    if product_type == 'GRD':
        product_type += '_' + granule[10] + granule[14]
    url = f'{DATAPOOL_URL}/{product_type}/{mission}/{granule}.zip'
    return url


def download_file(url):
    print(f"\nDownloading {url}")
    local_filename = url.split("/")[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    return local_filename


def main_v2():
    parser = ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('granule')
    args = parser.parse_args()

    write_netrc_file(args.username, args.password)

    # download granule from datapool
    # via get_asf.py
    granule_url = get_download_url(args.granule)
    granule_zip_file = download_file(granule_url)

    # unzip granule (skip this and let rtc_sentinel.py do the unzip)

    output_folder = rtc_sentinel_gamma(granule_zip_file)

    # write esa citation file (have rtc_sentinel call new hyp3_lib function,
    # or just get rid of separate citation file)

    # write argis-compatable xml metadata file(s) (move to rtc_sentinel)

    # something with browse images? (move to rtc_sentinel)

    # clip_tiffs_to_roi? (move to rtc_sentinel)

    # decide final product name? (move to rtc sentinel?)

    # zip output folder? (skip for now?)

    if args.bucket:
        upload_folder_to_s3(output_folder, args.bucket, args.bucket_prefix)

# end v2 functions


def find_png(dir_):
    # First try to find RGB
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".png") and 'rgb' in filepath and 'large' not in filepath:
                log.info('Browse image: ' + filepath)
                return filepath

    # No RGB, see if we can find a grayscale browse
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".png") and 'large' not in filepath:
                log.info('Browse image: ' + filepath)
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


def find_zip(dir_):
    for subdir, dirs, files in os.walk(dir_):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith(".zip") and ('GRD' in file or 'SLC' in file or 'L0' in file):
                log.info('Found zip: ' + filepath)
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
            raise Exception("Unsupported Sentinel-1: "+granule)
    else:
        typ = "l0"

    log.info('Downloading {0} with get_asf.py'.format(granule))
    execute(cfg, "get_asf.py --{0} --dir={1} {2}".format(typ, cfg['workdir'], granule))

    if 'GRD' in granule or 'SLC' in granule:
        zip_file = os.path.join(cfg['workdir'], granule+'.zip')
    else:
        zip_file = find_zip(cfg['workdir'])
        if zip_file:
            granule = os.path.splitext(os.path.basename(zip_file))[0]
        else:
            log.info('Nothing found for {0}'.format(granule))
            return granule

    if not os.path.isfile(zip_file):
        raise Exception('Could not find expected download file: ' + zip_file)
    else:
        log.info('Download complete')
        log.info('Unzipping ' + zip_file)

        unzip(zip_file, cfg['workdir'])

        if granule.startswith('S1'):
            safe_file = os.path.join(cfg['workdir'], granule+'.SAFE')
            if not os.path.isdir(safe_file):
                raise Exception('Failed to unzip, SAFE directory not found: ' + safe_file)

    log.info('Unzip completed.')

    return granule


def process_rtc_gamma(cfg, n):
    try:
        log.info('Processing GAMMA RTC "{0}" for "{1}"'.format(cfg['sub_name'], cfg['username']))

        in_granule = cfg['granule']

        cfg['log'] = "Processing started at " + str(datetime.now()) + "\n\n"
        g = download(cfg, in_granule)

        if in_granule.startswith('S1'):

            if 'RAW' in g:
                raise Exception('Sentinel RAW data is not supported: ' + in_granule)
            d = g[17:25]
            sd = d[0:4] + '-' + d[4:6] + '-' + d[6:8]
            cfg["email_text"] = "This is an RTC product from {0}.".format(sd)

            res = get_extra_arg(cfg, 'resolution', cfg['default_rtc_resolution'])
            opts_str = f'_{res}'

            if res not in ('10m', '30m'):
                raise Exception('Invalid resolution: ' + res)

            if res == '30m':
                args = ['-l']
            else:
                args = []

            if extra_arg_is(cfg, 'matching', 'no'):
                opts_str += '_nomatch'
                args += ['-n']
            else:
                opts_str += '_match'

            if extra_arg_is(cfg, 'power', 'no') or extra_arg_is(cfg, 'keep_area', 'yes'):
                opts_str += '_amp'
                args += ['--amp']
            else:
                opts_str += '_power'

            if extra_arg_is(cfg, 'gamma0', 'no') or extra_arg_is(cfg, 'keep_area', 'yes'):
                opts_str += '_sigma0'
                args += ['--sigma']
            else:
                opts_str += '_gamma0'

            if extra_arg_is(cfg, 'filter', 'yes'):
                args += ['-f']
                opts_str += '_filt'

            if extra_arg_is(cfg, 'keep_area', 'yes'):
                args += ['-n']
                opts_str += '_flat'

            if res == '10m':
                args += ['-o', '10']
            else:
                default_looks = 6
                if 'SLC' in in_granule:
                    default_looks = 3
                looks = get_extra_arg(cfg, 'looks', str(default_looks))
                args += ['-k', looks]

            safe_dir = g + '.SAFE'
            args += [safe_dir, ]

            process(cfg, 'rtc_sentinel.py', args)

        elif in_granule.startswith('E1') \
                or in_granule.startswith('E2') \
                or in_granule.startswith('R1') or in_granule.startswith('J1'):

            if in_granule.startswith('J1') and not user_ok_for_jers(cfg, cfg['user_id']):
                raise Exception('User does not have permission to process JERS data: ' + in_granule)

            log.info('Legacy granule: ' + g)
            raw = find_raw(cfg['workdir'])
            d = os.path.dirname(raw)

            log.info('Changing to directory ' + d)
            os.chdir(d)

            opts_str = '-12.5m'
            args = ["-g", "-d", os.path.basename(raw)]

            process(cfg, 'rtc_legacy.py', args)

        else:
            raise Exception('Unrecognized: ' + in_granule)

        product = find_product(cfg['workdir'])
        if not os.path.isdir(product):
            log.info('PRODUCT directory not found: ' + product)
            log.error('Processing failed')
            raise Exception("Processing failed: PRODUCT directory not found")
        else:
            if extra_arg_is(cfg, "include_dem", "no"):
                find_and_remove(product, '_dem.tif')
            if extra_arg_is(cfg, "include_inc", "no"):
                find_and_remove(product, '_inc_map.tif')

            out_name = build_output_name(g, cfg['workdir'], opts_str + cfg['suffix'])
            if "STD_L0_F" in out_name:
                out_name = out_name.replace("_L0", "")
            log.info('Output name: ' + out_name)

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

                log.debug('Renaming ' + product + ' to ' + out_path)
                os.rename(product, out_path)

                browse_path = find_png(out_path)
                cfg['attachment'] = browse_path
                add_browse(cfg, 'LOW-RES', browse_path)

                find_browses(cfg, out_path)
                zip_dir(out_path, zip_file)

                cfg['final_product_size'] = [os.stat(zip_file).st_size, ]
                cfg['original_product_size'] = 0

                record_metrics(cfg, conn)
                if 'lag' in cfg and 'email_text' in cfg:
                    cfg['email_text'] += "\n" + "You are receiving this product {0} after it was acquired.".format(
                        cfg['lag'])

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
    Main entrypoint for hyp3_rtc_gamma
    """
    processor = Processor(
        'rtc_gamma', process_rtc_gamma, sci_version=hyp3_rtc_gamma.__version__
    )
    processor.run()


if __name__ == '__main__':
    main()

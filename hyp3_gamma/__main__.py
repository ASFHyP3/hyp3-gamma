"""
HyP3 plugin for processing SAR data with GAMMA
"""
import glob
import logging
import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path
from shutil import make_archive

from hyp3lib.aws import upload_file_to_s3
from hyp3lib.fetch import download_file, write_credentials_to_netrc_file
from hyp3lib.image import create_thumbnail
from hyp3lib.scene import get_download_url
from hyp3lib.util import string_is_true
from pkg_resources import load_entry_point

from hyp3_gamma import __version__
from hyp3_gamma.rtc.rtc_sentinel import rtc_sentinel_gamma

log = logging.getLogger(__name__)


def entry():
    parser = ArgumentParser(prefix_chars='+', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('++version', action='version', version=f'hyp3_gamma {__version__}')
    parser.add_argument(
        'process', choices=['rtc'],
        help='Select the HyP3 process to use'
    )
    args, unknowns = parser.parse_known_args()

    sys.argv = [args.process, *unknowns]
    sys.exit(
        load_entry_point('hyp3_gamma', 'console_scripts', args.process)()
    )


def rtc():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', action='version', version=f'hyp3_gamma {__version__}')
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('--resolution', type=float, choices=[10.0, 30.0], default=30.0)
    parser.add_argument('--radiometry', choices=['gamma0', 'sigma0'], default='gamma0')
    parser.add_argument('--scale', choices=['power', 'amplitude'], default='power')
    parser.add_argument('--speckle-filter', type=string_is_true, default=False)
    parser.add_argument('--dem-matching', type=string_is_true, default=False)
    parser.add_argument('--include-dem', type=string_is_true, default=False)
    parser.add_argument('--include-inc-map', type=string_is_true, default=False)
    parser.add_argument('granule')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    write_credentials_to_netrc_file(args.username, args.password)

    granule_url = get_download_url(args.granule)
    granule_zip_file = download_file(granule_url, chunk_size=5242880)

    product_name = rtc_sentinel_gamma(
                        in_file=granule_zip_file,
                        res=args.resolution,
                        match_flag=args.dem_matching,
                        pwr_flag=(args.scale == 'power'),
                        gamma_flag=(args.radiometry == 'gamma0'),
                        filter_flag=args.speckle_filter,
                    )

    if not args.include_dem:
        find_and_remove(product_name, '*_dem.tif*')
    if not args.include_inc_map:
        find_and_remove(product_name, '*_inc_map.tif*')

    output_zip = make_archive(base_name=product_name, format='zip', base_dir=product_name)
    if args.bucket:
        upload_file_to_s3(Path(output_zip), args.bucket, args.bucket_prefix)
        browse_images = Path(product_name).glob('*.png')
        for browse in browse_images:
            thumbnail = create_thumbnail(browse)
            upload_file_to_s3(browse, args.bucket, args.bucket_prefix)
            upload_file_to_s3(thumbnail, args.bucket, args.bucket_prefix)


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


def main():
    """
    Main entrypoint for hyp3_gamma
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    log.propagate = False

    entry()


if __name__ == '__main__':
    main()

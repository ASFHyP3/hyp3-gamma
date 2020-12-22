"""
rtc_gamma processing for HyP3
"""
import logging
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path
from shutil import make_archive

from hyp3lib.aws import upload_file_to_s3
from hyp3lib.fetch import write_credentials_to_netrc_file
from hyp3lib.image import create_thumbnail
from hyp3lib.util import string_is_true
from pkg_resources import load_entry_point

from hyp3_gamma import util
from hyp3_gamma.insar.ifm_sentinel import insar_sentinel_gamma
from hyp3_gamma.rtc.rtc_sentinel import rtc_sentinel_gamma


def main():
    parser = ArgumentParser(prefix_chars='+', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '++process', choices=['rtc', 'insar'], default='rtc',
        help='Select the HyP3 entrypoint version to use'
    )
    args, unknowns = parser.parse_known_args()

    sys.argv = [args.process, *unknowns]
    sys.exit(
        load_entry_point('hyp3_gamma', 'console_scripts', args.process)()
    )


def rtc():
    parser = ArgumentParser()
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
    parser.add_argument('--include-scattering-area', type=string_is_true, default=False)
    parser.add_argument('granule')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    write_credentials_to_netrc_file(args.username, args.password)

    safe_dir = util.get_granule(args.granule)

    product_name = rtc_sentinel_gamma(
                        safe_dir=safe_dir,
                        resolution=args.resolution,
                        dem_matching=args.dem_matching,
                        power=(args.scale == 'power'),
                        gamma0=(args.radiometry == 'gamma0'),
                        speckle_filter=args.speckle_filter,
                        include_dem=args.include_dem,
                        include_inc_map=args.include_inc_map,
                        include_scattering_area=args.include_scattering_area,
                    )

    output_zip = make_archive(base_name=product_name, format='zip', base_dir=product_name)
    if args.bucket:
        upload_file_to_s3(Path(output_zip), args.bucket, args.bucket_prefix)
        browse_images = Path(product_name).glob('*.png')
        for browse in browse_images:
            thumbnail = create_thumbnail(browse)
            upload_file_to_s3(browse, args.bucket, args.bucket_prefix)
            upload_file_to_s3(thumbnail, args.bucket, args.bucket_prefix)


def insar():
    parser = ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('--include-look-vectors', type=string_is_true, default=False)
    parser.add_argument('--include-los-displacement', type=string_is_true, default=False)
    parser.add_argument('--looks', choices=['20x4', '10x2'], default='20x4')
    parser.add_argument('granules', type=str.split, nargs='+')
    args = parser.parse_args()

    args.granules = [item for sublist in args.granules for item in sublist]
    if len(args.granules) != 2:
        parser.error('Must provide exactly two granules')

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    write_credentials_to_netrc_file(args.username, args.password)

    g1, g2 = util.earlier_granule_first(args.granules[0], args.granules[1])
    reference_granule = util.get_granule(g1)
    secondary_granule = util.get_granule(g2)

    rlooks, alooks = (20, 4) if args.looks == '20x4' else (10, 2)

    product_name = insar_sentinel_gamma(
        reference_file=reference_granule,
        secondary_file=secondary_granule,
        alooks=alooks,
        rlooks=rlooks,
        look_flag=args.include_look_vectors,
        los_flag=args.include_los_displacement,
    )

    output_zip = make_archive(base_name=product_name, format='zip', base_dir=product_name)

    if args.bucket:
        upload_file_to_s3(Path(output_zip), args.bucket, args.bucket_prefix)
        browse_images = Path(product_name).glob('*.png')
        for browse in browse_images:
            thumbnail = create_thumbnail(browse)
            upload_file_to_s3(browse, args.bucket, args.bucket_prefix)
            upload_file_to_s3(thumbnail, args.bucket, args.bucket_prefix)


if __name__ == '__main__':
    main()

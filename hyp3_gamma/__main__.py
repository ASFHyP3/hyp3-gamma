"""
rtc_gamma processing for HyP3
"""
import logging
import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from importlib.metadata import entry_points
from pathlib import Path
from shutil import make_archive

from hyp3lib.aws import upload_file_to_s3
from hyp3lib.execute import execute
from hyp3lib.fetch import write_credentials_to_netrc_file
from hyp3lib.image import create_thumbnail
from hyp3lib.util import string_is_true

from hyp3_gamma import util
from hyp3_gamma.insar.ifm_sentinel import insar_sentinel_gamma
from hyp3_gamma.rtc.rtc_sentinel import rtc_sentinel_gamma


def main():
    parser = ArgumentParser(prefix_chars='+', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '++process', choices=['rtc', 'insar', 'water_map'], default='rtc',
        help='Select the HyP3 entrypoint version to use'
    )
    parser.add_argument('++omp-num-threads', type=int, help='The number of OpenMP threads to use for parallel regions')
    args, unknowns = parser.parse_known_args()
    (process_entry_point,) = entry_points(group='console_scripts', name=args.process)

    if args.omp_num_threads:
        os.environ['OMP_NUM_THREADS'] = str(args.omp_num_threads)

    sys.argv = [args.process, *unknowns]
    sys.exit(
        process_entry_point.load()()
    )


def check_earthdata_credentials(username, password):
    if username is None:
        username = os.getenv('EARTHDATA_USERNAME')
        if username is None:
            raise ValueError(
                'Please provide Earthdata username via the --username option '
                'or the EARTHDATA_USERNAME environment variable.'
            )

    if password is None:
        password = os.getenv('EARTHDATA_PASSWORD')
        if password is None:
            raise ValueError(
                'Please provide Earthdata password via the --password option '
                'or the EARTHDATA_PASSWORD environment variable.'
            )

    return username, password


def rtc():
    parser = ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('--resolution', type=float, choices=[10.0, 30.0], default=30.0)
    parser.add_argument('--radiometry', choices=['gamma0', 'sigma0'], default='gamma0')
    parser.add_argument('--scale', choices=['power', 'decibel', 'amplitude'], default='power')
    parser.add_argument('--speckle-filter', type=string_is_true, default=False)
    parser.add_argument('--dem-matching', type=string_is_true, default=False)
    parser.add_argument('--include-dem', type=string_is_true, default=False)
    parser.add_argument('--include-inc-map', type=string_is_true, default=False)
    parser.add_argument('--include-scattering-area', type=string_is_true, default=False)
    parser.add_argument('--include-rgb', type=string_is_true, default=False)
    parser.add_argument('--dem-name', choices=['copernicus', 'legacy'], default='copernicus')
    parser.add_argument('granule')
    args = parser.parse_args()

    username, password = check_earthdata_credentials(args.username, args.password)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    write_credentials_to_netrc_file(username, password)

    safe_dir = util.get_granule(args.granule)

    product_name = rtc_sentinel_gamma(
        safe_dir=safe_dir,
        resolution=args.resolution,
        scale=args.scale,
        radiometry=args.radiometry,
        speckle_filter=args.speckle_filter,
        dem_matching=args.dem_matching,
        include_dem=args.include_dem,
        include_inc_map=args.include_inc_map,
        include_scattering_area=args.include_scattering_area,
        include_rgb=args.include_rgb,
        dem_name=args.dem_name,
    )
    output_zip = make_archive(base_name=product_name, format='zip', base_dir=product_name)

    if args.bucket:
        product_dir = Path(product_name)
        for browse in product_dir.glob('*.png'):
            create_thumbnail(browse, output_dir=product_dir)

        upload_file_to_s3(Path(output_zip), args.bucket, args.bucket_prefix)

        for product_file in product_dir.iterdir():
            upload_file_to_s3(product_file, args.bucket, args.bucket_prefix)


def insar():
    parser = ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('--include-dem', type=string_is_true, default=False)
    parser.add_argument('--include-look-vectors', type=string_is_true, default=False)
    parser.add_argument('--include-los-displacement', type=string_is_true, default=False)
    parser.add_argument('--include-displacement-maps', type=string_is_true, default=False)
    parser.add_argument('--include-wrapped-phase', type=string_is_true, default=False)
    parser.add_argument('--include-inc-map', type=string_is_true, default=False)
    parser.add_argument('--apply-water-mask', type=string_is_true, default=False)
    parser.add_argument('--looks', choices=['20x4', '10x2'], default='20x4')
    parser.add_argument('granules', type=str.split, nargs='+')
    args = parser.parse_args()

    username, password = check_earthdata_credentials(args.username, args.password)

    # TODO: Remove `--include-los-displacement` and this logic once it's no longer supported by the HyP3 API
    args.include_displacement_maps = args.include_displacement_maps | args.include_los_displacement

    args.granules = [item for sublist in args.granules for item in sublist]
    if len(args.granules) != 2:
        parser.error('Must provide exactly two granules')

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    write_credentials_to_netrc_file(username, password)

    g1, g2 = util.earlier_granule_first(args.granules[0], args.granules[1])
    reference_granule = util.get_granule(g1)
    secondary_granule = util.get_granule(g2)

    rlooks, alooks = (20, 4) if args.looks == '20x4' else (10, 2)

    product_name = insar_sentinel_gamma(
        reference_file=reference_granule,
        secondary_file=secondary_granule,
        alooks=alooks,
        rlooks=rlooks,
        include_dem=args.include_dem,
        include_look_vectors=args.include_look_vectors,
        include_displacement_maps=args.include_displacement_maps,
        include_wrapped_phase=args.include_wrapped_phase,
        include_inc_map=args.include_inc_map,
        apply_water_mask=args.apply_water_mask,
    )

    output_zip = make_archive(base_name=product_name, format='zip', base_dir=product_name)

    if args.bucket:
        product_dir = Path(product_name)
        for browse in product_dir.glob('*.png'):
            create_thumbnail(browse, output_dir=product_dir)

        upload_file_to_s3(Path(output_zip), args.bucket, args.bucket_prefix)

        for product_file in product_dir.iterdir():
            upload_file_to_s3(product_file, args.bucket, args.bucket_prefix)


def water_map():
    parser = ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')

    parser.add_argument('--resolution', type=float, choices=[10.0, 30.0], default=30.0)
    parser.add_argument('--speckle-filter', type=string_is_true, default=False)
    parser.add_argument('--max-vv-threshold', type=float, default=-17.)
    parser.add_argument('--max-vh-threshold', type=float, default=-24.)
    parser.add_argument('--hand-threshold', type=float, default=15.)
    parser.add_argument('--hand-fraction', type=float, default=0.8)
    parser.add_argument('--membership-threshold', type=float, default=0.45)
    parser.add_argument('granule')

    parser.add_argument('--include-flood-depth', type=string_is_true, default=False)
    parser.add_argument('--estimator', type=str, default='iterative', choices=['iterative', 'logstat', 'nmad', 'numpy'])
    parser.add_argument('--water-level-sigma', type=float, default=3.)
    parser.add_argument('--known-water-threshold', type=float, default=30.)
    parser.add_argument('--iterative-min', type=int, default=0)
    parser.add_argument('--iterative-max', type=int, default=15)

    args = parser.parse_args()

    username, password = check_earthdata_credentials(args.username, args.password)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    write_credentials_to_netrc_file(username, password)

    safe_dir = util.get_granule(args.granule)

    product_name = rtc_sentinel_gamma(
        safe_dir=safe_dir,
        resolution=args.resolution,
        scale='power',
        radiometry='gamma0',
        speckle_filter=args.speckle_filter,
        dem_matching=False,
        include_dem=True,
        include_inc_map=False,
        include_scattering_area=False,
        include_rgb=True,
        dem_name='copernicus',
    )
    execute(f'conda run -n  asf-tools water_map {product_name}/{product_name}_WM.tif '
            f'{product_name}/{product_name}_VV.tif {product_name}/{product_name}_VH.tif '
            f'--max-vv-threshold {args.max_vv_threshold} --max-vh-threshold {args.max_vh_threshold} '
            f'--hand-threshold {args.hand_threshold} --hand-fraction {args.hand_fraction} '
            f'--membership-threshold {args.membership_threshold}', uselogging=True)

    files_to_remove = [
        Path(product_name) / f'{product_name}_WM_VV_initial.tif',
        Path(product_name) / f'{product_name}_WM_VH_initial.tif',
        Path(product_name) / f'{product_name}_WM_VV_fuzzy.tif',
        Path(product_name) / f'{product_name}_WM_VH_fuzzy.tif',
    ]
    for file_to_remove in files_to_remove:
        file_to_remove.unlink()

    if args.include_flood_depth:
        execute(f'conda run -n  asf-tools flood_map {product_name}/{product_name}_FM.tif '
                f'{product_name}/{product_name}_VV.tif {product_name}/{product_name}_WM.tif '
                f'{product_name}/{product_name}_WM_HAND.tif --estimator {args.estimator} '
                f'--water-level-sigma {args.water_level_sigma} --known-water-threshold {args.known_water_threshold} '
                f'--iterative-bounds {args.iterative_min} {args.iterative_max}',
                uselogging=True)

    output_zip = make_archive(base_name=product_name, format='zip', base_dir=product_name)

    if args.bucket:
        product_dir = Path(product_name)
        for browse in product_dir.glob('*.png'):
            create_thumbnail(browse, output_dir=product_dir)

        upload_file_to_s3(Path(output_zip), args.bucket, args.bucket_prefix)

        for product_file in product_dir.iterdir():
            upload_file_to_s3(product_file, args.bucket, args.bucket_prefix)


if __name__ == '__main__':
    main()

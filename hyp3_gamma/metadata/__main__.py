import argparse
from pathlib import Path

from dateutil.parser import parse as dt_parse

from hyp3_metadata import __version__, create_metadata_file_set_rtc
from hyp3_metadata.util import SUPPORTED_DEMS, populate_example_data


def main():
    """Generate an example set of metadata files for HyP3 products"""
    parser = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('-o', '--output-dir', default='.', type=Path,
                        help='Generate the example products in this directory')

    parser.add_argument('--product-name', default='S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2',
                        help='RTC product name')
    parser.add_argument('--granule-name',
                        default='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
                        help='Source granule used to generate the RTC product')
    parser.add_argument('--dem-name', default='GLO-30', choices=SUPPORTED_DEMS,
                        help='DEM used to generate the RTC product')
    parser.add_argument('--processing-date', default='2020-01-01T00:00:00+00:00', type=dt_parse)
    parser.add_argument('--looks', default=1, type=int,
                        help='Number of azimuth looks taken when generating the RTC product')

    args = parser.parse_args()

    product_dir = args.output_dir / args.product_name
    product_dir.mkdir(parents=True, exist_ok=True)

    populate_example_data(product_dir)

    create_metadata_file_set_rtc(
        product_dir=product_dir,
        granule_name=args.granule_name,
        dem_name=args.dem_name,
        processing_date=args.processing_date,
        looks=args.looks,
        plugin_name='hyp3_gamma',
        plugin_version='X.Y.Z',
        processor_name='GAMMA',
        processor_version='YYYYMMDD',
    )


if __name__ == '__main__':
    main()

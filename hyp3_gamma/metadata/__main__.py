import argparse
from pathlib import Path

from dateutil.parser import parse as dt_parse

from hyp3_metadata import __version__, create, insar, rtc


def main():
    """Generate an example set of metadata files for HyP3 products"""
    parser = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    # RTC Argruments
    rtc_parser = subparsers.add_parser('rtc')
    rtc_parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    rtc_parser.add_argument('-o', '--output-dir', default='.', type=Path,
                            help='Generate the example products in this directory')

    rtc_parser.add_argument('--product-name', default='S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2',
                            help='RTC product name')
    rtc_parser.add_argument('--granule-name',
                            default='S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8',
                            help='Source granule used to generate the RTC product')
    rtc_parser.add_argument('--dem-name', default='GLO-30', choices=rtc.SUPPORTED_DEMS,
                            help='DEM used to generate the RTC product')
    rtc_parser.add_argument('--processing-date', default='2020-01-01T00:00:00+00:00', type=dt_parse)
    rtc_parser.add_argument('--looks', default=1, type=int,
                            help='Number of azimuth looks taken when generating the RTC product')
    rtc_parser.set_defaults(func=rtc_metadata)

    # INSAR Arguments
    insar_parser = subparsers.add_parser('insar')
    insar_parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    insar_parser.add_argument('-o', '--output-dir', default='.', type=Path,
                              help='Generate the example products in this directory')

    insar_parser.add_argument('--product-name', default='S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1',
                              help='INSAR product name')
    insar_parser.add_argument('--reference-granule-name',
                              default='S1B_IW_SLC__1SSH_20210430T125122_20210430T125149_026696_033052_6408',
                              help='Reference granule used to generate the INSAR product')
    insar_parser.add_argument('--secondary-granule-name',
                              default='S1A_IW_SLC__1SSH_20210424T125204_20210424T125231_037592_046F17_3392',
                              help='Secondary granule used to generate the INSAR product')
    insar_parser.add_argument('--processing-date', default='2020-01-01T00:00:00+00:00', type=dt_parse)
    insar_parser.add_argument('--looks', default='20x4', type=str,
                              help='Number of azimuth looks taken when generating the RTC product')
    insar_parser.set_defaults(func=insar_metadata)

    args = parser.parse_args()
    args.func(args)


def rtc_metadata(args):
    product_dir = args.output_dir / args.product_name
    product_dir.mkdir(parents=True, exist_ok=True)

    rtc.populate_example_data(product_dir)

    create.create_metadata_file_set_rtc(
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


def insar_metadata(args):
    product_dir = args.output_dir / args.product_name
    product_dir.mkdir(parents=True, exist_ok=True)

    insar.populate_example_data(product_dir)

    create.create_metadata_file_set_insar(
        product_dir=product_dir,
        reference_granule_name=args.reference_granule_name,
        secondary_granule_name=args.secondary_granule_name,
        processing_date=args.processing_date,
        looks=args.looks,
        dem_name='GLO-30',
        plugin_name='hyp3_gamma',
        plugin_version='X.Y.Z',
        processor_name='GAMMA',
        processor_version='YYYYMMDD')


if __name__ == '__main__':
    main()

"""insar_gamma processing for HyP3"""

import logging
import os
from argparse import ArgumentParser
from pathlib import Path
from shutil import make_archive
from zipfile import ZipFile

from hyp3lib.aws import upload_file_to_s3
from hyp3lib.fetch import download_file, write_credentials_to_netrc_file
from hyp3lib.image import create_thumbnail
from hyp3lib.scene import get_download_url
from hyp3lib.util import string_is_true

from hyp3_insar_gamma.ifm_sentinel import gamma_process

log = logging.getLogger(__name__)


def get_granule(granule):
    download_url = get_download_url(granule)
    zip_file = download_file(download_url)
    log.info(f'Unzipping {zip_file}')
    with ZipFile(zip_file) as z:
        z.extractall()
    os.remove(zip_file)
    return f'{granule}.SAFE'


def earlier_granule_first(g1, g2):
    if g1[17:32] <= g2[17:32]:
        return g1, g2
    return g2, g1


def main():
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

    g1, g2 = earlier_granule_first(args.granules[0], args.granules[1])
    reference_granule = get_granule(g1)
    secondary_granule = get_granule(g2)

    rlooks, alooks = (20, 4) if args.looks == '20x4' else (10, 2)

    product_name = gamma_process(
        reference_file=reference_granule,
        secondary_file=secondary_granule,
        alooks=alooks,
        rlooks=rlooks,
        look_flag=args.include_look_vectors,
        los_flag=args.include_los_displacement,
    )

    zip_file = make_archive(base_name=product_name, format='zip', base_dir=product_name)

    if args.bucket:
        upload_file_to_s3(Path(zip_file), args.bucket, args.bucket_prefix)
        browse_images = Path(product_name).glob('*.png')
        for browse in browse_images:
            thumbnail = create_thumbnail(browse)
            upload_file_to_s3(browse, args.bucket, args.bucket_prefix)
            upload_file_to_s3(thumbnail, args.bucket, args.bucket_prefix)


if __name__ == '__main__':
    main()

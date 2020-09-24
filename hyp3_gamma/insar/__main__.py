"""insar_gamma processing for HyP3"""

import glob
import logging
import os
from argparse import ArgumentParser
from mimetypes import guess_type
from shutil import make_archive
from zipfile import ZipFile

import boto3
from PIL import Image
from hyp3lib.fetch import download_file
from hyp3proclib import earlier_granule_first

from hyp3_insar_gamma.ifm_sentinel import gamma_process

log = logging.getLogger(__name__)
SENTINEL_DISTRIBUTION_URL = 'https://d2jcx4uuy4zbnt.cloudfront.net'
EARTHDATA_LOGIN_DOMAIN = 'urs.earthdata.nasa.gov'
S3_CLIENT = boto3.client('s3')


def write_netrc_file(username, password):
    netrc_file = os.path.join(os.environ['HOME'], '.netrc')
    if os.path.isfile(netrc_file):
        log.warning(f'Using existing .netrc file: {netrc_file}')
    else:
        with open(netrc_file, 'w') as f:
            f.write(f'machine {EARTHDATA_LOGIN_DOMAIN} login {username} password {password}')


def get_download_url(granule):
    mission = granule[0] + granule[2]
    product_type = granule[7:10]
    if product_type == 'GRD':
        product_type += '_' + granule[10] + granule[14]
    url = f'{SENTINEL_DISTRIBUTION_URL}/{product_type}/{mission}/{granule}.zip'
    return url


def get_granule(granule):
    download_url = get_download_url(granule)
    zip_file = download_file(download_url)
    log.info(f'Unzipping {zip_file}')
    with ZipFile(zip_file) as z:
        z.extractall()
    os.remove(zip_file)
    return f'{granule}.SAFE'


def get_content_type(filename):
    content_type = guess_type(filename)[0]
    if not content_type:
        content_type = 'application/octet-stream'
    return content_type


def upload_file_to_s3(path_to_file, file_type, bucket, prefix=''):
    key = os.path.join(prefix, os.path.basename(path_to_file))
    extra_args = {'ContentType': get_content_type(key)}

    log.info(f'Uploading s3://{bucket}/{key}')
    S3_CLIENT.upload_file(path_to_file, bucket, key, extra_args)
    tag_set = {
        'TagSet': [
            {
                'Key': 'file_type',
                'Value': file_type
            }
        ]
    }
    S3_CLIENT.put_object_tagging(Bucket=bucket, Key=key, Tagging=tag_set)


def create_thumbnail(input_image, size=(100, 100)):
    filename, ext = os.path.splitext(input_image)
    thumbnail_name = f'{filename}_thumb{ext}'

    output_image = Image.open(input_image)
    output_image.thumbnail(size)
    output_image.save(thumbnail_name)
    return thumbnail_name


def string_is_true(s: str) -> bool:
    return s.lower() == 'true'


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

    write_netrc_file(args.username, args.password)

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
        upload_file_to_s3(zip_file, 'product', args.bucket, args.bucket_prefix)
        browse_images = glob.glob(f'{product_name}/*.png')
        for browse in browse_images:
            thumbnail = create_thumbnail(browse)
            upload_file_to_s3(browse, 'browse', args.bucket, args.bucket_prefix)
            upload_file_to_s3(thumbnail, 'thumbnail', args.bucket, args.bucket_prefix)


if __name__ == '__main__':
    main()

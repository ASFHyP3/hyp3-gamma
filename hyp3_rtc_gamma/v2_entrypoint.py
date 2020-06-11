from argparse import ArgumentParser
from mimetypes import guess_type
from os.path import join
import boto3


def get_content_type(filename):
    content_type = guess_type(filename)[0]
    if not content_type:
        content_type = 'application/octet-stream'
    return content_type


def upload_to_s3(filenames, bucket, prefix=''):
    s3 = boto3.client('s3')
    for filename in filenames:
        key = join(prefix, filename)
        extra_args = {'ContentType': get_content_type(filename)}
        s3.upload_file(filename, bucket, key, extra_args)


def main():
    parser = ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--bucket')
    parser.add_argument('--bucket-prefix', default='')
    parser.add_argument('granule')
    args = parser.parse_args()

    # download granule from datapool
      # via get_asf.py

    # unzip granule
      # skip this and let rtc_sentinel.py do the unzip

    # call rtc_sentinel
      # with the right default parameters
    output_files = ['output_file_1.txt', 'output_file_2.csv']
    for output_file in output_files:
        with open(output_file, 'w') as f:
            f.write(args.granule)

    # write esa citation file
      # have rtc_sentinel call new hyp3_lib function
      # just get rid of separate citation file)

    # write argis-compatable xml metadata file(s)
      # move to rtc_sentinel

    # something with browse images? (move to rtc_sentinel)

    # clip_tiffs_to_roi? (move to rtc_sentinel)

    # decide final product name? (move to rtc sentinel?)

    # zip output folder? (skip for now?)

    # upload relevant files to s3 (remember to set content-type)
    if args.bucket:
        upload_to_s3(output_files, args.bucket, args.bucket_prefix)


if __name__ == '__main__':
    main()

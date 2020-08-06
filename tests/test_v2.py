import os

import pytest
from PIL import Image
from botocore.stub import ANY, Stubber

from hyp3_rtc_gamma import __main__ as main


@pytest.fixture(autouse=True)
def s3_stubber():
    with Stubber(main.S3_CLIENT) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


def test_get_content_type():
    assert main.get_content_type('foo') == 'application/octet-stream'
    assert main.get_content_type('foo.asfd') == 'application/octet-stream'
    assert main.get_content_type('foo.txt') == 'text/plain'
    assert main.get_content_type('foo.zip') == 'application/zip'
    assert main.get_content_type('foo/bar.png') == 'image/png'


def test_get_download_url():
    granule = 'S1A_IW_GRDH_1SDV_20200611T090849_20200611T090914_032967_03D196_D46C'
    url = main.get_download_url(granule)
    assert url == f'https://d2jcx4uuy4zbnt.cloudfront.net/GRD_HD/SA/{granule}.zip'

    granule = 'S1B_IW_SLC__1SDV_20200611T071252_20200611T071322_021982_029B8F_B023'
    url = main.get_download_url(granule)
    assert url == f'https://d2jcx4uuy4zbnt.cloudfront.net/SLC/SB/{granule}.zip'


def test_write_netrc_file(tmp_path):
    os.environ['HOME'] = str(tmp_path)
    output_file = os.path.join(tmp_path, '.netrc')

    main.write_netrc_file('foo', 'bar')
    assert os.path.isfile(output_file)
    with open(output_file, 'r') as f:
        assert f.read() == 'machine urs.earthdata.nasa.gov login foo password bar'

    main.write_netrc_file('already_there', 'this call should do nothing')
    with open(output_file, 'r') as f:
        assert f.read() == 'machine urs.earthdata.nasa.gov login foo password bar'


def test_upload_file_to_s3(tmp_path, s3_stubber):
    expected_params = {
        'Body': ANY,
        'Bucket': 'myBucket',
        'Key': 'myFile.zip',
        'ContentType': 'application/zip',
    }
    s3_stubber.add_response(method='put_object', expected_params=expected_params, service_response={})

    file_to_upload = tmp_path / 'myFile.zip'
    file_to_upload.touch()
    main.upload_file_to_s3(str(file_to_upload), 'file_type', 'myBucket')


def test_upload_file_to_s3_with_prefix(tmp_path, s3_stubber):
    expected_params = {
        'Body': ANY,
        'Bucket': 'myBucket',
        'Key': 'myPrefix/myFile.txt',
        'ContentType': 'text/plain',
    }
    s3_stubber.add_response(method='put_object', expected_params=expected_params, service_response={})

    file_to_upload = tmp_path / 'myFile.txt'
    file_to_upload.touch()
    main.upload_file_to_s3(str(file_to_upload), 'file_type', 'myPrefix', 'myBucket')


def test_create_thumbnail(image):
    with Image.open(image) as input_image:
        assert input_image.size == (162, 150)

    thumbnail = main.create_thumbnail(image, (100, 100))
    assert os.path.basename(thumbnail) == 'test_thumb.png'

    with Image.open(image) as input_image:
        assert input_image.size == (162, 150)

    with Image.open(thumbnail) as output_image:
        assert output_image.size == (100, 93)

    thumbnail = main.create_thumbnail(image, (255, 255))

    with Image.open(thumbnail) as output_image:
        assert output_image.size == (162, 150)

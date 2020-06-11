import os

from hyp3_rtc_gamma import __main__ as main


def test_get_content_type():
    assert main.get_content_type('foo') == 'application/octet-stream'
    assert main.get_content_type('foo.asfd') == 'application/octet-stream'
    assert main.get_content_type('foo.txt') == 'text/plain'
    assert main.get_content_type('foo.zip') == 'application/zip'
    assert main.get_content_type('foo/bar.png') == 'image/png'


def test_get_download_url():
    granule = 'S1A_IW_GRDH_1SDV_20200611T090849_20200611T090914_032967_03D196_D46C'
    url = main.get_download_url(granule)
    assert url == f'https://datapool.asf.alaska.edu/GRD_HD/SA/{granule}.zip'

    granule = 'S1B_IW_SLC__1SDV_20200611T071252_20200611T071322_021982_029B8F_B023'
    url = main.get_download_url(granule)
    assert url == f'https://datapool.asf.alaska.edu/SLC/SB/{granule}.zip'


def test_download_file(tmp_path):
    os.chdir(tmp_path)
    main.download_file('https://imgs.xkcd.com/comics/automation.png')
    assert os.path.isfile('automation.png')


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

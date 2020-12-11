import glob
import logging
import os
from zipfile import ZipFile

from hyp3lib.fetch import download_file
from hyp3lib.scene import get_download_url

log = logging.getLogger(__name__)


def find_and_remove(directory, file_pattern):
    pattern = os.path.join(directory, file_pattern)
    for filename in glob.glob(pattern):
        logging.info(f'Removing {filename}')
        os.remove(filename)


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

import shutil
from glob import glob
from pathlib import Path

import pytest

_HERE = Path(__file__).parent


@pytest.fixture()
def test_data_folder():
    return _HERE / 'data'


@pytest.fixture(scope='session')
def product_dir(tmp_path_factory):
    prod = tmp_path_factory.mktemp('S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2', numbered=False)
    product_files = glob(str(_HERE / 'data' / 'rtc*'))
    for f in product_files:
        shutil.copy(f, prod / f'{Path(f).name.replace("rtc", prod.name)}')
    return prod

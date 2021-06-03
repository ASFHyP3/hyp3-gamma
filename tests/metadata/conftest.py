from pathlib import Path

import pytest

from hyp3_metadata import data
from hyp3_metadata.insar import populate_example_data as populate_insar
from hyp3_metadata.rtc import populate_example_data as populate_rtc


@pytest.fixture()
def test_data_folder():
    return Path(data.__file__).parent


@pytest.fixture(scope='session')
def rtc_product_dir(tmp_path_factory):
    prod = tmp_path_factory.mktemp('S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2', numbered=False)
    populate_rtc(prod)
    return prod


@pytest.fixture(scope='session')
def insar_product_dir(tmp_path_factory):
    prod = tmp_path_factory.mktemp('S1AB_20210424T125204_20210430T125122_HHP006_INT80_G_ueF_B4A1', numbered=False)
    populate_insar(prod)
    return prod

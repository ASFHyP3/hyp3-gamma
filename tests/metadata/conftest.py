from pathlib import Path

import pytest

from hyp3_metadata import data
from hyp3_metadata.util import populate_example_data


@pytest.fixture()
def test_data_folder():
    return Path(data.__file__).parent


@pytest.fixture(scope='session')
def product_dir(tmp_path_factory):
    prod = tmp_path_factory.mktemp('S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2', numbered=False)
    populate_example_data(prod)
    return prod

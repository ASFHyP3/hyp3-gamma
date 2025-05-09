import os
import shutil
from pathlib import Path

import pytest


_HERE = os.path.dirname(__file__)


@pytest.fixture()
def test_data_dir():
    here = Path(os.path.dirname(__file__))
    return here / 'data'


@pytest.fixture()
def geotiff(tmp_path):
    geotiff_file = str(tmp_path / 'test_geotiff.tif')
    shutil.copy(os.path.join(_HERE, 'data', 'test_geotiff.tif'), geotiff_file)
    return geotiff_file

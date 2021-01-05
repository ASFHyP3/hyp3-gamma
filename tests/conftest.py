import os
from pathlib import Path

import pytest


@pytest.fixture()
def test_data_dir():
    here = Path(os.path.dirname(__file__))
    return here / 'data'

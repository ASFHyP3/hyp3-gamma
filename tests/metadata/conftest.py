import os
from pathlib import Path

import pytest

_HERE = os.path.dirname(__file__)


@pytest.fixture()
def test_data_folder():
    return Path(_HERE) / 'data'

import os
import shutil

import pytest

_HERE = os.path.dirname(__file__)


@pytest.fixture()
def image(tmp_path):
    image = str(tmp_path / 'test.png')
    shutil.copy(os.path.join(_HERE, 'data', 'test.png'), image)
    return image

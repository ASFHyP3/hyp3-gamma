from pathlib import Path

import pytest
from hyp3_rtc_gamma import __main__ as main


def test_find_product_name(tmp_path):
    with pytest.raises(Exception):
        main.find_product_name('not_a_directory')

    with pytest.raises(Exception):
        main.find_product_name(tmp_path)

    Path(tmp_path / 'foo.png').touch()
    Path(tmp_path / 'foo_VV.tif').touch()
    with pytest.raises(Exception):
        main.find_product_name(tmp_path)

    Path(tmp_path / 'foo.README.txt').touch()
    assert main.find_product_name(tmp_path) == 'foo'

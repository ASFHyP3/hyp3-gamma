import logging
import os

import pytest

from hyp3_gamma.get_gamma_version import get_gamma_version


def test_gamma_version_var():
    gamma_version = '20200131'
    os.environ['GAMMA_VERSION'] = gamma_version

    result = get_gamma_version()
    os.environ.pop('GAMMA_VERSION')

    assert gamma_version == result


def test_bad_gamma_version_var(caplog):
    with caplog.at_level(logging.WARNING):
        gamma_version = '20202233'
        os.environ['GAMMA_VERSION'] = gamma_version

        _ = get_gamma_version()
        os.environ.pop('GAMMA_VERSION')

        assert 'does not conform to the expected YYYYMMDD format' in caplog.text


def test_no_gamma_home_var():
    with pytest.raises(KeyError):
        os.environ.pop('GAMMA_VERSION', None)
        os.environ.pop('GAMMA_HOME', None)

        _ = get_gamma_version()


def test_asf_gamma_version(tmp_path):
    os.environ.pop('GAMMA_VERSION', None)
    os.environ['GAMMA_HOME'] = str(tmp_path.resolve())

    gamma_version = '20170707'
    asf = tmp_path / 'ASF_Gamma_version.txt'
    asf.write_text(gamma_version)

    result = get_gamma_version()
    os.environ.pop('GAMMA_HOME')

    assert gamma_version == result


def test_bad_asf_gamma_version(caplog, tmp_path):
    with caplog.at_level(logging.WARNING):
        os.environ.pop('GAMMA_VERSION', None)
        os.environ['GAMMA_HOME'] = str(tmp_path.resolve())

        gamma_version = '20170732'
        asf = tmp_path / 'ASF_Gamma_version.txt'
        asf.write_text(gamma_version)

        _ = get_gamma_version()
        os.environ.pop('GAMMA_HOME')

        assert 'does not conform to the expected YYYYMMDD format' in caplog.text


def test_gamma_direcory_parse(caplog, tmp_path):
    with caplog.at_level(logging.WARNING):
        os.environ.pop('GAMMA_VERSION', None)

        gamma_version = '20170707'
        gamma_home = tmp_path / f'GAMMA_SOFTWARE-{gamma_version}'
        gamma_home.mkdir()
        os.environ['GAMMA_HOME'] = str(gamma_home.resolve())

        result = get_gamma_version()
        os.environ.pop('GAMMA_HOME')

        assert 'No GAMMA_VERSION environment variable or ASF_Gamma_version.txt ' in caplog.text
        assert gamma_version == result


def test_bad_gamma_direcory_parse(caplog, tmp_path):
    with caplog.at_level(logging.WARNING):
        os.environ.pop('GAMMA_VERSION', None)

        gamma_version = '20170732'
        gamma_home = tmp_path / f'GAMMA_SOFTWARE-{gamma_version}'
        gamma_home.mkdir()
        os.environ['GAMMA_HOME'] = str(gamma_home.resolve())

        _ = get_gamma_version()
        os.environ.pop('GAMMA_HOME')

        assert 'No GAMMA_VERSION environment variable or ASF_Gamma_version.txt ' in caplog.text
        assert 'does not conform to the expected YYYYMMDD format' in caplog.text

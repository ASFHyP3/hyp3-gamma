"""HyP3 plugin for processing SAR data with GAMMA"""

# FIXME: Python 3.8+ this should be `from importlib.metadata...`
from importlib_metadata import PackageNotFoundError, version


try:
    __version__ = version(__name__)
except PackageNotFoundError:
    print('package is not installed!\n'
          'Install in editable/develop mode via (from the top of this repo):\n'
          '   python -m pip install -e .[develop]\n'
          'Or, to just get the version number use:\n'
          '   python setup.py --version')

__all__ = ['__version__']

"""Package for generating HyP3 products' metadata"""

# FIXME: Python 3.8+ this should be `from importlib.metadata...`
from importlib_metadata import PackageNotFoundError, version

from hyp3_metadata.create import create_metadata_file_set_insar, create_metadata_file_set_rtc

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    print('package is not installed!\n'
          'Install in editable/develop mode via (from the top of this repo):\n'
          '   python -m pip install -e .\n'
          'Or, to just get the version number use:\n'
          '   python setup.py --version')

__all__ = ['__version__',  'create_metadata_file_set_insar', 'create_metadata_file_set_rtc']

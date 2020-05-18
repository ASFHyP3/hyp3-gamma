"""
insar_gamma processing
"""

import argparse
import logging

from hyp3_insar_gamma import __version__

log = logging.getLogger(__name__)


def process(hello_world=False):
    """Process hello_world

    Args:
        hello_world (bool): If true, print "Hello world!" (Default: False)
    """
    log.debug(f'Hello world? {hello_world}')
    if hello_world:
        print("Hello world!")


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='proc_insar_gamma',
        description=__doc__,
    )
    parser.add_argument('--hello-world', action='store_true',
                        help='Print "Hello world!"')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    process(**args.__dict__)


if __name__ == "__main__":
    main()

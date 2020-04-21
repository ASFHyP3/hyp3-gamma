"""
rtc_gamma processing for HyP3
"""

import os
from datetime import datetime

import hyp3proclib
from hyp3proclib.logger import log
from hyp3proclib.proc_base import Processor

import hyp3_rtc_gamma


def hyp3_process(cfg, n):
    try:
        log.info('Processing hello_world')
        if not cfg['skip_processing']:
            log.info(f'Process starting at {datetime.now()}')
            launch_dir = os.getcwd()
            os.chdir(cfg['workdir'])

            hyp3proclib.process(
                cfg, 'proc_rtc_gamma', ["--hello-world"]
            )

            os.chdir(launch_dir)
        else:
            log.info('Processing skipped!')
            cfg['log'] += "(debug mode)"

        cfg['success'] = True
        hyp3proclib.update_completed_time(cfg)

        product_dir = os.path.join(cfg['workdir'], 'PRODUCT')
        if not os.path.isdir(product_dir):
            log.info(f'PRODUCT directory not found: {product_dir}')
            log.error('Processing failed')
            raise Exception('Processing failed: PRODUCT directory not found')
        else:
            # TODO: final product cleanup and upload to HyP3 DB
            pass

    except Exception as e:
        log.exception('rtc_gamma processing failed!')
        log.exception('Notifying user')
        hyp3proclib.failure(cfg, str(e))

    hyp3proclib.file_system.cleanup_workdir(cfg)

    log.info('rtc_gamma done')


def main():
    """
    Main entrypoint for hyp3_rtc_gamma
    """
    processor = Processor(
        'rtc_gamma', hyp3_process, sci_version=hyp3_rtc_gamma.__version__
    )
    processor.run()


if __name__ == '__main__':
    main()

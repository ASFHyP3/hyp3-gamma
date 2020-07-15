import logging
import os
import shutil

from hyp3lib import ExecuteError
from hyp3lib.SLC_copy_S1_fullSW import SLC_copy_S1_fullSW
from hyp3lib.execute import execute
from hyp3lib.getBursts import getBursts
from hyp3lib.get_orb import downloadSentinelOrbitFile
from hyp3lib.par_s1_slc_single import par_s1_slc_single


def ingest_S1_granule(safe_dir, pol, looks, out_file, orbit_file=None):
    """

    Args:
        safe_dir:
        pol:
        looks:
        out_file:
        orbit_file:
    """
    pol = pol.lower()
    granule_type = safe_dir[7:11]

    # Ingest the granule into gamma format
    if "GRD" in granule_type:
        cmd = f'par_S1_GRD {safe_dir}/*/*{pol}*.tiff {safe_dir}/*/*{pol}*.xml {safe_dir}/*/*/calibration-*{pol}*.xml ' \
              f'{safe_dir}/*/*/noise-*{pol}*.xml {pol}.grd.par {pol}.grd'
        execute(cmd, uselogging=True)

        # Fetch precision state vectors

        try:
            if orbit_file is None:
                logging.info('Trying to get orbit file information from file {}'.format(safe_dir))
                orbit_file, _ = downloadSentinelOrbitFile(safe_dir)
            logging.debug('Applying precision orbit information')
            cmd = f'S1_OPOD_vec {pol}.grd.par {orbit_file}'
            execute(cmd, uselogging=True)
        except ExecuteError:  # TODO orbit download error...
            logging.warning('Unable to fetch precision state vectors... continuing')

        # Multi-look the image
        if looks > 1.0:
            cmd = f'multi_look_MLI {pol}.grd {pol}.grd.par {out_file} {out_file}.par {looks} {looks}'
            execute(cmd, uselogging=True)
        else:
            shutil.copy(f'{pol}.grd', out_file)
            shutil.copy(f'{pol}.grd.par', f'{out_file}.par')

    else:
        #  Ingest SLC data files into gamma format
        par_s1_slc_single(safe_dir, pol)
        date = safe_dir[17:25]
        make_tab_flag = True
        burst_tab = getBursts(safe_dir, make_tab_flag)
        shutil.copy(burst_tab, date)

        # Mosaic the swaths together and copy SLCs over        
        back = os.getcwd()
        os.chdir(date)
        path = '../'
        rlooks = looks * 5
        alooks = looks
        SLC_copy_S1_fullSW(path, date, 'SLC_TAB', burst_tab, mode=2, raml=rlooks, azml=alooks)
        os.chdir(back)

        # Rename files
        shutil.move(f'{date}.mli', out_file)
        shutil.move(f'{date}.mli.par', f'{out_file}.par')

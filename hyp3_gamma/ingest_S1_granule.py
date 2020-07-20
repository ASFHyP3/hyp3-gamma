import logging
import os
import shutil

from hyp3lib import OrbitDownloadError
from hyp3lib.SLC_copy_S1_fullSW import SLC_copy_S1_fullSW
from hyp3lib.execute import execute
from hyp3lib.getBursts import getBursts
from hyp3lib.get_orb import downloadSentinelOrbitFile
from hyp3lib.par_s1_slc_single import par_s1_slc_single


def ingest_S1_granule(safe_dir: str, pol: str, looks: int, out_file: str, orbit_file: str = None):
    """Pre-process S1 imagery into GAMMA format

    Args:
        safe_dir: Sentinel-1 SAFE directory location
        pol: polarization (e.g., 'vv')
        looks: the number of looks to take
        out_file: file name of the output GAMMA formatted imagery
        orbit_file: Orbit file to use (will download a matching orbit file if None)
    """
    pol = pol.lower()
    granule_type = safe_dir[7:10]

    # Ingest the granule into gamma format
    if granule_type == 'GRD':
        cmd = f'par_S1_GRD {safe_dir}/*/*{pol}*.tiff {safe_dir}/*/*{pol}*.xml {safe_dir}/*/*/calibration-*{pol}*.xml ' \
              f'{safe_dir}/*/*/noise-*{pol}*.xml {pol}.grd.par {pol}.grd'
        execute(cmd, uselogging=True)

        # Ingest the precision state vectors
        try:
            if orbit_file is None:
                logging.info('Trying to get orbit file information from file {}'.format(safe_dir))
                orbit_file, _ = downloadSentinelOrbitFile(safe_dir)
            logging.debug('Applying precision orbit information')
            execute(f'S1_OPOD_vec {pol}.grd.par {orbit_file}', uselogging=True)
        except OrbitDownloadError:
            logging.warning('Unable to fetch precision state vectors... continuing')

        if looks > 1.0:
            cmd = f'multi_look_MLI {pol}.grd {pol}.grd.par {out_file} {out_file}.par {looks} {looks}'
            execute(cmd, uselogging=True)
        else:
            shutil.copy(f'{pol}.grd', out_file)
            shutil.copy(f'{pol}.grd.par', f'{out_file}.par')

    else:
        #  Ingest SLC data files into gamma format
        par_s1_slc_single(safe_dir, pol, orbit_file=orbit_file)
        date = safe_dir[17:25]
        burst_tab = getBursts(safe_dir, make_tab_flag=True)
        shutil.copy(burst_tab, date)

        # Mosaic the swaths together and copy SLCs over        
        back = os.getcwd()
        os.chdir(date)
        SLC_copy_S1_fullSW('../', date, 'SLC_TAB', burst_tab, mode=2, raml=looks * 5, azml=looks)
        os.chdir(back)

        shutil.move(f'{date}.mli', out_file)
        shutil.move(f'{date}.mli.par', f'{out_file}.par')

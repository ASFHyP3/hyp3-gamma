import glob
import logging
import os

from hyp3lib import OrbitDownloadError
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from hyp3lib.get_orb import downloadSentinelOrbitFile


def make_cmd(swath, acquisition_date, out_dir, pol=None):
    """Assemble the par_S1_SLC gamma commands
    
    Args:
        swath: Swath to process
        acquisition_date: The acquisition date of the SLC imagery
        out_dir: Where to output the GAMMA formatted files
        pol: pol: polarization (e.g., 'vv')
    """
    if pol is None:
        m = glob.glob(f'measurement/s1*-iw{swath}*')[0]
        n = glob.glob(f'annotation/s1*-iw{swath}*')[0]
        o = glob.glob(f'annotation/calibration/calibration-s1*-iw{swath}*')[0]
        p = glob.glob(f'annotation/calibration/noise-s1*-iw{swath}*')[0]
    else:
        m = glob.glob(f'measurement/s1*-iw{swath}*{pol}*')[0]
        n = glob.glob(f'annotation/s1*-iw{swath}*{pol}*')[0]
        o = glob.glob(f'annotation/calibration/calibration-s1*-iw{swath}*{pol}*')[0]
        p = glob.glob(f'annotation/calibration/noise-s1*-iw{swath}*{pol}*')[0]
    
    cmd = f'par_S1_SLC {m} {n} {o} {p} {out_dir}/{acquisition_date}_00{swath}.slc.par ' \
          f'{out_dir}/{acquisition_date}_00{swath}.slc {out_dir}/{acquisition_date}_00{swath}.tops_par'
    
    return cmd


def par_s1_slc_single(safe_dir, pol='vv', orbit_file=None):
    """Pre-process S1 SLC imagery into GAMMA format SLCs

    Args:
        safe_dir: Sentinel-1 SAFE directory location
        pol: polarization (e.g., 'vv')
        orbit_file: Orbit file to use (will download a matching orbit file if None)
    """
    wrk = os.getcwd()
    pol = pol.lower()

    logging.info(f'Procesing directory {safe_dir}')
    image_type = safe_dir[13:16]
    logging.info(f'Found image type {image_type}')

    datelong = safe_dir.split('_')[5]
    acquisition_date = (safe_dir.split('_')[5].split('T'))[0]
    path = os.path.join(wrk, acquisition_date)
    if not os.path.exists(path):
        os.mkdir(path)

    logging.info(f'SAFE directory is {safe_dir}')
    logging.info(f'Long date is {datelong}')
    logging.info(f'Acquisition date is {acquisition_date}')

    os.chdir(safe_dir)

    for swath in range(1, 4):
        cmd = make_cmd(swath, acquisition_date, path, pol=pol)
        execute(cmd, uselogging=True)

    os.chdir(path)

    # Ingest the precision state vectors
    try:
        if orbit_file is None:
            logging.info(f'Trying to get orbit file information from file {safe_dir}')
            orbit_file, _ = downloadSentinelOrbitFile(safe_dir)
        logging.info('Applying precision orbit information')
        execute(f'S1_OPOD_vec {acquisition_date}_001.slc.par {orbit_file}', uselogging=True)
        execute(f'S1_OPOD_vec {acquisition_date}_002.slc.par {orbit_file}', uselogging=True)
        execute(f'S1_OPOD_vec {acquisition_date}_003.slc.par {orbit_file}', uselogging=True)
    except OrbitDownloadError:
        logging.warning('Unable to fetch precision state vectors... continuing')

    slc = glob.glob('*_00*.slc')
    slc.sort()
    par = glob.glob('*_00*.slc.par')
    par.sort()
    top = glob.glob('*_00*.tops_par')
    top.sort()
    with open(os.path.join(path, 'SLC_TAB'), 'w') as f:
        for i in range(len(slc)):
            f.write(f'{slc[i]} {par[i]} {top[i]}\n')

    # Make a raster version of swath 3
    width = getParameter(f'{acquisition_date}_003.slc.par', 'range_samples')
    execute(f"rasSLC {acquisition_date}_003.slc {width} 1 0 50 10")
    os.chdir(wrk)

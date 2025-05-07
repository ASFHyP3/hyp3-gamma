"""re-process S1 SLC imagery into gamma format SLCs"""

import logging
import os
import shutil

from hyp3lib.execute import execute

from hyp3_gamma.get_parameter import get_parameter


def slc_copy_s1_full_sw(path, slcname, tabin, burst_tab, mode=2, dem=None, dempath=None, raml=10, azml=2):
    logging.info('Using range looks {}'.format(raml))
    logging.info('Using azimuth looks {}'.format(azml))
    logging.info('Operating in mode {}'.format(mode))
    logging.info('In directory {}'.format(os.getcwd()))

    if not os.path.isfile(tabin):
        logging.error("ERROR: Can't find tab file {} in {}".format(tabin, os.getcwd()))
    f = open(tabin, 'r')
    g = open('TAB_swFULL', 'w')
    for line in f:
        s = line.split()
        for i in range(len(s)):
            g.write('{} '.format(os.path.join(path, s[i])))
        g.write('\n')
    f.close()
    g.close()

    wrk = os.getcwd()

    cmd = 'SLC_copy_S1_TOPS {} {} {}'.format(tabin, 'TAB_swFULL', burst_tab)
    execute(cmd, uselogging=True)

    shutil.copy(tabin, path)
    os.chdir(path)

    cmd = 'SLC_mosaic_S1_TOPS {TAB} {SLC}.slc {SLC}.slc.par {RL} {AL}'.format(TAB=tabin, SLC=slcname, RL=raml, AL=azml)
    execute(cmd, uselogging=True)

    width = get_parameter('{}.slc.par'.format(slcname), 'range_samples')
    cmd = 'rasSLC {}.slc {} 1 0 50 10'.format(slcname, width)
    execute(cmd, uselogging=True)

    cmd = 'multi_S1_TOPS {TAB} {SLC}.mli {SLC}.mli.par {RL} {AL}'.format(TAB=tabin, SLC=slcname, RL=raml, AL=azml)
    execute(cmd, uselogging=True)

    mode = int(mode)
    if mode == 1:
        logging.info('currently in {}'.format(os.getcwd()))
        logging.info('creating directory DEM')

        if not os.path.exists('DEM'):
            os.mkdir('DEM')
        os.chdir('DEM')
        mliwidth = get_parameter('../{}.mli.par'.format(slcname), 'range_samples')
        mlinline = get_parameter('../{}.mli.par'.format(slcname), 'azimuth_lines')

        # FIXME: Convert to an f-string
        cmd = 'GC_map_mod ../{SLC}.mli.par  - {DP}/{DEM}.par {DP}/{DEM}.dem 2 2 demseg.par demseg ../{SLC}.mli  MAP2RDC inc pix ls_map 1 1'.format(  # noqa: E501
            SLC=slcname, DEM=dem, DP=dempath
        )
        execute(cmd, uselogging=True)

        demwidth = get_parameter('demseg.par', 'width')

        cmd = 'geocode MAP2RDC demseg {} HGT_SAR_{}_{} {} {}'.format(demwidth, raml, azml, mliwidth, mlinline)
        execute(cmd, uselogging=True)

        # FIXME: Convert to an f-string
        cmd = 'gc_map ../{SLC}.mli.par - {DP}/{DEM}.par 1 demseg.par demseg map_to_rdc 2 2 pwr_sim_map - - inc_flat'.format(  # noqa: E501
            SLC=slcname, DP=dempath, DEM=dem
        )
        execute(cmd, uselogging=True)

        os.chdir('..')

    shutil.copy(tabin, 'SLC{}_tab'.format(mode))
    os.chdir(wrk)

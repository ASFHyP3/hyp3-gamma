"""re-process S1 SLC imagery into gamma format SLCs"""

import argparse
import logging
import os
import shutil

from hyp3lib.execute import execute

from hyp3_gamma.getParameter import getParameter


def SLC_copy_S1_fullSW(path, slcname, tabin, burst_tab, mode=2, dem=None, dempath=None, raml=10, azml=2):
    logging.info(f"Using range looks {raml}")
    logging.info(f"Using azimuth looks {azml}")
    logging.info(f"Operating in mode {mode}")
    logging.info(f"In directory {os.getcwd()}")

    if not os.path.isfile(tabin):
        logging.error(f"ERROR: Can't find tab file {tabin} in {os.getcwd()}")
    f = open(tabin, "r")
    g = open("TAB_swFULL", "w")
    for line in f:
        s = line.split()
        for i in range(len(s)):
            g.write(f"{os.path.join(path, s[i])} ")
        g.write("\n")
    f.close()
    g.close()

    wrk = os.getcwd()

    execute(f"SLC_copy_S1_TOPS {tabin} {'TAB_swFULL'} {burst_tab}", uselogging=True)

    shutil.copy(tabin, path)
    os.chdir(path)

    execute(f"SLC_mosaic_S1_TOPS {tabin} {slcname}.slc {slcname}.slc.par {raml} {azml}", uselogging=True)

    width = getParameter(f"{slcname}.slc.par", "range_samples")
    execute(f"rasSLC {slcname}.slc {width} 1 0 50 10", uselogging=True)

    execute(f"multi_S1_TOPS {tabin} {slcname}.mli {slcname}.mli.par {raml} {azml}", uselogging=True)

    mode = int(mode)
    if mode == 1:

        logging.info(f"currently in {os.getcwd()}")
        logging.info("creating directory DEM")

        if not os.path.exists("DEM"):
            os.mkdir("DEM")
        os.chdir("DEM")
        mliwidth = getParameter(f"../{slcname}.mli.par", "range_samples")
        mlinline = getParameter(f"../{slcname}.mli.par", "azimuth_lines")

        execute(
            f"GC_map_mod ../{slcname}.mli.par  - {dempath}/{dem}.par "
            f"{dempath}/{dem}.dem 2 2 demseg.par demseg ../{slcname}.mli  MAP2RDC inc pix ls_map 1 1",
            uselogging=True
        )

        demwidth = getParameter("demseg.par", "width")

        execute(f"geocode MAP2RDC demseg {demwidth} HGT_SAR_{raml}_{azml} {mliwidth} {mlinline}", uselogging=True)

        execute(
            f"gc_map ../{slcname}.mli.par - "
            f"{dempath}/{dem}.par 1 demseg.par demseg map_to_rdc 2 2 pwr_sim_map - - inc_flat",
            uselogging=True
        )

        os.chdir("..")

    shutil.copy(tabin, f"SLC{mode}_tab")
    os.chdir(wrk)


def main():
    """Main entrypoint"""

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description=__doc__,
    )
    parser.add_argument('outDir', help="Absolute path to destination folder")
    parser.add_argument('slcID', help="SLC identifier (e.g. 20150429)")
    parser.add_argument('slcTab', help='SLC Tab file')
    parser.add_argument('burstTab', help='Burst tab for which bursts to copy')
    parser.add_argument('mode', help='1 = master image, 2 = slave image')
    parser.add_argument('-d', '--dem', help='Name of DEM file', dest="dem")
    parser.add_argument('-p', '--path', help='Path to DEM file', dest="path")
    parser.add_argument('-rl', '--rangelooks', default='10', help='Number of range looks', dest="rl")
    parser.add_argument('-al', '--azimuthlooks', default='2', help='Number of range looks', dest="al")
    args = parser.parse_args()

    if not os.path.exists(args.slcTab):
        logging.error(f"ERROR:  Can't find slc tab file {args.slcTab}")

    if not os.path.exists(args.burstTab):
        logging.error(f"ERROR:  Can't find burst tab file {args.burstTab}")

    log_file = "SLC_copy_S1_fullSW_log.txt"
    logging.basicConfig(filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    SLC_copy_S1_fullSW(
        args.outDir, args.slcID, args.slcTab, args.burstTab, args.mode, args.dem,
        args.path, args.rl, args.al
    )


if __name__ == '__main__':
    main()

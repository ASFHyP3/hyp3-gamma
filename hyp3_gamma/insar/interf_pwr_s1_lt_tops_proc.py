"""Sentinel-1 SLC data and DEM coregistration process"""

import argparse
import logging
import os
import shutil
import sys

from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter


def create_slc2r_tab(SLC2tab, SLC2Rtab):
    if os.path.isfile(SLC2Rtab):
        os.remove(SLC2Rtab)

    with open(SLC2Rtab, "wb") as g:
        with open(SLC2tab) as f:
            content = f.readlines()
            for item in content:
                item = item.rstrip()
                out = item.replace("slc", "rslc")
                out = out.replace("tops", "rtops")
                g.write("{}\n".format(out).encode())


def coregister_data(cnt, SLC2tab, SLC2Rtab, spar, mpar, mmli, smli, ifgname,
                    reference, secondary, lt, rlooks, alooks, iterations):
    if cnt < iterations + 1:
        offi = ifgname + ".off_{}".format(cnt)
    else:
        offi = ifgname + ".off.it.corrected.temp"

    if cnt == 0:
        offit = "-"
    elif cnt < iterations + 1:
        offit = ifgname + ".off.it"
    else:
        offit = ifgname + ".off.it.corrected"

    SLC1tab = "SLC1_tab"
    srslc = secondary + ".rslc"
    srpar = secondary + ".rslc.par"

    execute(f"SLC_interp_lt_S1_TOPS {SLC2tab} {spar} {SLC1tab} {mpar} {lt}"
            f" {mmli} {smli} {offit} {SLC2Rtab} {srslc} {srpar}", uselogging=True)

    execute(f"create_offset {mpar} {spar} {offi} 1 {rlooks} {alooks} 0", uselogging=True)

    if cnt < iterations + 1:
        cmd_sfx = "256 64 offsets 1 64 256 0.2"
    else:
        cmd_sfx = "512 256 - 1 16 64 0.2"
    execute(f"offset_pwr {reference}.slc {secondary}.rslc {mpar} {srpar} {offi} offs snr {cmd_sfx}", uselogging=True)

    with open("offsetfit{}.log".format(cnt), "w") as log:
        execute(f"offset_fit offs snr {offi} - - 0.2 1", uselogging=True, logfile=log)

    if cnt < iterations + 1:
        ifg_diff_sfx = f'it{cnt}'
    else:
        ifg_diff_sfx = 'man'
    execute(f"SLC_diff_intf {reference}.slc {secondary}.rslc {mpar} {srpar} {offi}"
            f" {ifgname}.sim_unw {ifgname}.diff0.{ifg_diff_sfx} {rlooks} {alooks} 0 0", uselogging=True)

    width = getParameter(offi, "interferogram_width")
    f"offset_add {offit} {offi} {offi}.temp"
    execute(f"rasmph_pwr {ifgname}.diff0.{ifg_diff_sfx} {reference}.mli {width} 1 1 0 3 3", uselogging=True)

    if cnt == 0:
        offit = ifgname + ".off.it"
        shutil.copy(offi, offit)
    elif cnt < iterations + 1:
        execute(f"offset_add {offit} {offi} {offi}.temp", uselogging=True)
        shutil.copy("{}.temp".format(offi), offit)
    else:
        execute(f"offset_add {offit} {offi} {offi}.out", uselogging=True)


def interf_pwr_s1_lt_tops_proc(reference, secondary, dem, rlooks=10, alooks=2, iterations=5, step=0):
    # Setup various file names that we'll need
    ifgname = "{}_{}".format(reference, secondary)
    SLC2tab = "SLC2_tab"
    SLC2Rtab = "SLC2R_tab"
    lt = "{}.lt".format(reference)
    mpar = reference + ".slc.par"
    spar = secondary + ".slc.par"
    mmli = reference + ".mli.par"
    smli = secondary + ".mli.par"
    off = ifgname + ".off_temp"

    # Make a fresh slc2r tab
    create_slc2r_tab(SLC2tab, SLC2Rtab)

    if step == 0:
        if not os.path.isfile(dem):
            logging.info("Currently in directory {}".format(os.getcwd()))
            logging.error("ERROR: Input DEM file {} can't be found!".format(dem))
            sys.exit(1)
        logging.info("Input DEM file {} found".format(dem))
        logging.info("Preparing initial look up table and sim_unw file")
        execute(f"create_offset {mpar} {spar} {off} 1 {rlooks} {alooks} 0", uselogging=True)

        execute(f"rdc_trans {mmli} {dem} {smli} {lt}", uselogging=True)

        execute(f"phase_sim_orb {mpar} {spar} {off} {dem} {ifgname}.sim_unw {mpar} -", uselogging=True)

    elif step == 1:
        logging.info("Starting initial coregistration with look up table")
        coregister_data(
            0, SLC2tab, SLC2Rtab, spar, mpar, mmli, smli, ifgname, reference, secondary, lt, rlooks, alooks, iterations
        )
    elif step == 2:
        logging.info("Starting iterative coregistration with look up table")
        for n in range(1, iterations + 1):
            coregister_data(
                n, SLC2tab, SLC2Rtab, spar, mpar, mmli, smli, ifgname,
                reference, secondary, lt, rlooks, alooks, iterations
            )
    elif step == 3:
        logging.info("Starting single interation coregistration with look up table")
        coregister_data(
            iterations + 1, SLC2tab, SLC2Rtab, spar, mpar, mmli, smli, ifgname,
            reference, secondary, lt, rlooks, alooks, iterations
        )
    else:
        logging.error("ERROR: Unrecognized step {}; must be from 0 - 2".format(step))
        sys.exit(1)


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='INTERF_PWR_S1_LT_TOPS_Proc.py',
        description=__doc__,
    )

    parser.add_argument("reference", help='Reference scene identifier')
    parser.add_argument("secondary", help='Secondary scene identifier')
    parser.add_argument("dem", help='Dem file in SAR coordinates (e.g. ./DEM/HGT_SAR_10_2)')
    parser.add_argument("-r", "--rlooks", type=int, default=10, help="Number of range looks (def=10)")
    parser.add_argument("-a", "--alooks", type=int, default=2, help="Number of azimuth looks (def=2)")
    parser.add_argument("-i", "--iter", type=int, default=5, help='Number of coregistration iterations (def=5)')
    parser.add_argument("-s", "--step", type=int, default=0,
                        help='Procesing step: 0) Prepare LUT and SIM_UNW; '
                             '1) Initial co-registration with DEM; 2) iteration coregistration')
    args = parser.parse_args()

    logFile = "interf_pwr_s1_tops_proc_log.txt"
    logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    interf_pwr_s1_lt_tops_proc(args.reference, args.secondary, args.dem, rlooks=args.rlooks, alooks=args.alooks,
                               iterations=args.iter, step=args.step)


if __name__ == "__main__":
    main()

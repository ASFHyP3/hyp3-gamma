"""Unwrap and geocode Sentinel-1 INSAR products from GAMMA"""

import argparse
import logging
import os

from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter


def geocode_back(inname, outname, width, lt, demw, demn, type):
    cmd = "geocode_back {IN} {W} {LT} {OUT} {DEMW} {DEMN} 0 {TYPE}".format(IN=inname, W=width, LT=lt, OUT=outname,
                                                                           DEMW=demw, DEMN=demn, TYPE=type)
    execute(cmd, uselogging=True)


def data2geotiff(inname, outname, dempar, type):
    cmd = "data2geotiff {DEM} {IN} {TYPE} {OUT}".format(DEM=dempar, IN=inname, OUT=outname, TYPE=type)
    execute(cmd, uselogging=True)


def unwrapping_geocoding(master, slave, step="man", rlooks=10, alooks=2, trimode=0,
                         npatr=1, npata=1, alpha=0.6):
    dem = "./DEM/demseg"
    dempar = "./DEM/demseg.par"
    lt = "./DEM/MAP2RDC"
    ifgname = "{}_{}".format(master, slave)
    offit = "{}.off.it".format(ifgname)
    mmli = master + ".mli"
    smli = slave + ".mli"

    if not os.path.isfile(dempar):
        logging.error("ERROR: Unable to find dem par file {}".format(dempar))

    if not os.path.isfile(lt):
        logging.error("ERROR: Unable to find look up table file {}".format(lt))

    if not os.path.isfile(offit):
        logging.error("ERROR: Unable to find offset file {}".format(offit))

    width = getParameter(offit, "interferogram_width")
    mwidth = getParameter(mmli + ".par", "range_samples")
    swidth = getParameter(smli + ".par", "range_samples")
    demw = getParameter(dempar, "width")
    demn = getParameter(dempar, "nlines")

    ifgf = "{}.diff0.{}".format(ifgname, step)

    logging.info("{} will be used for unwrapping and geocoding".format(ifgf))

    logging.info("-------------------------------------------------")
    logging.info("            Start unwrapping")
    logging.info("-------------------------------------------------")

    cmd = "cc_wave {IFGF} {MMLI} - {IFG}.cc {W}".format(IFGF=ifgf, IFG=ifgname, MMLI=mmli, W=width)
    execute(cmd, uselogging=True)

    cmd = "rascc {IFG}.cc {MMLI} {W} 1 1 0 1 1 .1 .9 - - - {IFG}.cc.ras".format(IFG=ifgname, MMLI=mmli, W=width)
    execute(cmd, uselogging=True)

    cmd = "adf {IFGF} {IFGF}.adf {IFG}.adf.cc {W} {A} - 5".format(IFGF=ifgf, IFG=ifgname, W=width, A=alpha)
    execute(cmd, uselogging=True)

    cmd = "rasmph_pwr {IFGF}.adf {MMLI} {W}".format(IFGF=ifgf, MMLI=mmli, W=width)
    execute(cmd, uselogging=True)

    cmd = "rascc {IFG}.adf.cc {MMLI} {W} 1 1 0 1 1 .1 .9 - - - {IFG}.adf.cc.ras".format(IFG=ifgname, MMLI=mmli, W=width)
    execute(cmd, uselogging=True)

    cmd = "rascc_mask {IFG}.adf.cc {MMLI} {W} 1 1 0 1 1 0.10 0.20 ".format(IFG=ifgname, MMLI=mmli, W=width)
    execute(cmd, uselogging=True)

    cmd = "mcf {IFGF}.adf {IFG}.adf.cc {IFG}.adf.cc_mask.bmp {IFG}.adf.unw {W} {TRI} 0 0 - - {NPR} {NPA}".format(
        IFGF=ifgf, IFG=ifgname, W=width, TRI=trimode, NPR=npatr, NPA=npata)

    #    cmd = "mcf {IFGF}.adf {IFG}.adf.cc - {IFG}.adf.unw {W} {TRI} 0 0 - - {NPR} {NPA}".format(
    #        IFGF=ifgf,IFG=ifgname,W=width,TRI=trimode,NPR=npatr,NPA=npata)

    execute(cmd, uselogging=True)

    cmd = "rasrmg {IFG}.adf.unw {MMLI} {W} 1 1 0 1 1 0.33333 1.0 .35 0.0 - {IFG}.adf.unw.ras".format(IFG=ifgname,
                                                                                                     MMLI=mmli, W=width)
    execute(cmd, uselogging=True)

    cmd = "dispmap {IFG}.adf.unw DEM/HGT_SAR_{RL}_{AL} {MMLI}.par - {IFG}.vert.disp 1".format(IFG=ifgname, RL=rlooks,
                                                                                              AL=alooks, MMLI=mmli)
    execute(cmd, uselogging=True)

    cmd = "rashgt {IFG}.vert.disp - {W} 1 1 0 1 1 0.028".format(IFG=ifgname, W=width)
    execute(cmd, uselogging=True)

    cmd = "dispmap {IFG}.adf.unw DEM/HGT_SAR_{RL}_{AL} {MMLI}.par - {IFG}.los.disp 0".format(IFG=ifgname, RL=rlooks,
                                                                                             AL=alooks, MMLI=mmli)
    execute(cmd, uselogging=True)

    cmd = "rashgt {IFG}.los.disp - {W} 1 1 0 1 1 0.028".format(IFG=ifgname, W=width)
    execute(cmd, uselogging=True)

    logging.info("-------------------------------------------------")
    logging.info("            End unwrapping")
    logging.info("-------------------------------------------------")

    logging.info("-------------------------------------------------")
    logging.info("            Start geocoding")
    logging.info("-------------------------------------------------")

    geocode_back(mmli, mmli + ".geo", mwidth, lt, demw, demn, 0)
    geocode_back(smli, smli + ".geo", swidth, lt, demw, demn, 0)
    geocode_back("{}.sim_unw".format(ifgname), "{}.sim_unw.geo".format(ifgname), width, lt, demw, demn, 0)
    geocode_back("{}.adf.unw".format(ifgname), "{}.adf.unw.geo".format(ifgname), width, lt, demw, demn, 0)
    geocode_back("{}.adf".format(ifgf), "{}.adf.geo".format(ifgf), width, lt, demw, demn, 1)
    geocode_back("{}.adf.unw.ras".format(ifgname), "{}.adf.unw.geo.bmp".format(ifgname), width, lt, demw, demn, 2)
    geocode_back("{}.adf.bmp".format(ifgf), "{}.adf.bmp.geo".format(ifgf), width, lt, demw, demn, 2)
    geocode_back("{}.cc".format(ifgname), "{}.cc.geo".format(ifgname), width, lt, demw, demn, 0)
    geocode_back("{}.adf.cc".format(ifgname), "{}.adf.cc.geo".format(ifgname), width, lt, demw, demn, 0)
    geocode_back("{}.vert.disp.bmp".format(ifgname), "{}.vert.disp.bmp.geo".format(ifgname), width, lt, demw, demn, 2)
    geocode_back("{}.vert.disp".format(ifgname), "{}.vert.disp.geo".format(ifgname), width, lt, demw, demn, 0)
    geocode_back("{}.los.disp.bmp".format(ifgname), "{}.los.disp.bmp.geo".format(ifgname), width, lt, demw, demn, 2)
    geocode_back("{}.los.disp".format(ifgname), "{}.los.disp.geo".format(ifgname), width, lt, demw, demn, 0)

    data2geotiff(mmli + ".geo", mmli + ".geo.tif", dempar, 2)
    data2geotiff(smli + ".geo", smli + ".geo.tif", dempar, 2)
    data2geotiff("{}.sim_unw.geo".format(ifgname), "{}.sim_unw.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.adf.unw.geo".format(ifgname), "{}.adf.unw.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.adf.unw.geo.bmp".format(ifgname), "{}.adf.unw.geo.bmp.tif".format(ifgname), dempar, 0)
    data2geotiff("{}.adf.bmp.geo".format(ifgf), "{}.adf.bmp.geo.tif".format(ifgf), dempar, 0)
    data2geotiff("{}.cc.geo".format(ifgname), "{}.cc.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.adf.cc.geo".format(ifgname), "{}.adf.cc.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("DEM/demseg", "{}.dem.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.vert.disp.bmp.geo".format(ifgname), "{}.vert.disp.geo.tif".format(ifgname), dempar, 0)
    data2geotiff("{}.vert.disp.geo".format(ifgname), "{}.vert.disp.geo.org.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.los.disp.bmp.geo".format(ifgname), "{}.los.disp.geo.tif".format(ifgname), dempar, 0)
    data2geotiff("{}.los.disp.geo".format(ifgname), "{}.los.disp.geo.org.tif".format(ifgname), dempar, 2)
    data2geotiff("DEM/inc_flat", "{}.inc.tif".format(ifgname), dempar, 2)
    cmd = "look_vector {MMLI}.par {OFFIT} {DEMPAR} {DEM} lv_theta lv_phi".format(MMLI=mmli, OFFIT=offit, DEMPAR=dempar,
                                                                                 DEM=dem)
    execute(cmd, uselogging=True)
    data2geotiff("lv_theta", "{}.lv_theta.tif".format(ifgname), dempar, 2)
    data2geotiff("lv_phi", "{}.lv_phi.tif".format(ifgname), dempar, 2)

    logging.info("-------------------------------------------------")
    logging.info("            End geocoding")
    logging.info("-------------------------------------------------")


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='unwrapping_geocoding.py',
        description=__doc__,
    )
    parser.add_argument("master", help='Master scene identifier')
    parser.add_argument("slave", help='Slave scene identifier')
    parser.add_argument("-s", "--step", default='man', help='Level of interferogram for unwrapping (def=man)')
    parser.add_argument("-r", "--rlooks", default=10, help="Number of range looks (def=10)")
    parser.add_argument("-a", "--alooks", default=2, help="Number of azimuth looks (def=2)")
    parser.add_argument("-t", "--tri", default=0,
                        help="Triangulation method for mcf unwrapper: "
                             "0) filled traingular mesh (default); 1) Delaunay triangulation")
    parser.add_argument("--alpha", default=0.6, type=float, help="adf filter alpha value (def=0.6)")
    parser.add_argument("--npatr", default=1, help="Number of patches in range (def=1)")
    parser.add_argument("--npata", default=1, help="Number of patches in azimuth (def=1)")
    args = parser.parse_args()

    logFile = "unwrapping_geocoding_log.txt"
    logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    unwrapping_geocoding(args.master, args.slave, step=args.step, rlooks=args.rlooks, alooks=args.alooks,
                         trimode=args.tri, npatr=args.npatr, npata=args.npata, alpha=args.alpha)


if __name__ == "__main__":
    main()

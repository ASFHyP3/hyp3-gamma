import argparse
import glob
import logging
import os
import sys

from hyp3lib import saa_func_lib as saa
from hyp3lib.ps2dem import ps2dem
from osgeo import gdal


def smooth_dem_tiles(demdir, build=True):
    os.chdir(demdir)

    for mytif in glob.glob("*_8m_dem.tif"):
        newtif = mytif.replace(".tif", "_30m.tif")
        print("creating file {}".format(newtif))
        gdal.Translate(newtif, mytif, xRes=30, yRes=30)

    for mytif in glob.glob("*_8m_dem_30m.tif"):

        new_name = mytif.replace(".tif", "_smooth.tif")
        print("new_name {}".format(new_name))
        if not os.path.isfile(new_name):

            print("Cleaning up DEM {}".format(mytif))

            src_ds = gdal.Open(mytif)
            (x1, y1, trans, proj, data) = saa.read_gdal_file(src_ds)
            if src_ds is None:
                print('Unable to open %s' % mytif)
                sys.exit(1)

            srcband = src_ds.GetRasterBand(1)
            no_data = srcband.GetNoDataValue()

            print("noData value is {}".format(no_data))

            dem = mytif.replace(".tif", ".dem")
            par = dem + ".par"
            ps2dem(mytif, dem, par)

            tmp_name = mytif.replace(".tif", "_tmp.dem")
            cmd = "fill_gaps {in1} {width} {out} - - 1 100".format(in1=dem, width=x1, out=tmp_name)
            os.system(cmd)

            cmd = "data2geotiff {par} {in1} 2 {out}".format(par=par, in1=tmp_name, out=new_name)
            os.system(cmd)

            print("removing {} {} {}".format(dem, par, tmp_name))
            os.remove(dem)
            os.remove(par)
            os.remove(tmp_name)

    if build:
        cmd = "gdalbuildvrt full_area.vrt *_smooth.tif"
        os.system(cmd)

        cmd = "gdal_translate full_area.vrt full_area.tif"
        os.system(cmd)

        cmd = "ps2dem.py full_area.tif full_area.dem full_area.dem.par"
        os.system(cmd)

        logging.info("Finished creating output")
        return "full_area.dem", "full_area.dem.par"


def main():
    parser = argparse.ArgumentParser(prog="smooth_dem_tiles.py",
                                     description="Smooth REMA DEM tiles using fill_gaps")
    parser.add_argument("dir", help="Directory containing REMA DEMs to smooth")
    parser.add_argument("-n", help="Don't create full_area.dem output", action="store_false")
    args = parser.parse_args()

    logFile = "smooth_dem_tiles_{}.log".format(os.getpid())
    logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    smooth_dem_tiles(args.dir, build=args.n)


if __name__ == "__main__":
    main()

"""Convert a polar stereo GeoTIFF DEM into GAMMA's internal format"""

import argparse
import logging
import os
import warnings
from pathlib import Path
from typing import Union

import numpy as np
from osgeo import gdal, osr

import hyp3lib.saa_func_lib as saa
from hyp3lib.execute import execute
from hyp3lib.system import gamma_version


def ps2dem(in_dem: Union[str, Path], out_dem: str, dem_par: str):
    """
    Convert a polar stereo GeoTIFF DEM into GAMMA's internal format

    Args:
        in_dem: Polar stereographic DEM in GeoTIFF to be converted
        out_dem: Name of the output DEM in GAMMA's internal format
        dem_par: Name of the output DEM parameter file
    """
    dem_par_in = "dem_par.in"
    basename = os.path.basename(in_dem)

    logging.info("PS DEM in GEOTIFF format: {}".format(in_dem))
    logging.info("output DEM: {}".format(out_dem))
    logging.info("output DEM parameter file: {}".format(dem_par))

    xsize, ysize, trans, proj, data = saa.read_gdal_file(saa.open_gdal_file(in_dem))

    east = trans[0]
    north = trans[3]
    pix_east = trans[1]
    pix_north = trans[5]

    src_ds = gdal.Open(in_dem)

    prj = src_ds.GetProjection()

    srs = osr.SpatialReference(wkt=prj)

    lat_of_origin = srs.GetProjParm("latitude_of_origin")
    logging.info("latitude of origin {}".format(lat_of_origin))

    central_meridian = srs.GetProjParm("central_meridian")
    logging.info("central_meridian   {}".format(central_meridian))

    false_easting = srs.GetProjParm('false_easting')
    logging.info("false_easting      {}".format(false_easting))

    false_northing = srs.GetProjParm('false_northing')
    logging.info("false_northing     {}".format(false_northing))

    string = src_ds.GetMetadata()
    pixasarea = string["AREA_OR_POINT"]
    if "AREA" in pixasarea:
        logging.info("Pixel as Area! Updating corner coordinates to pixel as point")
        logging.info("pixel upper northing (m): {}    easting (m): {}".format(north, east))
        east = east + pix_east / 2.0
        north = north + pix_north / 2.0
        logging.info("Update pixel upper northing (m): {}    easting (m): {}".format(north, east))

    gamma_ver = gamma_version()
    if gamma_ver.startswith('2017'):
        warnings.warn('GAMMA versions prior to 2019 will not be supported in hyp3lib 2.0+',
                      DeprecationWarning, stacklevel=2)
        with open(dem_par_in, "w") as f:
            f.write("PS\n")
            f.write("WGS84\n")
            f.write("1\n")
            f.write(f"{lat_of_origin}\n")
            f.write(f"{central_meridian}\n")
            f.write(f"{basename}\n")
            f.write("REAL*4\n")
            f.write("0\n")
            f.write("1\n")
            f.write(f"{np.abs(xsize)}\n")
            f.write(f"{np.abs(ysize)}\n")
            f.write(f"{pix_north} {pix_east}\n")
            f.write(f"{north} {east}\n")
    else:
        with open(dem_par_in, "w") as f:
            f.write("PS\n")
            f.write("WGS84\n")
            f.write("1\n")
            f.write("other\n")
            f.write(f"{srs.GetAttrValue('PROJECTION')}\n")
            f.write("0\n")
            f.write(f"{false_easting}\n")
            f.write(f"{false_northing}\n")
            f.write("1\n")
            f.write(f"{central_meridian}\n")
            f.write(f"{lat_of_origin}\n")
            f.write(f"{basename}\n")
            f.write("REAL*4\n")
            f.write("0\n")
            f.write("1\n")
            f.write(f"{np.abs(xsize)}\n")
            f.write(f"{np.abs(ysize)}\n")
            f.write(f"{pix_north} {pix_east}\n")
            f.write(f"{north} {east}\n")

    if os.path.isfile(dem_par):
        os.remove(dem_par)
    execute("create_dem_par {} < {}".format(dem_par, dem_par_in))
    os.remove(dem_par_in)

    # Since 0 is the invalid pixel sentinel for gamma software,
    # Replace 0 with 1, because zero in a DEM is assumed valid
    # Then, replace anything <= -32767 with 0
    # (but first remove NANs)
    srcband = src_ds.GetRasterBand(1)
    no_data = srcband.GetNoDataValue()

    data[np.isnan(data)] = 0.0001
    data[data == 0] = 1
    data[data <= no_data] = 0

    # Convert to ENVI (binary) format
    if data.dtype == np.float32:
        fdata = data
    else:
        # Convert to floating point
        fdata = data.astype(np.float32)
    fdata = fdata.byteswap()

    tmptif = "temporary_dem_file.tif"
    saa.write_gdal_file_float(tmptif, trans, proj, fdata)
    gdal.Translate(out_dem, tmptif, format="ENVI")
    os.remove(tmptif)
    os.remove(out_dem + ".aux.xml")
    filename, file_extension = os.path.splitext(out_dem)
    os.remove(out_dem.replace(file_extension, ".hdr"))


def main():
    """Main entrypoint"""

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description=__doc__,
    )
    parser.add_argument('ps_dem', help='name of GeoTIFF file (input)')
    parser.add_argument('dem', help='DEM data (output)')
    parser.add_argument('dempar', help='Gamma DEM parameter file (output)')

    log_file = "{}_{}_log.txt".format("ps2dem", os.getpid())
    logging.basicConfig(filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")
    args = parser.parse_args()

    if not os.path.exists(args.ps_dem):
        parser.error(f'GeoTIFF file {args.ps_dem} does not exist!')

    ps2dem(args.ps_dem, args.dem, args.dempar)


if __name__ == '__main__':
    main()

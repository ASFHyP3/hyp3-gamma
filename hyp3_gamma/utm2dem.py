"""Convert a geotiff DEM into GAMMA internal format"""

import argparse
import os

import numpy as np
from osgeo import gdal, osr, gdalconst

import hyp3lib.saa_func_lib as saa
from hyp3lib.execute import execute


def utm2dem(inDem,outDem,demPar,dataType="float"):
    demParIn = "dem_par.in"
    dataType = dataType.lower()
    basename = os.path.basename(inDem)
    logname = basename + "_utm_dem.log"
    log = open(logname,"w")

    print("UTM DEM in GEOTIFF format: {}".format(inDem))
    print("output DEM: {}".format(outDem))
    print("output DEM parameter file: {}".format(demPar))
    print("log file: {}".format(logname))

    (x,y,trans,proj,data) = saa.read_gdal_file(saa.open_gdal_file(inDem))

    xsize = x
    ysize = y
    east = trans[0]
    north = trans[3]
    pix_east = trans[1]
    pix_north = trans[5]

    ds=gdal.Open(inDem)
    prj=ds.GetProjection()
    s = prj.split("[")
    for t in s:
        if "false_northing" in t:
             u = t.split('"')
             v = u[2].split(",")
             w = v[1].split("]")
             false_north = w[0]
    print("found false_north {}".format(false_north))

    srs=osr.SpatialReference(wkt=prj)
    string = srs.GetAttrValue('projcs')
    t = string.split(" ")
    zone = t[5]
    print("Found zone string {} of length {}".format(zone, len(zone)))

    if len(zone) == 3:
        zone = zone[0:2]
    else:
        zone = zone[0]
    print("found zone {}".format(zone))

    src = gdal.Open(inDem, gdalconst.GA_ReadOnly)
    string = src.GetMetadata()
    pixasarea = string["AREA_OR_POINT"]
    if "AREA" in pixasarea:
        print("Pixel as Area! Updating corner coordinates to pixel as point")
        print("pixel upper northing (m): {}    easting (m): {}".format(north, east))
        east = east + pix_east / 2.0
        north = north + pix_north / 2.0
        print("Update pixel upper northing (m): {}    easting (m): {}".format(north, east))

    pix_size = pix_east
    print("approximate DEM latitude pixel spacing (m): {}".format(pix_size))

    # Create the input file for create_dem_par    
    f = open(demParIn,"w")
    f.write("UTM\n")
    f.write("WGS84\n")
    f.write("1\n")
    f.write("{}\n".format(zone))
    f.write("{}\n".format(false_north))
    f.write("{}\n".format(basename))
    if "float" in dataType:
        f.write("REAL*4\n")
    elif "int16" in dataType:
        f.write("INTEGER*2\n")
    f.write("0.0\n")
    f.write("1.0\n")
    f.write("{}\n".format(xsize))
    f.write("{}\n".format(ysize))
    f.write("{} {}\n".format(pix_north,pix_east))
    f.write("{} {}\n".format(north,east))
    f.close()

    # Create a new dem par file
    if os.path.isfile(demPar): 
        os.remove(demPar)
    execute("create_dem_par {} < {}".format(demPar,demParIn),logfile=log)

    # Replace 0 with 1; Replace anything <= -32767 with 0; byteswap
    data[data==0] = 1
    data[data<=-32767] = 0
    data = data.byteswap()

    # Convert to ENVI (binary) format
    tmptif = "temporary_dem_file.tif"
    if "float" in dataType:
        saa.write_gdal_file_float(tmptif,trans,proj,data.astype(np.float32))
    elif "int16" in dataType:
        saa.write_gdal_file(tmptif,trans,proj,data)
    gdal.Translate(outDem,tmptif,format="ENVI")
    os.remove(tmptif)
    os.remove(outDem + ".aux.xml")
    filename, file_extension = os.path.splitext(outDem)
    os.remove(outDem.replace(file_extension,".hdr"))


def main():
    """Main entrypoint"""

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description=__doc__,
    )
    parser.add_argument('utm_dem', help='name of GeoTIFF file (input)')
    parser.add_argument('dem', help='DEM data (output)')
    parser.add_argument('dempar', help='Gamma DEM parameter file (output)')
    parser.add_argument('-t', '--dataType', help='Desired output data type (float or int16)', default='float')
    args = parser.parse_args()

    if not os.path.exists(args.utm_dem):
        parser.error(f'GeoTIFF file {args.utm_dem} does not exist!')

    utm2dem(args.utm_dem, args.dem, args.dempar, args.dataType)


if __name__ == '__main__':
    main()

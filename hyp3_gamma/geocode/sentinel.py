"""Geocode a sentinel-1 granule using Gamma software"""

import argparse
import datetime
import glob
import logging
import math
import os
import shutil
import zipfile

import numpy as np
from hyp3lib.asf_geometry import geometry_geo2proj
from hyp3lib.byteSigmaScale import byteSigmaScale
from hyp3lib.createAmp import createAmp
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from hyp3lib.getSubSwath import get_bounding_box_file
from hyp3lib.ingest_S1_granule import ingest_S1_granule
from hyp3lib.makeAsfBrowse import makeAsfBrowse
from hyp3lib.make_arc_thumb import pngtothumb

from hyp3_geocode import __version__



def create_dem_par(basename, data_type, pixel_size, lat_max, lat_min, lon_max, lon_min, post):
    dem_par_in = "{}_dem_par.in".format(basename)
    zone, false_north, y_min, y_max, x_min, x_max = geometry_geo2proj(lat_max, lat_min, lon_max, lon_min)

    logging.debug("Original Output Coordinates: {} {} {} {}".format(y_min, y_max, x_min, x_max))

    if post is not None:
        shift = 0
        x_max = math.ceil(x_max / post) * post + shift
        x_min = math.floor(x_min / post) * post - shift
        y_max = math.ceil(y_max / post) * post + shift
        y_min = math.floor(y_min / post) * post - shift
        logging.debug("Snapped Output Coordinates: {} {} {} {}".format(y_min, y_max, x_min, x_max))

    with open(dem_par_in, "w") as f:
        f.write("UTM\n")
        f.write("WGS84\n")
        f.write("1\n")
        f.write("{}\n".format(zone))
        f.write("{}\n".format(false_north))
        f.write("{}\n".format(basename))
        if "float" in data_type:
            f.write("REAL*4\n")
        elif "int16" in data_type:
            f.write("INTEGER*2\n")
        f.write("0.0\n")
        f.write("1.0\n")

        xsize = np.floor(abs((x_max - x_min) / pixel_size))
        ysize = np.floor(abs((y_max - y_min) / pixel_size))

        f.write("{}\n".format(int(xsize)))
        f.write("{}\n".format(int(ysize)))
        f.write("{} {}\n".format(-1.0 * pixel_size, pixel_size))
        f.write("{} {}\n".format(y_max, x_min))

    return dem_par_in


def blank_bad_data(raw_file, x, y, left=15, right=15):
    # Read in the data
    data = np.fromfile(raw_file, dtype=np.float32)
    data = np.reshape(data, (y, x))
    data = data.byteswap()

    # For each line in the file
    for i in range(y):
        # Black out the start of the line
        for j in range(x):
            if data[i, j] != 0:
                data[i, :j + left] = 0
                break
        # Black out the end of the line
        for j in range(x - 1, 0, -1):
            if data[i, j] != 0:
                data[i, j - right:] = 0
                break

    # Write out the data
    data = data.byteswap()
    data.tofile(raw_file)


def process_pol(pol, type_, infile, outfile, pixel_size, height, make_tab_flag=True, gamma0_flag=False,
                offset=None):
    logging.info(f"Processing the {pol} polarization")
    # FIXME: make_tab_flag isn't used... should it be doing something?
    logging.debug(f'Unused option make_tab_flag was {make_tab_flag}')

    mgrd = f"{outfile}.{pol}.mgrd"
    utm = f"{outfile}.{pol}.utm"
    area_map = f"{outfile}_area_map.par"
    small_map = f"{outfile}_small_map"

    look_fact = np.floor((pixel_size / 10.0) + 0.5)
    if look_fact < 1:
        look_fact = 1

    # Ingest the granule into gamma format
    ingest_S1_granule(infile, pol, look_fact, mgrd)

    if gamma0_flag:
        # Convert sigma-0 to gamma-0
        cmd = f"radcal_MLI {mgrd} {mgrd}.par - {mgrd}.sigma - 0 0 -1"
        execute(cmd, uselogging=True)
        cmd = f"radcal_MLI {mgrd}.sigma {mgrd}.par - {mgrd}.gamma - 0 0 2"
        execute(cmd, uselogging=True)
        shutil.move(f"{mgrd}.gamma", mgrd)

    # Blank out the bad data at the left and right edges
    dsx = int(getParameter(f"{mgrd}.par", "range_samples", uselogging=True))
    dsy = int(getParameter(f"{mgrd}.par", "azimuth_lines", uselogging=True))

    if "GRD" in type_:
        blank_bad_data(mgrd, dsx, dsy, left=20, right=20)

    # Create geocoding look up table
    if offset:
        cmd = f"gec_map {mgrd}.par {offset} {area_map} {height} {small_map}.par {small_map}.utm_to_rdc"
    else:
        cmd = f"gec_map {mgrd}.par - {area_map} {height} {small_map}.par {small_map}.utm_to_rdc"
    execute(cmd, uselogging=True)

    # Gecode the granule
    out_size = getParameter(f"{small_map}.par", "width", uselogging=True)
    cmd = f"geocode_back {mgrd} {dsx} {small_map}.utm_to_rdc {utm} {out_size}"
    execute(cmd, uselogging=True)

    # Create the geotiff file
    tiffile = f"{outfile}_{pol}.tif"
    cmd = f"data2geotiff {small_map}.par {utm} 2 {tiffile}"
    execute(cmd, uselogging=True)


def create_xml_files(infile, outfile, height, type_, gamma0_flag, pixel_size):
    """Create XML metadata files"""
    cfgdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "config"))
    back = os.getcwd()
    os.chdir("PRODUCT")
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d")
    time = now.strftime("%H%M%S")
    dt = now.strftime("%Y-%m-%dT%H:%M:%S")
    year = now.year
    encoded_jpg = pngtothumb("{}.png".format(outfile))
    basename = os.path.basename(infile)
    granulename = os.path.splitext(basename)[0]

    if type_ == "SLC":
        full_type = "Single-Look Complex"
    else:
        full_type = "Ground Range Detected"

    if gamma0_flag:
        power_type = "gamma"
    else:
        power_type = "sigma"

    for myfile in glob.glob("*.tif"):
        with open(f"{cfgdir}/GeocodingTemplate.xml", "r") as f:
            with open(f"{myfile}.xml", "w") as g:
                if "vv" in myfile:
                    pol = "vv"
                elif "vh" in myfile:
                    pol = "vh"
                elif "hh" in myfile:
                    pol = "hh"
                elif "hv" in myfile:
                    pol = "hv"

                for line in f:
                    line = line.replace("[DATE]", date)
                    line = line.replace("[TIME]", "{}00".format(time))
                    line = line.replace("[DATETIME]", dt)
                    line = line.replace("[HEIGHT]", "{}".format(height))
                    line = line.replace("[YEARPROCESSED]", "{}".format(year))
                    line = line.replace("[YEARACQUIRED]", infile[17:21])
                    line = line.replace("[TYPE]", type_)
                    line = line.replace("[FULL_TYPE]", full_type)
                    line = line.replace("[SPACING]", "{}".format(int(pixel_size)))
                    line = line.replace("[THUMBNAIL_BINARY_STRING]", encoded_jpg)
                    line = line.replace("[POL]", pol)
                    line = line.replace("[POWERTYPE]", power_type)
                    line = line.replace("[GRAN_NAME]", granulename)
                    line = line.replace("[FORMAT]", "power")
                    g.write(f"{line}\n")

    for myfile in glob.glob("*.png"):
        if "rgb" in myfile:
            scale = 'color'
            encoded_jpg = pngtothumb("{}_rgb.png".format(outfile))
        else:
            scale = 'grayscale'
            encoded_jpg = pngtothumb("{}.png".format(outfile))

        if "large" in myfile:
            res = "medium"
        else:
            res = "low"

        with open(f"{cfgdir}/GeocodingTemplate_{scale}_png.xml", "r") as f:
            with open(f"{myfile}.xml", "w") as g:
                for line in f:
                    line = line.replace("[DATE]", date)
                    line = line.replace("[TIME]", "{}00".format(time))
                    line = line.replace("[DATETIME]", dt)
                    line = line.replace("[YEARPROCESSED]", "{}".format(year))
                    line = line.replace("[YEARACQUIRED]", infile[17:21])
                    line = line.replace("[TYPE]", type_)
                    line = line.replace("[FULL_TYPE]", full_type)
                    line = line.replace("[THUMBNAIL_BINARY_STRING]", encoded_jpg)
                    line = line.replace("[RES]", res)
                    line = line.replace("[GRAN_NAME]", granulename)
                    line = line.replace("[FORMAT]", "power")
                    g.write(f"{line}\n")

    os.chdir(back)


def make_products(outfile, pol, cp=None):
    # Create greyscale geotiff and ASF browse images
    tiffile = "{out}_{pol}.tif".format(out=outfile, pol=pol)
    ampfile = createAmp(tiffile, nodata=0)
    newfile = ampfile.replace(".tif", "_sigma.tif")
    byteSigmaScale(ampfile, newfile)
    makeAsfBrowse(newfile, outfile)
    os.remove(newfile)

    # Create color ASF browse images
    if cp is not None:
        if pol == "vv":
            basename = "{}_vh".format(outfile)
        else:
            basename = "{}_hv".format(outfile)
        tiffile2 = "{}.tif".format(basename)
        ampfile2 = createAmp(tiffile2, nodata=0)
        outfile2 = ampfile2.replace(".tif", "_rgb.tif")
        threshold = -24

        # Direct call to rtc2color overran the memory (128 GB)
        #        rtc2color(ampfile,ampfile2, threshold, outfile2, amp=True, cleanup=True)
        # Trying this instead
        cmd = "rtc2color.py -amp -cleanup {fp} {cp} {th} {out}".format(fp=ampfile, cp=ampfile2, th=threshold,
                                                                       out=outfile2)
        execute(cmd, uselogging=True)

        colorname = "{}_rgb".format(outfile)
        makeAsfBrowse(outfile2, colorname)
        os.remove(ampfile2)
        os.remove(outfile2)

    os.remove(ampfile)

    # Move results to the PRODUCT directory
    if not os.path.isdir("PRODUCT"):
        os.mkdir("PRODUCT")
    for tiffile in glob.glob("*.tif"):
        shutil.move(tiffile, "PRODUCT")
    for txtfile in glob.glob("*_log.txt"):
        shutil.move(txtfile, "PRODUCT")
    for pngfile in glob.glob("*.png*"):
        shutil.move(pngfile, "PRODUCT")
    for kmzfile in glob.glob("*.kmz"):
        shutil.move(kmzfile, "PRODUCT")


def geocode_sentinel(infile, outfile, pixel_size=30.0, height=0, gamma0_flag=False, post=None,
                     offset=None):
    if not os.path.exists(infile):
        logging.error("ERROR: Input file {} does not exist".format(infile))
        exit(1)
    if "zip" in infile:
        zip_ref = zipfile.ZipFile(infile, 'r')
        zip_ref.extractall(".")
        zip_ref.close()
        infile = infile.replace(".zip", ".SAFE")

    type_ = 'GRD' if 'GRD' in infile else 'SLC'

    # Create par file covering the area we want to geocode
    lat_max, lat_min, lon_max, lon_min = get_bounding_box_file(infile)
    logging.debug("Input Coordinates: {} {} {} {}".format(lat_max, lat_min, lon_max, lon_min))
    area_map = "{}_area_map".format(outfile)
    demParIn = create_dem_par(area_map, "float", pixel_size, lat_max, lat_min, lon_max, lon_min, post)
    execute("create_dem_par {}.par < {}".format(area_map, demParIn), uselogging=True)

    # Get list of files to process
    vvlist = glob.glob("{}/*/*vv*.tiff".format(infile))
    vhlist = glob.glob("{}/*/*vh*.tiff".format(infile))
    hhlist = glob.glob("{}/*/*hh*.tiff".format(infile))
    hvlist = glob.glob("{}/*/*hv*.tiff".format(infile))

    pol = None
    cross_pol = None
    if vvlist:
        pol = "vv"
        process_pol(pol, type_, infile, outfile, pixel_size, height, make_tab_flag=True, gamma0_flag=gamma0_flag,
                    offset=offset)
        if vhlist:
            process_pol("vh", type_, infile, outfile, pixel_size, height, make_tab_flag=False, gamma0_flag=gamma0_flag,
                        offset=offset)
            cross_pol = "vh"
    if hhlist:
        pol = "hh"
        process_pol(pol, type_, infile, outfile, pixel_size, height, make_tab_flag=True, gamma0_flag=gamma0_flag,
                    offset=offset)
        if hvlist:
            process_pol("hv", type_, infile, outfile, pixel_size, height, make_tab_flag=False, gamma0_flag=gamma0_flag,
                        offset=offset)
            cross_pol = "hv"

    make_products(outfile, pol, cp=cross_pol)
    create_xml_files(infile, outfile, height, type_, gamma0_flag, pixel_size)


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='geocode_sentinel.py',
        description=__doc__,
    )
    parser.add_argument("infile",
                        help="Input zip file or SAFE directory")
    parser.add_argument("outfile",
                        help="Name of output geocoded file")
    parser.add_argument("-t", "--terrain_height", type=float, default=0.0,
                        help="Average terrain height for geocoding")
    parser.add_argument("-s", "--pixel_size", type=float, default=30.0,
                        help="Pixel size for output product (default 30m)")
    parser.add_argument("-p", "--post", type=float,
                        help="Pixel posting for output product")
    parser.add_argument("-g", "--gamma0", action="store_true",
                        help="Make output gamma0 instead of sigma0")
    parser.add_argument("-o", "--offset",
                        help="Optional offset file to use during geocoding")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    log_file = f"{args.outfile}_{os.getpid()}_log.txt"
    logging.basicConfig(
        filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
    )
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    geocode_sentinel(
        args.infile, args.outfile, height=args.terrain_height, pixel_size=args.pixel_size,
        gamma0_flag=args.gamma0, post=args.post, offset=args.offset
    )


if __name__ == "__main__":
    main()

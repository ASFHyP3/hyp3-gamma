"""Unwrap and geocode Sentinel-1 INSAR products from GAMMA"""

import argparse
import logging
import os

import numpy as np
from PIL import Image
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from osgeo import gdal

from hyp3_gamma.water_mask import create_water_mask

log = logging.getLogger(__name__)


def get_minimum_value_for_gamma_dtype(dtype):
    """Get the minimum numeric value for a GAMMA data type

    GAMMA provides these data types:
    * 0: RASTER 8 or 24 bit uncompressed raster image, SUN (`*.ras`), BMP:(`*.bmp`), or TIFF: (`*.tif`)
    * 1: SHORT integer (2 bytes/value)
    * 2: FLOAT (4 bytes/value)
    * 3: SCOMPLEX (short complex, 4 bytes/value)
    * 4: FCOMPLEX (float complex, 8 bytes/value)
    * 5: BYTE
    """
    dtype_map = {
        0: np.int8,
        1: np.int16,
        2: np.float32,
        3: np.float32,
        4: np.float64,
        5: np.int8,
    }
    try:
        return np.iinfo(dtype_map[dtype]).min
    except ValueError:
        return np.finfo(dtype_map[dtype]).min
    except KeyError:
        raise ValueError(f'Unknown GAMMA data type: {dtype}')


def setnodata(file, nodata):
    """
    The output geotiff files produced by gamma package always has 0.0 as nodata value.
    This function changes the nodata value in the geotiff file.

    """
    ds = gdal.Open(file, gdal.GA_Update)
    for i in range(1, ds.RasterCount + 1):
        band = ds.GetRasterBand(i)
        band_data = band.ReadAsArray()
        mask = band.GetMaskBand()
        mask_data = mask.ReadAsArray()
        band_data[mask_data == 0] = nodata
        band.WriteArray(band_data)
        band.SetNoDataValue(float(nodata))
    del ds


def geocode_back(inname, outname, width, lt, demw, demn, type_):
    execute(f"geocode_back {inname} {width} {lt} {outname} {demw} {demn} 0 {type_}", uselogging=True)


def geocode(inname, outname, inwidth, lt, outwidth, outlines, type_):
    execute(f"geocode {lt} {inname} {inwidth} {outname} {outwidth} {outlines} - {type_}", uselogging=True)


def data2geotiff(inname, outname, dempar, type_):
    execute(f"data2geotiff {dempar} {inname} {type_} {outname} ", uselogging=True)
    nodata = get_minimum_value_for_gamma_dtype(type_)
    setnodata(outname, nodata)


def create_phase_from_complex(incpx, outfloat, width):
    execute(f"cpx_to_real {incpx} {outfloat} {width} 4", uselogging=True)


def get_water_mask(cc_mask_file, mwidth, lt, demw, demn, dempar):
    """
    createwater_mask based on the cc_mask_file
    """
    tmp_mask = 'tmp_mask'
    os.system('cp {} {}.bmp'.format(cc_mask_file, tmp_mask))
    # 2--bmp
    geocode_back("{}.bmp".format(tmp_mask), "{}_geo.bmp".format(tmp_mask), mwidth, lt, demw, demn, 2)
    # 0--bmp
    data2geotiff("{}_geo.bmp".format(tmp_mask), "{}_geo.tif".format(tmp_mask), dempar, 0)
    # create water_mask.tif file
    create_water_mask("{}_geo.tif".format(tmp_mask), 'water_mask.tif')
    ds = gdal.Open('water_mask.tif')
    band = ds.GetRasterBand(1)
    mask = band.ReadAsArray()
    del ds
    return mask


def combine_water_mask(cc_mask_file, mwidth, mlines, lt, demw, demn, dempar):
    """combine cc_mask with water_mask
    """
    # read the original mask file
    in_im = Image.open(cc_mask_file)
    in_data = np.array(in_im)
    in_palette = in_im.getpalette()

    # get mask data and save it into the water_mask.bmp file
    mask = get_water_mask(cc_mask_file, mwidth, lt, demw, demn, dempar)
    water_im = Image.fromarray(mask)
    water_im.putpalette(in_palette)
    water_bmp_file = os.path.join(os.path.dirname(cc_mask_file), "water_mask.bmp")
    water_im.save(water_bmp_file)

    # map water_mask.bmp file to SAR coordinators
    water_mask_bmp_sar_file = os.path.join(os.path.dirname(cc_mask_file), "water_mask_sar.bmp")
    geocode(water_bmp_file, water_mask_bmp_sar_file, demw, lt, mwidth, mlines, 2)

    # read water_mask_bmp_sar_file
    water_mask_sar_im = Image.open(water_mask_bmp_sar_file)
    water_mask_sar_data = np.array(water_mask_sar_im)

    # combine two masks and output combined_mask.bmp
    in_data[water_mask_sar_data == 0] = 0
    out_im = Image.fromarray(in_data)
    out_im.putpalette(in_palette)
    out_file = os.path.join(os.path.dirname(cc_mask_file), "combined_mask.bmp")
    out_im.save(out_file)

    return out_file


def unwrapping_geocoding(reference, secondary, step="man", rlooks=10, alooks=2, trimode=0,
                         npatr=1, npata=1, alpha=0.6, water_masking=False):
    dem = "./DEM/demseg"
    dempar = "./DEM/demseg.par"
    lt = "./DEM/MAP2RDC"
    ifgname = "{}_{}".format(reference, secondary)
    offit = "{}.off.it".format(ifgname)
    mmli = reference + ".mli"
    smli = secondary + ".mli"

    if not os.path.isfile(dempar):
        log.error("ERROR: Unable to find dem par file {}".format(dempar))

    if not os.path.isfile(lt):
        log.error("ERROR: Unable to find look up table file {}".format(lt))

    if not os.path.isfile(offit):
        log.error("ERROR: Unable to find offset file {}".format(offit))

    width = getParameter(offit, "interferogram_width")
    mwidth = getParameter(mmli + ".par", "range_samples")
    mlines = getParameter(mmli + ".par", "azimuth_lines")
    swidth = getParameter(smli + ".par", "range_samples")
    demw = getParameter(dempar, "width")
    demn = getParameter(dempar, "nlines")

    ifgf = "{}.diff0.{}".format(ifgname, step)

    log.info("{} will be used for unwrapping and geocoding".format(ifgf))

    log.info("-------------------------------------------------")
    log.info("            Start unwrapping")
    log.info("-------------------------------------------------")

    execute(f"cc_wave {ifgf} {mmli} - {ifgname}.cc {width}", uselogging=True)

    execute(f"rascc {ifgname}.cc {mmli} {width} 1 1 0 1 1 .1 .9"
            f" - - - {ifgname}.cc.ras", uselogging=True)

    execute(f"adf {ifgf} {ifgf}.adf {ifgname}.adf.cc {width} {alpha} - 5", uselogging=True)

    execute(f"rasmph_pwr {ifgf}.adf {mmli} {width}", uselogging=True)

    execute(f"rascc {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 .1 .9"
            f" - - - {ifgname}.adf.cc.ras", uselogging=True)

    execute(f"rascc_mask {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 0.10 0.20 ", uselogging=True)

    if water_masking:
        # create and apply water mask
        out_file = combine_water_mask(f'{ifgname}.adf.cc_mask.bmp', mwidth, mlines, lt,
                                            demw, demn, dempar)
        execute(f"mcf {ifgf}.adf {ifgname}.adf.cc {out_file} {ifgname}.adf.unw {width} {trimode} 0 0"
                f" - - {npatr} {npata}", uselogging=True)
    else:
        # create water mask only
        _ = get_water_mask(f'{ifgname}.adf.cc_mask.bmp', mwidth, lt, demw, demn, dempar)
        execute(f"mcf {ifgf}.adf {ifgname}.adf.cc {ifgname}.adf.cc_mask.bmp {ifgname}.adf.unw {width} {trimode} 0 0"
                f" - - {npatr} {npata}", uselogging=True)

    execute(f"rasrmg {ifgname}.adf.unw {mmli} {width} 1 1 0 1 1 0.33333 1.0 .35 0.0"
            f" - {ifgname}.adf.unw.ras", uselogging=True)

    execute(f"dispmap {ifgname}.adf.unw DEM/HGT_SAR_{rlooks}_{alooks} {mmli}.par"
            f" - {ifgname}.vert.disp 1", uselogging=True)

    execute(f"rashgt {ifgname}.vert.disp - {width} 1 1 0 1 1 0.028", uselogging=True)

    execute(f"dispmap {ifgname}.adf.unw DEM/HGT_SAR_{rlooks}_{alooks} {mmli}.par"
            f" - {ifgname}.los.disp 0", uselogging=True)

    execute(f"rashgt {ifgname}.los.disp - {width} 1 1 0 1 1 0.028", uselogging=True)

    execute(f"gc_map2 {mmli}.par DEM/demseg.par 0 - - - - - - - inc_ell")

    log.info("-------------------------------------------------")
    log.info("            End unwrapping")
    log.info("-------------------------------------------------")

    log.info("-------------------------------------------------")
    log.info("            Start geocoding")
    log.info("-------------------------------------------------")

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

    create_phase_from_complex("{}.adf.geo".format(ifgf), "{}.adf.geo.phase".format(ifgf), width)

    data2geotiff(mmli + ".geo", mmli + ".geo.tif", dempar, 2)
    data2geotiff(smli + ".geo", smli + ".geo.tif", dempar, 2)
    data2geotiff("{}.sim_unw.geo".format(ifgname), "{}.sim_unw.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.adf.unw.geo".format(ifgname), "{}.adf.unw.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.adf.unw.geo.bmp".format(ifgname), "{}.adf.unw.geo.bmp.tif".format(ifgname), dempar, 0)
    data2geotiff("{}.adf.geo.phase".format(ifgf), "{}.adf.geo.tif".format(ifgf), dempar, 2)
    data2geotiff("{}.adf.bmp.geo".format(ifgf), "{}.adf.bmp.geo.tif".format(ifgf), dempar, 0)
    data2geotiff("{}.cc.geo".format(ifgname), "{}.cc.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.adf.cc.geo".format(ifgname), "{}.adf.cc.geo.tif".format(ifgname), dempar, 2)
    data2geotiff("DEM/demseg", "{}.dem.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.vert.disp.bmp.geo".format(ifgname), "{}.vert.disp.geo.tif".format(ifgname), dempar, 0)
    data2geotiff("{}.vert.disp.geo".format(ifgname), "{}.vert.disp.geo.org.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.los.disp.bmp.geo".format(ifgname), "{}.los.disp.geo.tif".format(ifgname), dempar, 0)
    data2geotiff("{}.los.disp.geo".format(ifgname), "{}.los.disp.geo.org.tif".format(ifgname), dempar, 2)
    data2geotiff("DEM/inc", "{}.inc.tif".format(ifgname), dempar, 2)
    data2geotiff("inc_ell", "{}.inc_ell.tif".format(ifgname), dempar, 2)
    execute(f"look_vector {mmli}.par {offit} {dempar} {dem} lv_theta lv_phi", uselogging=True)

    data2geotiff("lv_theta", "{}.lv_theta.tif".format(ifgname), dempar, 2)
    data2geotiff("lv_phi", "{}.lv_phi.tif".format(ifgname), dempar, 2)

    log.info("-------------------------------------------------")
    log.info("            End geocoding")
    log.info("-------------------------------------------------")


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='unwrapping_geocoding.py',
        description=__doc__,
    )
    parser.add_argument("reference", help='Reference scene identifier')
    parser.add_argument("secondary", help='Secondary scene identifier')
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

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    unwrapping_geocoding(args.reference, args.secondary, step=args.step, rlooks=args.rlooks, alooks=args.alooks,
                         trimode=args.tri, npatr=args.npatr, npata=args.npata, alpha=args.alpha)


if __name__ == "__main__":
    main()

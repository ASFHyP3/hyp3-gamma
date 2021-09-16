"""Unwrap and geocode Sentinel-1 INSAR products from GAMMA"""

import argparse
import logging
import subprocess
import os
from tempfile import TemporaryDirectory

import pyproj
import numpy as np
from PIL import Image
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from osgeo import gdal

from hyp3_gamma.water_mask import create_water_mask

log = logging.getLogger(__name__)


def get_first_valid_mask_pixel(inname):
    """
    input: validity mask file in bmp format
    return: ref_i, ref_j
    """
    im = Image.open(inname)
    data = np.asarray(im)
    idx = np.where(data > 0)
    ref_i, ref_j = idx[0][0], idx[1][0]
    return ref_i, ref_j


def get_valid_mask_pixel(inname):
    im = Image.open(inname)
    data = np.asarray(im)
    rows, cols = data.shape
    thr_val = 0.5*data.max()
    ref_i = 0
    ref_j = 0
    breaker = False
    for i in range(1, rows-2):
        for j in range(1, cols-2):
            # five points
            points = np.array([data[i, j-1], data[i, j], data[i, j+1], data[i-1, j], data[i+1, j]])
            # nine points
            points = np.array([data[i-1, j-1], data[i-1, j], data[i-1, j+1],
                               data[i, j-1], data[i, j], data[i, j+1],
                               data[i+1, j-1], data[i+1, j], data[i+1, j+1]])
            if np.all(points > thr_val):
                ref_i = i
                ref_j = j
                breaker = True
                break
        if breaker:
            break
    return ref_i, ref_j


def ij2coord(gt, x_pixel, y_line):
    x = gt[0] + x_pixel * gt[1] + y_line * gt[2]
    y = gt[3] + x_pixel * gt[4] + y_line * gt[5]
    return x, y


def projcoord2lonlat(dataset, x, y):
    """
    covert x,y of dataset's projected coord to longitude and latitude
    """
    dst = dataset.GetSpatialRef()
    dstproj4 = dst.ExportToProj4()
    ct2 = pyproj.Proj(dstproj4)
    lon, lat = ct2(x, y, inverse=True)
    return lon, lat


def convert_coord_from_sar_map(inname, dempar, width, lt, demw, demn, ref_i, ref_j):
    """
    inputs: inname--mask file in bmp format
            row -i, col-j in SAR space, get its related row and col in map space
    """
    im = Image.open(inname)
    data = np.asarray(im)
    data[:, :] = 0
    data[ref_i, ref_j] = 1
    outfile = "tmp_mask.bmp"
    im_out = Image.fromarray(data)
    im_out.save(outfile)
    # convert tmp_mask.bmp from SAR
    geocode_back("tmp_mask.bmp", "tmp_mask.geo.bmp", width, lt, demw, demn, 2)
    data2geotiff("tmp_mask.geo.bmp", "tmp_mask.geo.bmp.tif", dempar, 0)
    # im_map = Image.open("tmp_mask.geo.bmp")
    # data_map = np.asarray(im_map)
    # (row, col) = np.where(data_map == 1)

    ds =gdal.Open("tmp_mask.geo.bmp.tif")
    gt = ds.GetGeoTransform()
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    (row, col) = np.where(data == 1)
    y_line = row[0]
    x_pixel = col[0]
    x, y = ij2coord(gt, x_pixel, y_line)
    lon, lat = projcoord2lonlat(ds, x, y)
    del ds
    coords={"row_s": ref_i, "col_s": ref_j, "row_m": y_line, "col_m": x_pixel, "y": y, "x": x, "lat": lat, "lon": lon}

    return coords


def get_coords(in_mli_par, ref_azlin, ref_rpix, in_dem_par=None):

    """
    inputs: mil.par, dempar, reference point  in SAR space (ref_azlin, ref_rpix)
    returns: coords={"row_s":row_s,"col_s":col_s,"row_m":row_m,"col_m":col_m,"x":x,"y":y,"lat":lat,"lon":lon}
    """

    def _coord_lst(cmd):

        coord_txt = subprocess.run(cmd, capture_output=True, text=True)

        lst = coord_txt.stdout.split('\n')

        coord_str = [s for s in lst if "selected" in s]

        coord_lst = ' '.join(coord_str[0].split()).split(" ")[: -1]

        coord_lst = [float(s) for s in coord_lst]

        return coord_lst

    cmd = ['sarpix_coord', in_mli_par, '-']
    coord = {}
    if in_dem_par:
        cmd1 = cmd.copy()
        cmd1.extend([in_dem_par])
        cmd1.extend([str(ref_azlin), str(ref_rpix)])
        coord_lst = _coord_lst(cmd1)
        coord["row_s"], coord["col_s"], coord["row_m"], coord["col_m"], coord["y"], coord["x"] = \
            coord_lst[0], coord_lst[1], coord_lst[2], coord_lst[3], coord_lst[4], coord_lst[5]

        cmd2 = cmd.copy()
        cmd2.extend(['-'])
        cmd2.extend([str(ref_azlin), str(ref_rpix)])
        coord_lst = _coord_lst(cmd2)
        coord["lat"], coord["lon"] = coord_lst[2], coord_lst[3]
    else:
        cmd.extend(['-'])
        cmd.extend([str(ref_azlin), str(ref_rpix)])
        coord_lst = _coord_lst(cmd)
        coord["row_s"], coord["col_s"], coord["row_m"], coord["col_m"], coord["y"], coord["x"] = \
            coord_lst[0], coord_lst[1], None, None, None, None
        coord["lat"], coord["lon"] = coord_lst[2], coord_lst[3]

    return coord


def geocode_back(inname, outname, width, lt, demw, demn, type_):
    execute(f"geocode_back {inname} {width} {lt} {outname} {demw} {demn} 0 {type_}", uselogging=True)


def geocode(inname, outname, inwidth, lt, outwidth, outlines, type_):
    execute(f"geocode {lt} {inname} {inwidth} {outname} {outwidth} {outlines} - {type_}", uselogging=True)


def data2geotiff(inname, outname, dempar, type_):
    execute(f"data2geotiff {dempar} {inname} {type_} {outname} ", uselogging=True)


def create_phase_from_complex(incpx, outfloat, width):
    execute(f"cpx_to_real {incpx} {outfloat} {width} 4", uselogging=True)


def get_first_valid_unw_pixel(adf, adf_cc, adf_cc_mask, adf_unw, dempar, width, lines, lt, demw, demn):
    execute(f"mcf {adf} {adf_cc} {adf_cc_mask} {adf_unw} {width} 0 0 0"
            f" - - 1 1 - 0 0 0", uselogging=True)
    geocode_back(adf_unw, "adf_unw_geo", width, lt, demw, demn, 0)
    data2geotiff("adf_unw_geo", "adf_unw_geo.tif", dempar, 2)
    # read the bmp file
    ds = gdal.Open("adf_unw_geo.tif")
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    mskband = band.GetMaskBand()
    mskdata = mskband.ReadAsArray()

    #im = Image.open("adf_unw_geo.bmp")
    #data = np.asarray(im)
    ch = (data > 0) & (mskdata == 255)
    idx = np.where(ch == True)
    ref_i, ref_j = idx[0][-1], idx[1][-1]
    ref_val = data[ref_i, ref_j]
    data[:, :] = 0
    data[ref_i, ref_j] = 1
    outfile = "tmp_unw_geo.bmp"
    im_out = Image.fromarray(data)
    im_out = im_out.convert('L')
    im_out.save(outfile)

    geocode("tmp_unw_geo.bmp", "tmp_unw_sar.bmp", demw, lt, width, lines, 2)
    im = Image.open("tmp_unw_sar.bmp")
    data = np.asarray(im)
    idx = np.where(data == 1)
    ref_azlin, ref_rpix = idx[0][0], idx[1][0]

    return ref_azlin, ref_rpix


def get_water_mask(cc_mask_file, mwidth, lt, demw, demn, dempar):
    """
    create water_mask based on the cc_mask_file
    """
    with TemporaryDirectory() as temp_dir:
        os.system(f'cp {cc_mask_file} {temp_dir}/tmp_mask.bmp')
        # 2--bmp
        geocode_back(f'{temp_dir}/tmp_mask.bmp', f'{temp_dir}/tmp_mask_geo.bmp', mwidth, lt, demw, demn, 2)
        # 0--bmp
        data2geotiff(f'{temp_dir}/tmp_mask_geo.bmp', f'{temp_dir}/tmp_mask_geo.tif', dempar, 0)
        # create water_mask.tif file
        create_water_mask(f'{temp_dir}/tmp_mask_geo.tif', 'water_mask.tif')
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

    with TemporaryDirectory() as temp_dir:
        # get mask data and save it into the water_mask.bmp file
        mask = get_water_mask(cc_mask_file, mwidth, lt, demw, demn, dempar)
        water_im = Image.fromarray(mask)
        water_im.putpalette(in_palette)
        water_bmp_file = f'{temp_dir}/water_mask.bmp'
        water_im.save(water_bmp_file)

        # map water_mask.bmp file to SAR coordinators
        water_mask_bmp_sar_file = f'{temp_dir}/water_mask_sar.bmp'
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
                         npatr=1, npata=1, alpha=0.6, apply_water_mask=False):

    dem = "./DEM/demseg"
    dempar = "./DEM/demseg.par"
    lt = "./DEM/MAP2RDC"
    ifgname = "{}_{}".format(reference, secondary)
    offit = "{}.off.it".format(ifgname)
    mmli = reference + ".mli"
    smli = secondary + ".mli"
    ref_azlin = 0
    ref_rpix = 0


    if not os.path.isfile(dempar):
        log.error("ERROR: Unable to find dem par file {}".format(dempar))

    if not os.path.isfile(lt):
        log.error("ERROR: Unable to find look up table file {}".format(lt))

    if not os.path.isfile(offit):
        log.error("ERROR: Unable to find offset file {}".format(offit))

    width = getParameter(offit, "interferogram_width")
    lines = getParameter(offit, "interferogram_azimuth_lines")
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

    execute(f"adf {ifgf} {ifgf}.adf {ifgname}.adf.cc {width} {alpha} - 5", uselogging=True)

    execute(f"rasmph_pwr {ifgf}.adf {mmli} {width}", uselogging=True)

    execute(f"rascc_mask {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 0.10 0.20 ", uselogging=True)

    ref_azlin, ref_rpix = get_first_valid_mask_pixel(f"{ifgname}.adf.cc_mask.bmp")

    ref_azlin, ref_rpix = get_valid_mask_pixel(f"{ifgname}.adf.cc_mask.bmp")

    # ref_azlin, ref_rpix = get_first_valid_unw_pixel(f"{ifgf}.adf", f"{ifgname}.adf.cc", f"{ifgname}.adf.cc_mask.bmp",
    #                                                f"adf_unw", dempar, width, lines, lt, demw, demn)

    coords = get_coords(f"{mmli}.par", ref_azlin, ref_rpix, dempar)

    # coords = convert_coord_from_sar_map(f"{ifgname}.adf.cc_mask.bmp", dempar, width, lt,
    #                                    demw, demn, ref_azlin, ref_rpix)
    if apply_water_mask:
        # create and apply water mask
        out_file = combine_water_mask(f'{ifgname}.adf.cc_mask.bmp', mwidth, mlines, lt, demw, demn, dempar)
        execute(f"mcf {ifgf}.adf {ifgname}.adf.cc {out_file} {ifgname}.adf.unw {width} {trimode} 0 0"
                f" - - {npatr} {npata} - {ref_rpix} {ref_azlin} 0", uselogging=True)
    else:
        # create water mask only
        _ = get_water_mask(f'{ifgname}.adf.cc_mask.bmp', mwidth, lt, demw, demn, dempar)
        execute(f"mcf {ifgf}.adf {ifgname}.adf.cc {ifgname}.adf.cc_mask.bmp {ifgname}.adf.unw {width} {trimode} 0 0"
                f" - - {npatr} {npata} - {ref_rpix} {ref_azlin} 0", uselogging=True)

    execute(f"rasdt_pwr {ifgname}.adf.unw {mmli} {width} - - - - - {6 * np.pi} 1 rmg.cm {ifgname}.adf.unw.ras",
            uselogging=True)

    execute(f"dispmap {ifgname}.adf.unw DEM/HGT_SAR_{rlooks}_{alooks} {mmli}.par"
            f" - {ifgname}.vert.disp 1", uselogging=True)

    execute(f"dispmap {ifgname}.adf.unw DEM/HGT_SAR_{rlooks}_{alooks} {mmli}.par"
            f" - {ifgname}.los.disp 0", uselogging=True)

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
    geocode_back("{}.vert.disp".format(ifgname), "{}.vert.disp.geo".format(ifgname), width, lt, demw, demn, 0)
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
    data2geotiff("{}.vert.disp.geo".format(ifgname), "{}.vert.disp.geo.org.tif".format(ifgname), dempar, 2)
    data2geotiff("{}.los.disp.geo".format(ifgname), "{}.los.disp.geo.org.tif".format(ifgname), dempar, 2)
    data2geotiff("DEM/inc", "{}.inc.tif".format(ifgname), dempar, 2)
    data2geotiff("inc_ell", "{}.inc_ell.tif".format(ifgname), dempar, 2)
    execute(f"look_vector {mmli}.par {offit} {dempar} {dem} lv_theta lv_phi", uselogging=True)

    data2geotiff("lv_theta", "{}.lv_theta.tif".format(ifgname), dempar, 2)
    data2geotiff("lv_phi", "{}.lv_phi.tif".format(ifgname), dempar, 2)

    log.info("-------------------------------------------------")
    log.info("            End geocoding")
    log.info("-------------------------------------------------")

    return coords

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

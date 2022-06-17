"""Unwrap and geocode Sentinel-1 INSAR products from GAMMA"""

import argparse
import logging
import os
import subprocess
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from osgeo import gdal

from hyp3_gamma.water_mask import create_water_mask


log = logging.getLogger(__name__)


def get_ref_point_info(log_text: str):
    log_lines = log_text.splitlines()

    ref = [line for line in log_lines if "phase at reference point:" in line]
    ref_offset = float(ref[0].split(" ")[-2])

    init = [line for line in log_lines if "phase initialization flag:" in line]
    glb_offset = float(init[0].split(" ")[-2])
    init_flg = int(init[0].split(" ")[3])

    return {"initflg": init_flg, "refoffset": ref_offset, "glboffset": glb_offset}


def get_height_at_pixel(in_height_file: str, mlines: int, mwidth: int, ref_azlin: int, ref_rpix: int) -> float:
    """get the height of the pixel at the ref_azlin, ref_rpix
    """
    height = read_bin(in_height_file, mlines, mwidth)

    return height[ref_azlin, ref_rpix]


def coords_from_sarpix_coord(in_mli_par: str, ref_azlin: int, ref_rpix: int, height: float, in_dem_par: str) -> list:
    """
    Will return list of 6 coordinates if in_dem_par file is provided:
        row_s, col_s, row_m, col_m, y, x
    otherwise will return 4 coordinates:
        row_s, col_s, lat, lon
    with (row_s,col_s)in SAR space, and the rest of the coordinates in MAP space
    """
    cmd = ['sarpix_coord', in_mli_par, '-', in_dem_par, str(ref_azlin), str(ref_rpix), str(height)]
    log.info(f'Running command: {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    coord_log_lines = result.stdout.splitlines()

    selected_coords = [line for line in coord_log_lines if "selected" in line]
    log.info(f'Selected sarpix coordinates: {selected_coords[0]}')
    coord_lst = selected_coords[0].split()[:-1]
    coord_lst = [float(s) for s in coord_lst]
    return coord_lst


def get_coords(in_mli_par: str, ref_azlin: int = 0, ref_rpix: int = 0, height: float = 0.0,
               in_dem_par: str = None) -> dict:
    """
    Args:
        in_mli_par: GAMMA MLI par file
        ref_azlin: Reference azimuth line
        ref_rpix:  Reference range pixel
        in_dem_par: GAMMA DEM par file

    Returns:
        coordinates dictionary with row_s, col_s, lat, lon coordinates. Additionally, if
        in_dem_par is provided, coords will have row_m, col_m, y, and x.
    """
    row_s, col_s, lat, lon = coords_from_sarpix_coord(in_mli_par, ref_azlin, ref_rpix, height, '-')
    coords = {"row_s": int(row_s), "col_s": int(col_s), "lat": lat, "lon": lon}

    if in_dem_par:
        _, _, _, _, y, x = coords_from_sarpix_coord(in_mli_par, ref_azlin, ref_rpix, height, in_dem_par)
        coords["y"] = y
        coords["x"] = x

    return coords


def read_bin(file, lines: int, samples: int):
    data = np.fromfile(file, dtype='>f4')
    values = np.reshape(data, (lines, samples))
    return values


def read_bmp(file):
    im = Image.open(file)
    data = np.asarray(im)
    return data


def get_neighbors(array, i, j, n=1):
    i_max, j_max = array.shape

    i_start = max(i - n, 0)
    i_stop = min(i + n + 1, i_max)

    j_start = max(j - n, 0)
    j_stop = min(j + n + 1, j_max)

    return array[i_start:i_stop, j_start:j_stop]


def find_ref_point_with_largest_cc(data_cc: np.array, indices, window_size, start_idx, pick_num):

    # get the indices of the  pixels with the highest coherence values
    rows = indices[0][start_idx:start_idx + pick_num]

    cols = indices[1][start_idx:start_idx + pick_num]

    num = len(rows)
    tots = np.zeros(num, dtype=float)

    for k in range(num):
        neighbors = get_neighbors(data_cc, rows[k], cols[k], window_size)
        if (neighbors == 0.0).any() or neighbors.size < (2*window_size+1)**2:
            tots[k] = 0.0
        else:
            tots[k] = neighbors.sum()

    if (tots == 0.0).all():
        ref_i = None
        ref_j = None
    else:
        idx = np.where(tots == tots.max())
        ref_i = rows[idx[0][0]]
        ref_j = cols[idx[0][0]]

    return ref_i, ref_j


def ref_point_with_max_cc(data_cc: np.array, window_size=10, pick_num=20, cc_thresh=0.3):
    '''
    shift determine the window size, n=1 9-pixel window, n=2, 25-pixel window, etc.
    largest_num is the number of the first largest elements
    '''

    data = data_cc.copy()

    data[np.logical_or(data == 1.0, data < cc_thresh)] = 0.0

    indices = np.unravel_index(np.argsort(-data_cc, axis=None), data_cc.shape)

    start_idx = 0

    while True:

        ref_i, ref_j = find_ref_point_with_largest_cc(data, indices, window_size, start_idx, pick_num)

        if ref_i and ref_j:
            break

        start_idx += pick_num

    return ref_i, ref_j


def geocode_back(inname, outname, width, lt, demw, demn, type_):
    execute(f"geocode_back {inname} {width} {lt} {outname} {demw} {demn} 0 {type_}", uselogging=True)


def geocode(inname, outname, inwidth, lt, outwidth, outlines, type_):
    execute(f"geocode {lt} {inname} {inwidth} {outname} {outwidth} {outlines} - {type_}", uselogging=True)


def data2geotiff(inname, outname, dempar, type_):
    execute(f"data2geotiff {dempar} {inname} {type_} {outname} ", uselogging=True)


def create_phase_from_complex(incpx, outfloat, width):
    execute(f"cpx_to_real {incpx} {outfloat} {width} 4", uselogging=True)


def get_water_mask(cc_file, width, lt, demw, demn, dempar):
    """
    create water_mask geotiff file based on the cc_file (float binary file)
    """
    with TemporaryDirectory() as temp_dir:
        # 2--SUN raster/BMP/TIFF, 0--FLOAT (default)
        geocode_back(cc_file, f'{temp_dir}/tmp_mask_geo', width, lt, demw, demn, 0)
        # 0--RASTER 8 or 24 bit uncompressed raster image, SUN (*.ras), BMP:(*.bmp), or TIFF: (*.tif)
        # 2--FLOAT (4 bytes/value)
        data2geotiff(f'{temp_dir}/tmp_mask_geo', f'{temp_dir}/tmpgtiff_mask_geo.tif', dempar, 2)
        # create water_mask.tif file
        create_water_mask(f'{temp_dir}/tmpgtiff_mask_geo.tif', 'water_mask.tif')


def convert_water_mask_to_sar_bmp(water_mask, mwidth, mlines, lt, demw):
    '''
    input file is water_mask.tif file in MAP space, outptut is water_mask_sar.bmp file in SAR space.
    '''

    ds = gdal.Open(water_mask)
    band = ds.GetRasterBand(1)
    mask = band.ReadAsArray()
    del ds

    with TemporaryDirectory() as temp_dir:
        water_im = Image.fromarray(mask)
        water_bmp_file = f'{temp_dir}/water_mask.bmp'
        water_im.save(water_bmp_file)
        # map water_mask.bmp file to SAR coordinators
        water_mask_bmp_sar_file = "water_mask_sar.bmp"
        geocode(water_bmp_file, water_mask_bmp_sar_file, demw, lt, mwidth, mlines, 2)


def apply_mask(file: str, nlines: int, nsamples: int, mask_file: str):
    """
    use mask_file (bmp) to mask the file (binary), output the masked file (binary). All three file are in SAR space.
    """
    data = read_bin(file, nlines, nsamples)
    mask = read_bmp(mask_file)

    data[mask == 0] = 0

    outfile = "{file}_masked".format(file=file)
    data.tofile(outfile)

    return outfile


def combine_water_mask(cc_mask_file, water_mask_sar_file):
    """combine cc_mask with water_mask in SAR space
    """
    # read the original mask file
    in_im = Image.open(cc_mask_file)
    in_data = np.array(in_im)
    in_palette = in_im.getpalette()

    # combine two masks and output combined_mask.bmp
    water_mask_sar_data = read_bmp(water_mask_sar_file)
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

    execute(f"cc_wave {ifgf} - - {ifgname}.cc {width}", uselogging=True)

    execute(f"adf {ifgf} {ifgf}.adf {ifgname}.adf.cc {width} {alpha} - 5", uselogging=True)

    execute(f"rasmph_pwr {ifgf}.adf {mmli} {width}", uselogging=True)

    execute(f"rascc_mask {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 0.10 0.0 ", uselogging=True)

    get_water_mask(f"{ifgname}.adf.cc", width, lt, demw, demn, dempar)

    out_file = f"{ifgname}.adf.cc_mask.bmp"

    cc_ref = f"{ifgname}.cc"

    if apply_water_mask:
        # convert water_mak.tif in MAP to SAR space
        convert_water_mask_to_sar_bmp('water_mask.tif', mwidth, mlines, lt, demw)
        # combine the water mask with validity mask in SAR space
        out_file = combine_water_mask(f"{ifgname}.adf.cc_mask.bmp", 'water_mask_sar.bmp')
        # apply water mask in SAR space to cc
        cc_ref = apply_mask(f'{ifgname}.cc', int(mlines), int(mwidth), 'water_mask_sar.bmp')

    data_cc = read_bin(cc_ref, int(mlines), int(mwidth))
    ref_azlin, ref_rpix = ref_point_with_max_cc(data_cc)

    height = get_height_at_pixel(f"DEM/HGT_SAR_{rlooks}_{alooks}", int(mlines), int(mwidth), ref_azlin, ref_rpix)

    mcf_log = execute(f"mcf {ifgf}.adf {ifgname}.adf.cc {out_file} {ifgname}.adf.unw {width} {trimode} 0 0"
                      f" - - {npatr} {npata} - {ref_rpix} {ref_azlin} 1", uselogging=True)

    ref_point_info = get_ref_point_info(mcf_log)

    coords = get_coords(f"{mmli}.par", ref_azlin=ref_azlin, ref_rpix=ref_rpix, height=height, in_dem_par=dempar)

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

    return coords, ref_point_info


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

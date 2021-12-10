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


def coords_from_sapix_coord(in_mli_par: str, ref_azlin: int, ref_rpix: int, in_dem_par: str) -> list:
    """
    Will return list of 6 coordinates if in_dem_par file is provided:
        row_s, col_s, row_m, col_m, y, x
    otherwise will return 4 coordinates:
        row_s, col_s, lat, lon
    with (row_s,col_s)in SAR space, and the rest of the coordinates in MAP space
    """
    cmd = ['sarpix_coord', in_mli_par, '-', in_dem_par, str(ref_azlin), str(ref_rpix)]
    log.info(f'Running command: {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    coord_log_lines = result.stdout.splitlines()

    selected_coords = [line for line in coord_log_lines if "selected" in line]
    log.info(f'Selected sarpix coordinates: {selected_coords[0]}')
    coord_lst = selected_coords[0].split()[:-1]
    coord_lst = [float(s) for s in coord_lst]
    return coord_lst


def get_coords(in_mli_par: str, ref_azlin: int = 0, ref_rpix: int = 0, in_dem_par: str = None) -> dict:
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
    row_s, col_s, lat, lon = coords_from_sapix_coord(in_mli_par, ref_azlin, ref_rpix, '-')
    coords = {"row_s": int(row_s), "col_s": int(col_s), "lat": lat, "lon": lon}

    if in_dem_par:
        _, _, _, _, y, x = coords_from_sapix_coord(in_mli_par, ref_azlin, ref_rpix, in_dem_par)
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


def convert_bin_bmp(binfile: str, lines: int, samples: int):
    data = read_bin(binfile, lines, samples)
    out_file = "{binfile}.bmp".format(binfile = binfile)
    out_im = Image.fromarray(data)
    out_im.save(out_file)
    return out_file


def convert_bin_tiff(binfile: str, lines: int, samples: int):
    data = read_bin(binfile, lines, samples)
    out_file = "{binfile}.tif".format(binfile = binfile)
    out_im = Image.fromarray(data)
    out_im.save(out_file)
    return out_file



def convert_bmp_bin(bmpfile: str, outfile: str):
    data = read_bmp(bmpfile)
    np.tofile(outfile)
    return outfile


def ref_point_with_max_cc(fcc: str, fmask: str, mlines: int, mwidth: int):
    data_mk = read_bmp(fmask)
    data_mk_max = data_mk.max()
    data_mk = np.ma.masked_values(data_mk, data_mk_max)

    data_cc = read_bin(fcc, mlines, mwidth)
    data_cc_max = data_cc[data_mk.mask].max()
    idx = np.where(data_cc == data_cc_max)
    if idx:
        ref_i = idx[0][0]
        ref_j = idx[1][0]
        return ref_i, ref_j

    return 0, 0


def get_avg_intensity(mmli: str, mlines: int, mwidth: int):
    data = read_bin(mmli, mlines, mwidth)
    return float(data.mean())


def geocode_back(inname, outname, width, lt, demw, demn, type_):
    execute(f"geocode_back {inname} {width} {lt} {outname} {demw} {demn} 0 {type_}", uselogging=True)


def geocode(inname, outname, inwidth, lt, outwidth, outlines, type_):
    execute(f"geocode {lt} {inname} {inwidth} {outname} {outwidth} {outlines} - {type_}", uselogging=True)


def data2geotiff(inname, outname, dempar, type_):
    execute(f"data2geotiff {dempar} {inname} {type_} {outname} ", uselogging=True)


def create_phase_from_complex(incpx, outfloat, width):
    execute(f"cpx_to_real {incpx} {outfloat} {width} 4", uselogging=True)


def get_water_mask_orig(cc_mask_file, mwidth, lt, demw, demn, dempar):
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

def get_water_mask(cc_file, mwidth, lt, demw, demn, dempar):
    """
    create water_mask based on the cc_file
    """
    with TemporaryDirectory() as temp_dir:
        os.system(f'cp {cc_file} {temp_dir}/tmp_mask.tif')
        # 2--SUN raster/BMP/TIFF, 0--FLOAT (default)
        geocode_back(f'{temp_dir}/tmp_mask.tif', f'{temp_dir}/tmp_mask_geo.tif', mwidth, lt, demw, demn, 0)
        # 0--RASTER 8 or 24 bit uncompressed raster image, SUN (*.ras), BMP:(*.bmp), or TIFF: (*.tif)
        # 2--FLOAT (4 bytes/value)
        data2geotiff(f'{temp_dir}/tmp_mask_geo.tif', f'{temp_dir}/tmpgtiff_mask_geo.tif', dempar, 2)
        # create water_mask.tif file
        create_water_mask(f'{temp_dir}/tmpgtiff_mask_geo.tif', 'water_mask.tif')
    ds = gdal.Open('water_mask.tif')
    band = ds.GetRasterBand(1)
    mask = band.ReadAsArray()
    del ds
    return mask

def convert_from_sar_2_map(in_file, out_geotiff, width, lt, dempar, demw, demn, type_):

    geocode_back(in_file, "tmp.bmp", width, lt, demw, demn, type_)

    data2geotiff("tmp.bmp", out_geotiff, dempar, type_)


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


def mask_file(file: str, nlines, nsamples, mask_file: str):
    """
    use mask_file (bmp) to mask the file (binary), output the masked binary format file.
    """
    data = read_bin(file, nlines, nsamples)
    mask = read_bmp(mask_file)

    data[mask == 0] = 0
    outfile = "{file}_masked".format(file=file)
    data.tofile(outfile)

    return outfile


def get_masked_files(cc_file, mmli_file, mwidth, mlines, lt, demw, demn, dempar):
    """use water_mask to mask the cc and mmli, then used masked cc and mmli to calcualte the validity mask
    """
    # convert cc_file to {cc_file}.bmp
    cc_file_tif = convert_bin_tiff(cc_file, mlines, mwidth)
    mmli_file_tif = convert_bin_tiff(mmli_file, mlines, mwidth)

    # in_im = Image.open(cc_mask_file)
    # in_data = np.array(in_im)
    # in_palette = in_im.getpalette()

    with TemporaryDirectory() as temp_dir:
        # get mask data and save it into the water_mask.bmp file
        mask = get_water_mask(cc_file_tif, mwidth, lt, demw, demn, dempar)
        water_im = Image.fromarray(mask)
        # water_im.putpalette(in_palette)
        water_bmp_file = f'{temp_dir}/water_mask.bmp'
        water_im.save(water_bmp_file)

        # map water_mask.bmp file to SAR coordinators
        water_mask_bmp_sar_file = f'{temp_dir}/water_mask_sar.bmp'
        geocode(water_bmp_file, water_mask_bmp_sar_file, demw, lt, mwidth, mlines, 2)

        # read water_mask_bmp_sar_file
        # water_mask_sar_im = Image.open(water_mask_bmp_sar_file)
        # water_mask_sar_data = np.array(water_mask_sar_im)

        # mask cc_file and mmli_file
        cc_masked_file = mask_file(cc_file, mlines, mwidth, water_mask_bmp_sar_file)
        intensity_masked_file = mask_file(mmli_file, mlines, mwidth,water_mask_bmp_sar_file)

    return cc_masked_file, intensity_masked_file



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

    execute(f"cc_wave {ifgf} {mmli} - {ifgname}.cc {width}", uselogging=True)

    execute(f"adf {ifgf} {ifgf}.adf {ifgname}.adf.cc {width} {alpha} - 5", uselogging=True)

    execute(f"rasmph_pwr {ifgf}.adf {mmli} {width}", uselogging=True)

    # orignal cc_thres=0.1, pwr_thres=0.2
    # execute(f"rascc_mask {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 0.10 0.20 ", uselogging=True)

    # test
    cc_thres = float(input("cc_thres: "))
    pwr_thres = float(input("pwr_thres: "))

    # get the avg_intensity of the {mmli}
    # avg_intensity = get_avg_intensity(mmli, int(mlines), int(mwidth))
    # relative_pwr_thres = round(pwr_thres/avg_intensity, 2)
    # print(f"relative_pwr_thres: {relative_pwr_thres}")

    # mask {ifgname}.adf.cc and {mmli} files
    adf_cc_masked, mmli_masked = get_masked_files(f"{ifgname}.adf.cc", mmli, int(mwidth), int(mlines), lt, int(demw),
                                                  int(demn), dempar)
    execute(f"rascc_mask {adf_cc_masked} {mmli_masked} {width} 1 1 0 1 1 {cc_thres} {pwr_thres} ", uselogging=True)
    #the outputfile name is {adf_cc_masked}_mask.bmp

    # execute(f"rascc_mask {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 {cc_thres} {pwr_thres} ", uselogging=True)
    # execute(f"rascc_mask {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 {cc_thres} {relative_pwr_thres} ", uselogging=True)

    # test secondary way to produce combined mask
    out_file = "{adf_cc_masked}_mask.bmp".format(adf_cc_masked = adf_cc_masked)

    """
    if apply_water_mask:
        # create and apply water mask
        out_file = combine_water_mask(f"{ifgname}.adf.cc_mask.bmp", mwidth, mlines, lt, demw, demn, dempar)
    else:
        # create water mask only
        _ = get_water_mask(f"{ifgname}.adf.cc_mask.bmp", mwidth, lt, demw, demn, dempar)
        out_file = f"{ifgname}.adf.cc_mask.bmp"
   """

    ref_azlin, ref_rpix = ref_point_with_max_cc(f"{ifgname}.cc", out_file, int(mlines), int(mwidth))

    # mcf_log = execute(f"mcf {ifgf}.adf {ifgname}.adf.cc {out_file} {ifgname}.adf.unw {width} {trimode} 0 0"
    #                  f" - - {npatr} {npata} - {ref_rpix} {ref_azlin} 1", uselogging=True)

    # test if apply the validity mask

    mask_flg = input("do you want to use validity(y/n): ")
    if mask_flg.lower() == 'y':

        mcf_log = execute(f"mcf {ifgf}.adf {ifgname}.adf.cc {out_file} {ifgname}.adf.unw {width} {trimode} 0 0"
                          f" - - {npatr} {npata} - {ref_rpix} {ref_azlin} 1", uselogging=True)
    else:

        mcf_log = execute(f"mcf {ifgf}.adf {ifgname}.adf.cc - {ifgname}.adf.unw {width} {trimode} 0 0"
                          f" - - {npatr} {npata} - {ref_rpix} {ref_azlin} 1", uselogging=True)

    ref_point_info = get_ref_point_info(mcf_log)

    coords = get_coords(f"{mmli}.par", ref_azlin=ref_azlin, ref_rpix=ref_rpix, in_dem_par=dempar)

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

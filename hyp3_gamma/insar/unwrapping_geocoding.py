"""Unwrap and geocode Sentinel-1 INSAR products from GAMMA"""

import argparse
import logging
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory

import numpy as np
import scipy.ndimage
from PIL import Image
from hyp3lib.execute import execute
from osgeo import gdal

from hyp3_gamma.get_parameter import get_parameter
from hyp3_gamma.water_mask import create_water_mask


log = logging.getLogger(__name__)


def get_ref_point_info(log_text: str):
    log_lines = log_text.splitlines()

    ref = [line for line in log_lines if 'phase at reference point:' in line]
    ref_offset = float(ref[0].split(' ')[-2])

    init = [line for line in log_lines if 'phase initialization flag:' in line]
    glb_offset = float(init[0].split(' ')[-2])
    init_flg = int(init[0].split(' ')[3])

    return {'initflg': init_flg, 'refoffset': ref_offset, 'glboffset': glb_offset}


def get_height_at_pixel(in_height_file: str, mlines: int, mwidth: int, ref_azlin: int, ref_rpix: int) -> float:
    """Get the height of the pixel (ref_azlin, ref_rpix)"""
    height = read_bin(in_height_file, mlines, mwidth)

    return height[ref_azlin, ref_rpix]


def coords_from_sarpix_coord(in_mli_par: str, ref_azlin: int, ref_rpix: int, height: float, in_dem_par: str) -> list:
    """Will return list of 6 coordinates if in_dem_par file is provided:
        row_s, col_s, row_m, col_m, y, x
    otherwise will return 4 coordinates:
        row_s, col_s, lat, lon
    with (row_s,col_s)in SAR space, and the rest of the coordinates in MAP space
    """
    cmd = [
        'sarpix_coord',
        in_mli_par,
        '-',
        in_dem_par,
        str(ref_azlin),
        str(ref_rpix),
        str(height),
    ]
    log.info(f'Running command: {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    coord_log_lines = result.stdout.splitlines()

    selected_coords = [line for line in coord_log_lines if 'selected' in line]
    log.info(f'Selected sarpix coordinates: {selected_coords[0]}')
    coord_lst_str = selected_coords[0].split()[:-1]
    coord_lst = [float(s) for s in coord_lst_str]
    return coord_lst


def get_coords(
    in_mli_par: str,
    ref_azlin: int = 0,
    ref_rpix: int = 0,
    height: float = 0.0,
    in_dem_par: str | None = None,
) -> dict:
    """Args:
        in_mli_par: GAMMA MLI par file
        ref_azlin: Reference azimuth line
        ref_rpix:  Reference range pixel
        height: Height of the reference point
        in_dem_par: GAMMA DEM par file

    Returns:
        coordinates dictionary with row_s, col_s, lat, lon coordinates. Additionally, if
        in_dem_par is provided, coords will have row_m, col_m, y, and x.
    """
    row_s, col_s, lat, lon = coords_from_sarpix_coord(in_mli_par, ref_azlin, ref_rpix, height, '-')
    coords = {'row_s': int(row_s), 'col_s': int(col_s), 'lat': lat, 'lon': lon}

    if in_dem_par:
        _, _, _, _, y, x = coords_from_sarpix_coord(in_mli_par, ref_azlin, ref_rpix, height, in_dem_par)
        coords['y'] = y
        coords['x'] = x

    return coords


def read_bin(file, lines: int, samples: int):
    data = np.fromfile(file, dtype='>f4')
    values = np.reshape(data, (lines, samples))
    return values


def read_bmp(file):
    im = Image.open(file)
    data = np.asarray(im)
    return data


def get_reference_pixel(coherence: np.ndarray, window_size=(5, 5), coherence_threshold=0.3) -> tuple[int, int]:
    """Args:
        coherence: array of coherence values
        window_size: window size over which to sum coherence values for each pixel
        coherence_threshold: pixels with values less than the threshold in their window will not be considered

    Returns:
        array indices of the reference pixel
    """

    def sum_valid_coherence_values(array: np.ndarray) -> float:
        if (array < coherence_threshold).any() or (array == np.float64(1.0)).any():
            return 0.0
        return array.sum()

    pixel_weights = scipy.ndimage.generic_filter(
        input=coherence,
        function=sum_valid_coherence_values,
        size=window_size,
        mode='constant',
        cval=0.0,
    )
    x, y = np.unravel_index(np.argmax(pixel_weights), pixel_weights.shape)
    return int(x), int(y)


def geocode_back(inname, outname, width, lt, demw, demn, type_):
    execute(
        f'geocode_back {inname} {width} {lt} {outname} {demw} {demn} 0 {type_}',
        uselogging=True,
    )


def geocode(inname, outname, inwidth, lt, outwidth, outlines, type_):
    execute(
        f'geocode {lt} {inname} {inwidth} {outname} {outwidth} {outlines} - {type_}',
        uselogging=True,
    )


def data2geotiff(inname, outname, dempar, type_):
    execute(f'data2geotiff {dempar} {inname} {type_} {outname} ', uselogging=True)


def create_phase_from_complex(incpx, outfloat, width):
    execute(f'cpx_to_real {incpx} {outfloat} {width} 4', uselogging=True)


def get_water_mask(cc_file, width, lt, demw, demn, dempar):
    """Create water_mask geotiff file based on the cc_file (float binary file)"""
    with TemporaryDirectory() as temp_dir:
        # 2--SUN raster/BMP/TIFF, 0--FLOAT (default)
        geocode_back(cc_file, f'{temp_dir}/tmp_mask_geo', width, lt, demw, demn, 0)
        # 0--RASTER 8 or 24 bit uncompressed raster image, SUN (*.ras), BMP:(*.bmp), or TIFF: (*.tif)
        # 2--FLOAT (4 bytes/value)
        data2geotiff(f'{temp_dir}/tmp_mask_geo', f'{temp_dir}/tmpgtiff_mask_geo.tif', dempar, 2)
        # create water_mask.tif file
        create_water_mask(f'{temp_dir}/tmpgtiff_mask_geo.tif', 'water_mask.tif')


def convert_water_mask_to_sar_bmp(water_mask, mwidth, mlines, lt, demw):
    """Input file is water_mask.tif file in MAP space, outptut is water_mask_sar.bmp file in SAR space."""
    ds = gdal.Open(water_mask)
    band = ds.GetRasterBand(1)
    mask = band.ReadAsArray()
    del ds

    with TemporaryDirectory() as temp_dir:
        water_im = Image.fromarray(mask)
        water_bmp_file = f'{temp_dir}/water_mask.bmp'
        water_im.save(water_bmp_file)
        # map water_mask.bmp file to SAR coordinators
        water_mask_bmp_sar_file = 'water_mask_sar.bmp'
        geocode(water_bmp_file, water_mask_bmp_sar_file, demw, lt, mwidth, mlines, 2)


def apply_mask(file: str, nlines: int, nsamples: int, mask_file: str):
    """Use mask_file (bmp) to mask the file (binary), output the masked file (binary). All three file are in SAR space."""
    data = read_bin(file, nlines, nsamples)
    mask = read_bmp(mask_file)

    data[mask == 0] = 0

    outfile = f'{file}_masked'
    data.tofile(outfile)

    return outfile


def combine_water_mask(cc_mask_file, water_mask_sar_file):
    """Combine cc_mask with water_mask in SAR space"""
    # read the original mask file
    in_im = Image.open(cc_mask_file)
    in_data = np.array(in_im)
    in_palette = in_im.getpalette()

    # combine two masks and output combined_mask.bmp
    water_mask_sar_data = read_bmp(water_mask_sar_file)
    in_data[water_mask_sar_data == 0] = 0
    out_im = Image.fromarray(in_data)
    assert in_palette is not None
    out_im.putpalette(in_palette)
    out_file = os.path.join(os.path.dirname(cc_mask_file), 'combined_mask.bmp')
    out_im.save(out_file)

    return out_file


def unwrapping_geocoding(
    reference,
    secondary,
    step='man',
    rlooks=10,
    alooks=2,
    trimode=0,
    alpha=0.6,
    apply_water_mask=False,
):
    dem = './DEM/demseg'
    dempar = './DEM/demseg.par'
    lt = './DEM/MAP2RDC'
    ifgname = f'{reference}_{secondary}'
    offit = f'{ifgname}.off.it'
    mmli = reference + '.mli'
    smli = secondary + '.mli'

    if not os.path.isfile(dempar):
        log.error(f'ERROR: Unable to find dem par file {dempar}')

    if not os.path.isfile(lt):
        log.error(f'ERROR: Unable to find look up table file {lt}')

    if not os.path.isfile(offit):
        log.error(f'ERROR: Unable to find offset file {offit}')

    width = get_parameter(offit, 'interferogram_width')
    lines = get_parameter(offit, 'interferogram_azimuth_lines')
    mwidth = get_parameter(mmli + '.par', 'range_samples')
    mlines = get_parameter(mmli + '.par', 'azimuth_lines')
    swidth = get_parameter(smli + '.par', 'range_samples')
    demw = get_parameter(dempar, 'width')
    demn = get_parameter(dempar, 'nlines')

    ifgf = f'{ifgname}.diff0.{step}'

    log.info(f'{ifgf} will be used for unwrapping and geocoding')

    log.info('-------------------------------------------------')
    log.info('            Start unwrapping')
    log.info('-------------------------------------------------')

    execute(f'cc_wave {ifgf} - - {ifgname}.cc {width}', uselogging=True)

    if alpha > 0.0:
        execute(
            f'adf {ifgf} {ifgf}.adf {ifgname}.adf.cc {width} {alpha} - 5',
            uselogging=True,
        )
    else:
        log.info('Skipping adaptive phase filter because alpha is zero')
        shutil.copyfile(ifgf, f'{ifgf}.adf')
        shutil.copyfile(f'{ifgname}.cc', f'{ifgname}.adf.cc')

    execute(f'rasmph_pwr {ifgf}.adf {mmli} {width}', uselogging=True)

    execute(
        f'rascc_mask {ifgname}.adf.cc {mmli} {width} 1 1 0 1 1 0.10 0.0 ',
        uselogging=True,
    )

    get_water_mask(f'{ifgname}.adf.cc', width, lt, demw, demn, dempar)

    out_file = f'{ifgname}.adf.cc_mask.bmp'

    cc_ref = f'{ifgname}.cc'

    if apply_water_mask:
        # convert water_mak.tif in MAP to SAR space
        convert_water_mask_to_sar_bmp('water_mask.tif', mwidth, mlines, lt, demw)
        # combine the water mask with validity mask in SAR space
        out_file = combine_water_mask(f'{ifgname}.adf.cc_mask.bmp', 'water_mask_sar.bmp')
        # apply water mask in SAR space to cc
        cc_ref = apply_mask(f'{ifgname}.cc', int(mlines), int(mwidth), 'water_mask_sar.bmp')

    data_cc = read_bin(cc_ref, int(mlines), int(mwidth))
    ref_azlin, ref_rpix = get_reference_pixel(data_cc)
    del data_cc

    height = get_height_at_pixel(f'DEM/HGT_SAR_{rlooks}_{alooks}', int(mlines), int(mwidth), ref_azlin, ref_rpix)

    # unwrap very large interferograms in multiple patches to keep memory requirement under 31,600 MB
    # https://github.com/ASFHyP3/hyp3-gamma/issues/316
    if int(width) * int(lines) < 54000000:
        range_patches = 1
    else:
        range_patches = 2

    mcf_log = execute(
        f'mcf {ifgf}.adf {ifgname}.adf.cc {out_file} {ifgname}.adf.unw {width} {trimode} 0 0'
        f' - - {range_patches} 1 - {ref_rpix} {ref_azlin} 1',
        uselogging=True,
    )

    ref_point_info = get_ref_point_info(mcf_log)

    coords = get_coords(
        f'{mmli}.par',
        ref_azlin=ref_azlin,
        ref_rpix=ref_rpix,
        height=height,
        in_dem_par=dempar,
    )

    execute(
        f'rasdt_pwr {ifgname}.adf.unw {mmli} {width} - - - - - {6 * np.pi} 1 rmg.cm {ifgname}.adf.unw.ras',
        uselogging=True,
    )

    execute(
        f'dispmap {ifgname}.adf.unw DEM/HGT_SAR_{rlooks}_{alooks} {mmli}.par - {ifgname}.vert.disp 1',
        uselogging=True,
    )

    execute(
        f'dispmap {ifgname}.adf.unw DEM/HGT_SAR_{rlooks}_{alooks} {mmli}.par - {ifgname}.los.disp 0',
        uselogging=True,
    )

    execute(f'gc_map2 {mmli}.par DEM/demseg.par 0 - - - - - - - inc_ell')

    log.info('-------------------------------------------------')
    log.info('            End unwrapping')
    log.info('-------------------------------------------------')

    log.info('-------------------------------------------------')
    log.info('            Start geocoding')
    log.info('-------------------------------------------------')

    geocode_back(mmli, mmli + '.geo', mwidth, lt, demw, demn, 0)
    geocode_back(smli, smli + '.geo', swidth, lt, demw, demn, 0)
    geocode_back(
        f'{ifgname}.sim_unw',
        f'{ifgname}.sim_unw.geo',
        width,
        lt,
        demw,
        demn,
        0,
    )
    geocode_back(
        f'{ifgname}.adf.unw',
        f'{ifgname}.adf.unw.geo',
        width,
        lt,
        demw,
        demn,
        0,
    )
    geocode_back(f'{ifgf}.adf', f'{ifgf}.adf.geo', width, lt, demw, demn, 1)
    geocode_back(
        f'{ifgname}.adf.unw.ras',
        f'{ifgname}.adf.unw.geo.bmp',
        width,
        lt,
        demw,
        demn,
        2,
    )
    geocode_back(
        f'{ifgf}.adf.bmp',
        f'{ifgf}.adf.bmp.geo',
        width,
        lt,
        demw,
        demn,
        2,
    )
    geocode_back(f'{ifgname}.cc', f'{ifgname}.cc.geo', width, lt, demw, demn, 0)
    geocode_back(
        f'{ifgname}.adf.cc',
        f'{ifgname}.adf.cc.geo',
        width,
        lt,
        demw,
        demn,
        0,
    )
    geocode_back(
        f'{ifgname}.vert.disp',
        f'{ifgname}.vert.disp.geo',
        width,
        lt,
        demw,
        demn,
        0,
    )
    geocode_back(
        f'{ifgname}.los.disp',
        f'{ifgname}.los.disp.geo',
        width,
        lt,
        demw,
        demn,
        0,
    )

    create_phase_from_complex(f'{ifgf}.adf.geo', f'{ifgf}.adf.geo.phase', width)

    data2geotiff(mmli + '.geo', mmli + '.geo.tif', dempar, 2)
    data2geotiff(smli + '.geo', smli + '.geo.tif', dempar, 2)
    data2geotiff(
        f'{ifgname}.sim_unw.geo',
        f'{ifgname}.sim_unw.geo.tif',
        dempar,
        2,
    )
    data2geotiff(
        f'{ifgname}.adf.unw.geo',
        f'{ifgname}.adf.unw.geo.tif',
        dempar,
        2,
    )
    data2geotiff(
        f'{ifgname}.adf.unw.geo.bmp',
        f'{ifgname}.adf.unw.geo.bmp.tif',
        dempar,
        0,
    )
    data2geotiff(f'{ifgf}.adf.geo.phase', f'{ifgf}.adf.geo.tif', dempar, 2)
    data2geotiff(f'{ifgf}.adf.bmp.geo', f'{ifgf}.adf.bmp.geo.tif', dempar, 0)
    data2geotiff(f'{ifgname}.cc.geo', f'{ifgname}.cc.geo.tif', dempar, 2)
    data2geotiff(f'{ifgname}.adf.cc.geo', f'{ifgname}.adf.cc.geo.tif', dempar, 2)
    data2geotiff('DEM/demseg', f'{ifgname}.dem.tif', dempar, 2)
    data2geotiff(
        f'{ifgname}.vert.disp.geo',
        f'{ifgname}.vert.disp.geo.org.tif',
        dempar,
        2,
    )
    data2geotiff(
        f'{ifgname}.los.disp.geo',
        f'{ifgname}.los.disp.geo.org.tif',
        dempar,
        2,
    )
    data2geotiff('DEM/inc', f'{ifgname}.inc.tif', dempar, 2)
    data2geotiff('inc_ell', f'{ifgname}.inc_ell.tif', dempar, 2)
    execute(
        f'look_vector {mmli}.par {offit} {dempar} {dem} lv_theta lv_phi',
        uselogging=True,
    )

    data2geotiff('lv_theta', f'{ifgname}.lv_theta.tif', dempar, 2)
    data2geotiff('lv_phi', f'{ifgname}.lv_phi.tif', dempar, 2)

    log.info('-------------------------------------------------')
    log.info('            End geocoding')
    log.info('-------------------------------------------------')

    return coords, ref_point_info


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='unwrapping_geocoding.py',
        description=__doc__,
    )
    parser.add_argument('reference', help='Reference scene identifier')
    parser.add_argument('secondary', help='Secondary scene identifier')
    parser.add_argument(
        '-s',
        '--step',
        default='man',
        help='Level of interferogram for unwrapping (def=man)',
    )
    parser.add_argument('-r', '--rlooks', default=10, help='Number of range looks (def=10)')
    parser.add_argument('-a', '--alooks', default=2, help='Number of azimuth looks (def=2)')
    parser.add_argument(
        '-t',
        '--tri',
        default=0,
        help='Triangulation method for mcf unwrapper: 0) filled traingular mesh (default); 1) Delaunay triangulation',
    )
    parser.add_argument('--alpha', default=0.6, type=float, help='adf filter alpha value (def=0.6)')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO,
    )

    unwrapping_geocoding(
        args.reference,
        args.secondary,
        step=args.step,
        rlooks=args.rlooks,
        alooks=args.alooks,
        trimode=args.tri,
        alpha=args.alpha,
    )


if __name__ == '__main__':
    main()

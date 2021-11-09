"""Create a Radiometrically Terrain-Corrected (RTC) product from a Sentinel-1 scene using GAMMA software"""

import logging
import os
import shutil
import zipfile
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from datetime import datetime, timezone
from glob import glob
from math import isclose
from pathlib import Path
from secrets import token_hex
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import List

import numpy as np
from hyp3lib import DemError, ExecuteError, GranuleError, OrbitDownloadError
from hyp3lib import saa_func_lib as saa
from hyp3lib.byteSigmaScale import byteSigmaScale
from hyp3lib.createAmp import createAmp
from hyp3lib.execute import execute
from hyp3lib.getDemFor import getDemFile
from hyp3lib.getParameter import getParameter
from hyp3lib.get_dem import get_dem
from hyp3lib.get_orb import downloadSentinelOrbitFile
from hyp3lib.makeAsfBrowse import makeAsfBrowse
from hyp3lib.make_cogs import cogify_dir
from hyp3lib.raster_boundary2shape import raster_boundary2shape
from hyp3lib.rtc2color import rtc2color
from hyp3lib.system import gamma_version
from hyp3lib.utm2dem import utm2dem
from osgeo import gdal, gdalconst, ogr

import hyp3_gamma
from hyp3_gamma.dem import get_geometry_from_kml, prepare_dem_geotiff
from hyp3_gamma.metadata import create_metadata_file_set_rtc
from hyp3_gamma.rtc.coregistration import CoregistrationError, check_coregistration
from hyp3_gamma.util import is_shift, set_pixel_as_point, unzip_granule


log = logging.getLogger()
gdal.UseExceptions()
ogr.UseExceptions()


def create_decibel_tif(fi, nodata=None):
    f = gdal.Open(fi)
    in_nodata = f.GetRasterBand(1).GetNoDataValue()
    _, _, trans, proj, data = saa.read_gdal_file(f)
    data = np.ma.masked_less_equal(np.ma.masked_values(data, in_nodata), 0.)
    powerdb = 10*np.ma.log10(data)
    if not nodata:
        nodata = np.finfo(data.dtype).min.astype(float)
    outfile = fi.replace('.tif', '-db.tif')
    saa.write_gdal_file_float(outfile, trans, proj, powerdb.filled(nodata), nodata=nodata)
    del f
    return outfile


def get_product_name(granule_name, orbit_file=None, resolution=30.0, radiometry='gamma0', scale='power',
                     filtered=False, matching=False):
    platform = granule_name[0:3]
    beam_mode = granule_name[4:6]
    polarization = granule_name[14:16]
    acq_start_time = granule_name[17:32]
    res = int(resolution)

    if orbit_file is None:
        o = 'O'
    elif 'POEORB' in orbit_file:
        o = 'P'
    elif 'RESORB' in orbit_file:
        o = 'R'
    else:
        o = 'O'

    product_id = token_hex(2).upper()

    g = 'g' if radiometry == 'gamma0' else 's'
    p = 'p' if scale == 'power' else 'd' if scale == 'decibel' else 'a'
    f = 'f' if filtered else 'n'
    m = 'm' if matching else 'd'

    product_name = f'{platform}_{beam_mode}_{acq_start_time}_{polarization}{o}_RTC{res}_G_{g}{p}u{f}e{m}_{product_id}'
    return product_name


def get_granule_type(granule):
    granule_type = granule.split('_')[2]
    if granule_type not in ('GRDH', 'SLC'):
        raise ValueError(f'Unsupported granule type {granule_type}.  Only GRDH and SLC are supported.')
    return granule_type


def get_looks(granule_type, resolution):
    if granule_type == 'GRDH' and isclose(resolution, 30.0):
        return 6
    return round(resolution / 10)


def configure_log_file(log_file):
    log_file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%m/%d/%Y %I:%M:%S %p')
    log_file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(log_file_handler)
    return log_file


def log_parameters(safe_dir, resolution, radiometry, scale, speckle_filter, dem_matching, include_dem, include_inc_map,
                   include_scattering_area, include_rgb, orbit_file, product_name, dem_name):
    log.info('Parameters for this run:')
    log.info(f'    SAFE directory            : {safe_dir}')
    log.info(f'    Output resolution         : {resolution}')
    log.info(f'    Radiometry                : {radiometry}')
    log.info(f'    Scale                     : {scale}')
    log.info(f'    Speckle filter            : {speckle_filter}')
    log.info(f'    DEM matching              : {dem_matching}')
    log.info(f'    Include DEM               : {include_dem}')
    log.info(f'    Include inc. angle map    : {include_inc_map}')
    log.info(f'    Include scattering area   : {include_scattering_area}')
    log.info(f'    Include RGB decomposition : {include_rgb}')
    log.info(f'    Orbit file                : {orbit_file or "Original Predicted"}')
    log.info(f'    Output name               : {product_name}')
    log.info(f'    DEM name                  : {dem_name}')


def get_polarizations(safe_dir, skip_cross_pol=True):
    mapping = {
        'SH': ['hh'],
        'SV': ['vv'],
        'DH': ['hh', 'hv'],
        'DV': ['vv', 'vh'],
    }
    key = safe_dir[14:16]
    polarizations = mapping.get(key)

    if not polarizations:
        raise GranuleError(f'Could not determine polarization(s) from {safe_dir}')

    if len(polarizations) > 1 and skip_cross_pol:
        polarizations.pop()

    return polarizations


def run(cmd):
    execute(cmd, uselogging=True)


def prepare_dem(safe_dir: str, dem_name: str, bbox: List[float] = None, dem: str = None):
    dem_tif = 'dem.tif'
    dem_type = 'UNKNOWN'
    dem_image = 'dem.image'
    dem_par = 'dem.par'

    if dem:
        run(f'dem_import {dem} {dem_image} {dem_par} - - $DIFF_HOME/scripts/egm2008-5.dem '
            f'$DIFF_HOME/scripts/egm2008-5.dem_par')

    elif dem_name == 'copernicus':
        dem_type = 'GLO-30'
        if bbox:
            wkt = f'POLYGON (({bbox[0]} {bbox[3]}, {bbox[2]} {bbox[3]}, {bbox[2]} {bbox[1]}, {bbox[0]} {bbox[1]}, ' \
                  f'{bbox[0]} {bbox[3]}))'
            geometry = ogr.CreateGeometryFromWkt(wkt)
        else:
            geometry = get_geometry_from_kml(f'{safe_dir}/preview/map-overlay.kml')
        prepare_dem_geotiff(dem_tif, geometry)
        run(f'dem_import {dem_tif} {dem_image} {dem_par} - - $DIFF_HOME/scripts/egm2008-5.dem '
            f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - 1')

    elif dem_name == 'legacy':
        if bbox:
            dem_type = get_dem(bbox[0], bbox[1], bbox[2], bbox[3], dem_tif, post=30.0)
        else:
            dem, dem_type = getDemFile(safe_dir, dem_tif, post=30.0)
        utm2dem(dem_tif, dem_image, dem_par)

    else:
        raise DemError(f'DEM name "{dem_name}" is invalid; supported options are "copernicus" and "legacy".')

    return dem_image, dem_par, dem_type


def prepare_mli_image(safe_dir, granule_type, pol, orbit_file, looks):
    log.info(f'Generating multi-looked {pol.upper()} image')
    if granule_type == 'GRDH':
        return _prepare_mli_image_from_grd(safe_dir, pol, orbit_file, looks)
    elif granule_type == 'SLC':
        return _prepare_mli_image_from_slc(safe_dir, pol, orbit_file, looks)


def _prepare_mli_image_from_grd(safe_dir, pol, orbit_file, looks):
    annotation_xml = f'{safe_dir}/annotation/*-{pol}-*.xml'
    calibration_xml = f'{safe_dir}/annotation/calibration/calibration*-{pol}-*.xml'
    noise_xml = f'{safe_dir}/annotation/calibration/noise*-{pol}-*.xml'
    tiff = f'{safe_dir}/measurement/*-{pol}-*.tiff'

    mli_image = f'{pol}.mli'
    mli_par = f'{pol}.mli.par'

    with NamedTemporaryFile() as temp_image, NamedTemporaryFile() as temp_par:
        run(f'par_S1_GRD {tiff} {annotation_xml} {calibration_xml} {noise_xml} {temp_par.name} {temp_image.name}')
        if orbit_file:
            run(f'S1_OPOD_vec {temp_par.name} {orbit_file}')
        run(f'multi_look_MLI {temp_image.name} {temp_par.name} {mli_image} {mli_par} {looks} {looks} - - - 1')

    return mli_image, mli_par


def _prepare_mli_image_from_slc(safe_dir, pol, orbit_file, looks):
    with TemporaryDirectory() as temp_dir:
        slc_tab = f'{temp_dir}/slc_tab'
        for swath in (1, 2, 3):
            annotation_xml = f'{safe_dir}/annotation/*-iw{swath}-slc-{pol}-*.xml'
            calibration_xml = f'{safe_dir}/annotation/calibration/calibration-*-iw{swath}-slc-{pol}-*.xml'
            noise_xml = f'{safe_dir}/annotation/calibration/noise-*-iw{swath}-slc-{pol}-*.xml'
            tiff = f'{safe_dir}/measurement/*-iw{swath}-slc-{pol}-*.tiff'

            slc_image = f'{temp_dir}/swath{swath}.slc'
            slc_par = f'{temp_dir}/swath{swath}.slc.par'
            slc_tops_par = f'{temp_dir}/swath{swath}.slc.tops.par'

            run(f'par_S1_SLC {tiff} {annotation_xml} {calibration_xml} {noise_xml} {slc_par} {slc_image} '
                f'{slc_tops_par}')
            if orbit_file:
                run(f'S1_OPOD_vec {slc_par} {orbit_file}')

            with open(slc_tab, 'a') as f:
                f.write(f'{slc_image} {slc_par} {slc_tops_par}\n')

        mli_image = f'{pol}.mli'
        mli_par = f'{pol}.mli.par'
        run(f'multi_look_ScanSAR {slc_tab} {mli_image} {mli_par} {looks * 5} {looks}')

    return mli_image, mli_par


def apply_speckle_filter(mli_image, mli_par, looks):
    log.info('Applying enhanced Lee speckle filter')
    width = getParameter(mli_par, 'range_samples')
    with NamedTemporaryFile() as temp_file:
        run(f'enh_lee {mli_image} {temp_file.name} {width} {looks} 1 7 7')
        shutil.copy(temp_file.name, mli_image)


def create_area_geotiff(data_in, lookup_table, mli_par, dem_par, output_name):
    width_in = getParameter(mli_par, 'range_samples')
    width_out = getParameter(dem_par, 'width')
    nlines_out = getParameter(dem_par, 'nlines')

    with NamedTemporaryFile() as temp_file:
        run(f'geocode_back {data_in} {width_in} {lookup_table} {temp_file.name} {width_out} {nlines_out} 2')
        run(f'data2geotiff {dem_par} {temp_file.name} 2 {output_name}')


def create_browse_images(out_dir, out_name, pol):
    pol_amp_tif = f'{pol}-amp.tif'
    outfile = f'{out_dir}/{out_name}'
    with NamedTemporaryFile() as rescaled_tif:
        byteSigmaScale(pol_amp_tif, rescaled_tif.name)
        makeAsfBrowse(rescaled_tif.name, outfile)

    for file_type in ['inc_map', 'dem', 'area']:
        tif = f'{out_dir}/{out_name}_{file_type}.tif'
        if os.path.exists(tif):
            outfile = f'{out_dir}/{out_name}_{file_type}'
            with NamedTemporaryFile() as rescaled_tif:
                byteSigmaScale(tif, rescaled_tif.name)
                makeAsfBrowse(rescaled_tif.name, outfile)

    shapefile = f'{out_dir}/{out_name}_shape.shp'
    raster_boundary2shape(pol_amp_tif, None, shapefile, use_closing=False, pixel_shift=True, fill_holes=True)


def append_additional_log_files(log_file, pattern):
    for additional_log_file in sorted(glob(pattern)):
        with open(additional_log_file) as f:
            content = f.read()
        with open(log_file, 'a') as f:
            f.write('==============================================\n')
            f.write(f'Log: {additional_log_file}\n')
            f.write('==============================================\n')
            f.write(content)


def rtc_sentinel_gamma(safe_dir: str, resolution: float = 30.0, radiometry: str = 'gamma0', scale: str = 'power',
                       speckle_filter: bool = False, dem_matching: bool = False, include_dem: bool = False,
                       include_inc_map: bool = False, include_scattering_area: bool = False, include_rgb: bool = False,
                       dem: str = None, bbox: List[float] = None, looks: int = None, skip_cross_pol: bool = False,
                       dem_name: str = 'copernicus') -> str:
    """Creates a Radiometrically Terrain-Corrected (RTC) product from a Sentinel-1 scene using GAMMA software.

    Args:
        safe_dir: Path to the Sentinel-1 .SAFE directory to process.
        resolution: Pixel size of the output images.
        radiometry: Radiometry of the output backscatter image(s); `gamma0` or `sigma0`.
        scale: Scale of the output backscatter image(s); `decibel`, `power`, or `amplitude`.
        speckle_filter: Apply an enhanced Lee speckle filter.
        dem_matching: Attempt to co-register the image to the DEM.
        include_dem: Include the DEM GeoTIFF in the output package.
        include_inc_map: Include the incidence angle GeoTIFF in the output package.
        include_scattering_area: Include the local scattering area GeoTIFF in the output package.
        include_rgb: Include an RGB decomposition GeoTIFF in the output package.  This setting is ignored when
            processing a single-polarization product or when `skip_cross_pol` is selected.
        dem: Path to the DEM to use for RTC processing. Must be a GeoTIFF in a UTM projection. A DEM will be selected
            automatically if not provided.
        bbox: Subset the output images to the given lat/lon bounding box: `[lon_min, lat_min, lon_max, lat_max]`.
            `bbox` is ignored if `dem` is provided.
        looks: Number of azimuth looks to take. Will be selected automatically if not specified.  Range and filter looks
            are selected automatically based on azimuth looks and product type.
        skip_cross_pol: Do not include the co-polarization backscatter GeoTIFF in the output package.
        dem_name: DEM to use for RTC processing; `copernicus` or `legacy`. `dem_name` is ignored if `dem` is provided.

    Returns:
        product_name: Name of the output product directory
    """

    safe_dir = safe_dir.strip('/')
    granule = os.path.splitext(os.path.basename(safe_dir))[0]
    granule_type = get_granule_type(granule)
    polarizations = get_polarizations(granule, skip_cross_pol)

    try:
        orbit_file, _ = downloadSentinelOrbitFile(granule)
    except OrbitDownloadError as e:
        log.warning(e)
        log.warning(f'Proceeding using original predicted orbit data included with {granule}')
        orbit_file = None

    product_name = get_product_name(granule, orbit_file, resolution, radiometry, scale, speckle_filter, dem_matching)
    if looks is None:
        looks = get_looks(granule_type, resolution)

    os.mkdir(product_name)
    log_file = configure_log_file(f'{product_name}/{product_name}.log')
    log_parameters(safe_dir, resolution, radiometry, scale, speckle_filter, dem_matching, include_dem, include_inc_map,
                   include_scattering_area, include_rgb, orbit_file, product_name, dem_name)

    log.info('Preparing DEM')
    dem_image, dem_par, dem_type = prepare_dem(safe_dir, dem_name, bbox, dem)

    for pol in polarizations:
        mli_image, mli_par = prepare_mli_image(safe_dir, granule_type, pol, orbit_file, looks)
        if speckle_filter:
            apply_speckle_filter(mli_image, mli_par, looks * 30)

        if pol == polarizations[0]:
            log.info('Generating initial geocoding lookup table and simulating SAR image from the DEM')
            run(f'mk_geo_radcal2 {mli_image} {mli_par} {dem_image} {dem_par} dem_seg dem_seg.par . corrected '
                f'{resolution} 0 -q')

            if dem_matching:
                log.info('Determining co-registration offsets (DEM matching)')
                try:
                    run(f'mk_geo_radcal2 {mli_image} {mli_par} {dem_image} {dem_par} dem_seg dem_seg.par . '
                        f'corrected {resolution} 1 -q')
                    run(f'mk_geo_radcal2 {mli_image} {mli_par} {dem_image} {dem_par} dem_seg dem_seg.par . '
                        f'corrected {resolution} 2 -q')
                    check_coregistration('mk_geo_radcal_2.log', 'corrected.diff_par', pixel_size=resolution)
                except (ExecuteError, CoregistrationError):
                    log.warning('Co-registration offsets are too large; defaulting to dead reckoning')
                    if os.path.isfile('corrected.diff_par'):
                        os.remove('corrected.diff_par')

        log.info(f'Generating terrain geocoded {pol.upper()} image and performing pixel area correction')
        radiometry_flag = int(radiometry == 'gamma0')
        run(f'mk_geo_radcal2 {mli_image} {mli_par} {dem_image} {dem_par} dem_seg dem_seg.par . corrected '
            f'{resolution} 3 -q -c {radiometry_flag}')
        shutil.move('mk_geo_radcal_3.log', f'mk_geo_radcal_3_{pol}.log')

        power_tif = f'{pol}-power.tif'
        shutil.move('corrected_cal_map.mli.tif', power_tif)

        tmp_tif = createAmp(power_tif, nodata=0)
        amp_tif = f'{pol}-amp.tif'
        shutil.move(tmp_tif, amp_tif)

        output_tif = f'{product_name}/{product_name}_{pol.upper()}.tif'
        if scale == 'power':
            shutil.copy(power_tif, output_tif)
        elif scale == 'decibel':
            decibel_tif = create_decibel_tif(power_tif)
            shutil.copy(decibel_tif, output_tif)
        else:
            shutil.copy(amp_tif, output_tif)

    log.info('Collecting output GeoTIFFs')
    run(f'data2geotiff dem_seg.par corrected.ls_map 5 {product_name}/{product_name}_ls_map.tif')
    if include_dem:
        with NamedTemporaryFile() as temp_file:
            run(f'data2geotiff dem_seg.par dem_seg 2 {temp_file.name}')
            gdal.Translate(f'{product_name}/{product_name}_dem.tif', temp_file.name, outputType=gdalconst.GDT_Int16)
    if include_inc_map:
        run(f'data2geotiff dem_seg.par corrected.inc_map 2 {product_name}/{product_name}_inc_map.tif')
    if include_scattering_area:
        create_area_geotiff('corrected_gamma0.pix', 'corrected_1.map_to_rdc', mli_par, 'dem_seg.par',
                            f'{product_name}/{product_name}_area.tif')
    if len(polarizations) == 2:
        pol_power_tif = f'{polarizations[0]}-power.tif'
        cpol_power_tif = f'{polarizations[1]}-power.tif'
        rgb_tif = f'{product_name}/{product_name}_rgb.tif'
        rtc2color(pol_power_tif, cpol_power_tif, -24, rgb_tif, cleanup=True)
        makeAsfBrowse(rgb_tif, f'{product_name}/{product_name}_rgb')
        if not include_rgb:
            os.remove(rgb_tif)

    # do pixel shift if needed
    if is_shift(mli_par, 'dem_seg.par', power_tif)[0]:
        for tif_file in glob(f'{product_name}/*.tif'):
            set_pixel_as_point(tif_file, shift_origin=True)

    cogify_dir(directory=product_name)

    log.info('Generating browse images and metadata files')
    create_browse_images(product_name, product_name, polarizations[0])
    create_metadata_file_set_rtc(
        product_dir=Path(product_name),
        granule_name=granule,
        dem_name=dem_type,
        processing_date=datetime.now(timezone.utc),
        looks=looks,
        plugin_name=hyp3_gamma.__name__,
        plugin_version=hyp3_gamma.__version__,
        processor_name='GAMMA',
        processor_version=gamma_version(),
    )
    for pattern in ['*inc_map*png*', '*inc_map*kmz', '*dem*png*', '*dem*kmz', '*area*png*', '*area*kmz']:
        for f in glob(f'{product_name}/{pattern}'):
            os.remove(f)

    append_additional_log_files(log_file, 'mk_geo_radcal_*.log')
    return product_name


def main():
    """Main entrypoint"""
    parser = ArgumentParser(
        prog='rtc_sentinel.py',
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('safe_dir', help='Path to the Sentinel-1 .SAFE directory to process.')
    parser.add_argument('--resolution', type=float, default=30.0, help='Pixel size of the output images.')
    parser.add_argument('--radiometry', choices=('gamma0', 'sigma0'), default='gamma0',
                        help='Radiometry of the output backscatter image(s)')
    parser.add_argument('--scale', choices=('power', 'decibel', 'amplitude'), default='power',
                        help='Scale of the output backscatter image(s)')
    parser.add_argument('--speckle-filter', action='store_true', help='Apply an enhanced Lee speckle filter.')
    parser.add_argument('--dem-matching', action='store_true', help='Attempt to co-register the image to the DEM.')
    parser.add_argument('--include-dem', action='store_true', help='Include the DEM GeoTIFF in the output package.')
    parser.add_argument('--include-inc-map', action='store_true',
                        help='Include the incidence angle GeoTIFF in the output package.')
    parser.add_argument('--include-scattering-area', action='store_true',
                        help='Include the local scattering area GeoTIFF in the output package.')

    group = parser.add_mutually_exclusive_group()
    parser.add_argument('--include-rgb', action='store_true',
                        help='Include an RGB decomposition GeoTIFF in the output package.')
    group.add_argument('--skip-cross-pol', action='store_true',
                       help='Do not include the co-polarization backscatter GeoTIFF in the output package.')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dem', help='Path to the DEM to use for RTC processing. Must be a GeoTIFF in a UTM projection.'
                                     ' A DEM will be selected automatically if not provided.')
    group.add_argument('--dem-name', choices=('copernicus', 'legacy'), default='copernicus',
                       help='DEM to use for RTC processing.')

    parser.add_argument('--bbox', type=float, nargs=4, metavar=('LON_MIN', 'LAT_MIN', 'LON_MAX', 'LAT_MAX'),
                        help='Subset the output images to the given lat/lon bounding box. Ignored if --dem is '
                             'provided.')
    parser.add_argument('--looks', type=int,
                        help='Number of azimuth looks to take. Will be selected automatically if not specified.  Range '
                             'and filter looks are selected automatically based on azimuth looks and product type.')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    log.info('===================================================================')
    log.info('                Sentinel RTC Program - Starting')
    log.info('===================================================================')

    if zipfile.is_zipfile(args.safe_dir):
        args.safe_dir = unzip_granule(args.safe_dir)

    rtc_sentinel_gamma(safe_dir=args.safe_dir,
                       resolution=args.resolution,
                       radiometry=args.radiometry,
                       scale=args.scale,
                       speckle_filter=args.speckle_filter,
                       dem_matching=args.dem_matching,
                       include_dem=args.include_dem,
                       include_inc_map=args.include_inc_map,
                       include_scattering_area=args.include_scattering_area,
                       include_rgb=args.include_rgb,
                       dem=args.dem,
                       bbox=args.bbox,
                       looks=args.looks,
                       skip_cross_pol=args.skip_cross_pol,
                       dem_name=args.dem_name)

    log.info('===================================================================')
    log.info('                Sentinel RTC Program - Completed')
    log.info('===================================================================')


if __name__ == '__main__':
    main()

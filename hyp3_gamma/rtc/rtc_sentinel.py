"""Create a Radiometrically Terrain-Corrected (RTC) image from a  Sentinel-1 scene sing GAMMA software"""

import logging
import os
import shutil
import zipfile
from argparse import ArgumentParser
from datetime import datetime, timezone
from glob import glob
from math import isclose
from pathlib import Path
from secrets import token_hex
from tempfile import NamedTemporaryFile

from hyp3_metadata import create_metadata_file_set
from hyp3lib import ExecuteError, GranuleError
from hyp3lib.area2point import fix_geotiff_locations
from hyp3lib.byteSigmaScale import byteSigmaScale
from hyp3lib.createAmp import createAmp
from hyp3lib.execute import execute
from hyp3lib.getDemFor import getDemFile
from hyp3lib.getParameter import getParameter
from hyp3lib.get_orb import downloadSentinelOrbitFile
from hyp3lib.makeAsfBrowse import makeAsfBrowse
from hyp3lib.make_cogs import cogify_dir
from hyp3lib.raster_boundary2shape import raster_boundary2shape
from hyp3lib.rtc2color import rtc2color
from hyp3lib.system import gamma_version
from hyp3lib.utm2dem import utm2dem
from lxml import etree

import hyp3_gamma
from hyp3_gamma.rtc.check_coreg import CoregistrationError, check_coregistration
from hyp3_gamma.util import unzip_granule

log = logging.getLogger()


def get_product_name(granule_name, orbit_file=None, resolution=30.0, gamma0=True, power=True,
                     filtered=False, matching=False):
    platform = granule_name[0:3]
    beam_mode = granule_name[4:6]
    polarization = granule_name[14:16]
    date_time = granule_name[17:32]
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

    g = 'g' if gamma0 else 's'
    p = 'p' if power else 'a'
    f = 'f' if filtered else 'n'
    m = 'm' if matching else 'd'

    product_name = f'{platform}_{beam_mode}_{date_time}_{polarization}{o}_RTC{res}_G_{g}{p}u{f}e{m}_{product_id}'
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


def log_program_start(parameters):
    log.info('*** Sentinel RTC Program - Starting ***')
    for key, value in parameters.items():
        log.info(f'    {key}: {value}')


def get_polarizations(safe_dir):
    mapping = {
        'SH': ('hh', ),
        'SV': ('vv', ),
        'DH': ('hh', 'hv'),
        'DV': ('vv', 'vh'),
    }
    key = safe_dir[14:16]
    polarizations = mapping.get(key)

    if not polarizations:
        raise GranuleError(f'Could not determine polarization(s) from {safe_dir}')

    return polarizations


def run(cmd):
    execute(cmd, uselogging=True)


def get_burst_count(annotation_xml):
    root = etree.parse(annotation_xml)
    return root.find('.//burstList').attrib['count']


def create_area_geotiff(data_in, lookup_table, mli_par, dem_par, output_name):
    width_in = getParameter(mli_par, 'range_samples')
    width_out = getParameter(dem_par, 'width')
    nlines_out = getParameter(dem_par, 'nlines')

    with NamedTemporaryFile() as temp_file:
        run(f'geocode_back {data_in} {width_in} {lookup_table} {temp_file.name} {width_out} {nlines_out} 2')
        run(f'data2geotiff {dem_par} {temp_file.name} 2 {output_name}')


def create_browse_images(out_dir, out_name, polarizations):
    pol_amp_tif = f'{polarizations[0]}-amp.tif'

    if len(polarizations) > 1:
        cpol_amp_tif = f'{polarizations[1]}-amp.tif'
        threshold = -24
        outfile = f'{out_dir}/{out_name}_rgb'
        with NamedTemporaryFile() as rgb_tif:
            rtc2color(pol_amp_tif, cpol_amp_tif, threshold, rgb_tif.name, amp=True, cleanup=True)
            makeAsfBrowse(rgb_tif.name, outfile)

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

    pol_tif = f'{out_dir}/{out_name}_{polarizations[0].upper()}.tif'
    shapefile = f'{out_dir}/{out_name}_shape.shp'
    raster_boundary2shape(pol_tif, None, shapefile, use_closing=False, pixel_shift=True, fill_holes=True)


def rtc_sentinel_gamma(safe_dir, dem=None, resolution=30.0, gamma0=True, power=True, speckle_filter=False,
                       dem_matching=False, include_dem=False, include_inc_map=False, include_scattering_area=False):
    granule = os.path.splitext(os.path.basename(safe_dir))[0]
    granule_type = get_granule_type(granule)
    polarizations = get_polarizations(granule)
    orbit_file, _ = downloadSentinelOrbitFile(granule)
    product_name = get_product_name(granule, orbit_file, resolution, gamma0, power, speckle_filter, dem_matching)
    looks = get_looks(granule_type, resolution)

    os.mkdir(product_name)
    configure_log_file(f'{product_name}/{product_name}.log')
    log_program_start(locals())

    log.info('\nPreparing DEM')
    if dem is None:
        dem, dem_type = getDemFile(safe_dir, 'dem.tif', post=resolution)
    else:
        dem_type = 'unknown'
    dem_image = 'dem.image'
    dem_par = 'dem.par'
    utm2dem(dem, dem_image, dem_par)

    for pol in polarizations:

        log.info(f'\nGenerating multi-looked {pol.upper()} image')
        if granule_type == 'GRDH':
            annotation_xml = f'{safe_dir}/annotation/*-{pol}-*.xml'
            calibration_xml = f'{safe_dir}/annotation/calibration/calibration*-{pol}-*.xml'
            noise_xml = f'{safe_dir}/annotation/calibration/noise*-{pol}-*.xml'
            tiff = f'{safe_dir}/measurement/*-{pol}-*.tiff'

            run(f'par_S1_GRD {tiff} {annotation_xml} {calibration_xml} {noise_xml} ingested.par ingested')
            run(f'S1_OPOD_vec ingested.par {orbit_file}')
            run(f'multi_look_MLI ingested ingested.par multilooked multilooked.par {looks} {looks} - - - 1')
        elif granule_type == 'SLC':
            burst_tab = ''
            slc_tab = ''
            for swath in (1, 2, 3):
                annotation_xml = glob(f'{safe_dir}/annotation/*-iw{swath}-slc-{pol}-*.xml')[0]
                calibration_xml = f'{safe_dir}/annotation/calibration/calibration-*-iw{swath}-slc-{pol}-*.xml'
                noise_xml = f'{safe_dir}/annotation/calibration/noise-*-iw{swath}-slc-{pol}-*.xml'
                tiff = f'{safe_dir}/measurement/*-iw{swath}-slc-{pol}-*.tiff'

                run(f'par_S1_SLC {tiff} {annotation_xml} {calibration_xml} {noise_xml} {swath}.par {swath}.slc '
                    f'{swath}.tops.par')
                run(f'S1_OPOD_vec {swath}.par {orbit_file}')

                slc_tab += f'{swath}.slc {swath}.par {swath}.tops.par\n'
                burst_tab += f'1 {get_burst_count(annotation_xml)}\n'

            with open('SLC1_tab', 'w') as f:
                f.write(slc_tab)
            with open('burst_tab', 'w') as f:
                f.write(burst_tab)

            run('SLC_copy_ScanSAR SLC1_tab SLC2_tab burst_tab')
            run(f'SLC_mosaic_S1_TOPS SLC2_tab multilooked multilooked.par {looks*5} {looks}')
            run(f'multi_look_ScanSAR SLC2_tab multilooked multilooked.par {looks*5} {looks}')

        if speckle_filter:
            log.info('\nApplying enhanced Lee speckle filter')
            width = getParameter('multilooked.par', 'range_samples')
            run(f'enh_lee multilooked filtered {width} {looks*30} 1 7 7')
            shutil.move('filtered', 'multilooked')

        if pol == polarizations[0]:
            log.info('\nGenerating initial geocoding lookup table and simulating SAR image from the DEM')
            run(f'mk_geo_radcal2 multilooked multilooked.par {dem_image} {dem_par} dem_seg dem_seg.par . corrected '
                f'{resolution} 0 -q')

            if dem_matching:
                log.info('\nDetermining co-registration offsets (DEM matching)')
                try:
                    run(f'mk_geo_radcal2 multilooked multilooked.par {dem_image} {dem_par} dem_seg dem_seg.par . '
                        f'corrected {resolution} 1 -q')
                    run(f'mk_geo_radcal2 multilooked multilooked.par {dem_image} {dem_par} dem_seg dem_seg.par . '
                        f'corrected {resolution} 2 -q')
                    check_coregistration('mk_geo_radcal_2.log', 'corrected.diff_par', resolution)
                except (ExecuteError, CoregistrationError):
                    log.warning('Co-registration offsets are large; defaulting to dead reckoning')
                    if os.path.isfile('corrected.diff_par'):
                        os.remove('corrected.diff_par')

        log.info(f'\nGenerating terrain geocoded {pol.upper()} image and performing pixel area correction')
        run(f'mk_geo_radcal2 multilooked multilooked.par {dem_image} {dem_par} dem_seg dem_seg.par . corrected '
            f'{resolution} 3 -q -c {int(gamma0)}')

        power_tif = 'corrected_cal_map.mli.tif'
        amp_tif = createAmp(power_tif, nodata=0)
        if power:
            shutil.copy(power_tif, f'{product_name}/{product_name}_{pol.upper()}.tif')
        else:
            shutil.copy(amp_tif, f'{product_name}/{product_name}_{pol.upper()}.tif')
        shutil.move(amp_tif, f'{pol}-amp.tif')

    log.info('\nCollecting output GeoTIFFs')
    run(f'data2geotiff dem_seg.par corrected.ls_map 5 {product_name}/{product_name}_ls_map.tif')
    if include_dem:
        run(f'data2geotiff dem_seg.par dem_seg 2 {product_name}/{product_name}_dem.tif')
    if include_inc_map:
        run(f'data2geotiff dem_seg.par corrected.inc_map 2 {product_name}/{product_name}_inc_map.tif')
    if include_scattering_area:
        create_area_geotiff('corrected_gamma0.pix', 'corrected_1.map_to_rdc', 'multilooked.par', 'dem_seg.par',
                            f'{product_name}/{product_name}_area.tif')

    fix_geotiff_locations(dir=product_name)
    cogify_dir(directory=product_name)

    log.info('\nGenerating browse images and metadata files')
    create_browse_images(product_name, product_name, polarizations)
    create_metadata_file_set(
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

    log.info('*** Sentinel RTC Program - Completed ***')
    return product_name


def main():
    """Main entrypoint"""
    parser = ArgumentParser(
        prog='rtc_sentinel.py',
        description=__doc__,
    )
    parser.add_argument('safe_dir', help='Name of the input .SAFE directory')
    parser.add_argument('--dem', '-d', help='Specify a DEM file to use - must be in UTM projection')
    parser.add_argument('--resolution', '-r', type=float, default=30.0, help='Desired output resolution')
    parser.add_argument('--radiometry', choices=['gamma0', 'sigma0'], help='Desired output radiometry')
    parser.add_argument('--scale', choices=['power', 'amplitude'], help='Desired output scale')
    parser.add_argument('--speckle-filter', '-f', action='store_true', help='Apply enhanced Lee filter')
    parser.add_argument('--dem-matching', '-m', action='store_true', help='Attempt DEM matching')
    parser.add_argument('--include-dem', action='store_true', help='Include the DEM geotiff in the output package')
    parser.add_argument('--include-inc-map', action='store_true',
                        help='Include the incidence angle geotiff in the output package')
    parser.add_argument('--include-scattering-area', action='store_true',
                        help='Include the scattering area geotiff in the output package')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    if zipfile.is_zipfile(args.safe_dir):
        log.info(f'Unzipping {args.safe_dir}')
        args.safe_dir = unzip_granule(args.safe_dir)

    rtc_sentinel_gamma(safe_dir=args.safe_dir,
                       dem=args.dem,
                       resolution=args.resolution,
                       gamma0=(args.radiometry == 'gamma0'),
                       power=(args.scale == 'power'),
                       speckle_filter=args.speckle_filter,
                       dem_matching=args.dem_matching,
                       include_dem=args.include_dem,
                       include_inc_map=args.include_inc_map,
                       include_scattering_area=args.include_scattering_area)


if __name__ == '__main__':
    main()

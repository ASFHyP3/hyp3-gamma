"""Create a Radiometrically Terrain-Corrected (RTC) image from a  Sentinel-1 scene sing GAMMA software"""

import logging
import os
import shutil
from glob import glob
from secrets import token_hex
from tempfile import NamedTemporaryFile

from hyp3lib import ExecuteError, GranuleError
from hyp3lib.area2point import fix_geotiff_locations
from hyp3lib.createAmp import createAmp
from hyp3lib.getDemFor import getDemFile
from hyp3lib.execute import execute
from hyp3lib.getParameter import getParameter
from hyp3lib.get_orb import downloadSentinelOrbitFile
from hyp3lib.make_cogs import cogify_dir
from hyp3lib.utm2dem import utm2dem
from lxml import etree

from hyp3_gamma.rtc.check_coreg import CoregistrationError, check_coreg

log = logging.getLogger()


def get_product_name(granule_name, orbit_file=None, resolution=30.0, gamma0=True, power=True,
                     filtered=False, matching=False):
    platform = granule_name[0:3]
    beam_mode = granule_name[4:6]
    polarization = granule_name[14:16]
    datetime = granule_name[17:32]
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

    product_name = f'{platform}_{beam_mode}_{datetime}_{polarization}{o}_RTC{res}_G_{g}{p}u{f}e{m}_{product_id}'
    return product_name


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


def create_area_geotiff(data_in, lookup_table, mli_par, dem_par, output_name):
    log.info(f'Creating scattering area geotiff: {output_name}')
    width_in = getParameter(mli_par, 'range_samples')
    width_out = getParameter(dem_par, 'width')
    nlines_out = getParameter(dem_par, 'nlines')

    with NamedTemporaryFile() as temp_file:
        execute(f'geocode_back {data_in} {width_in} {lookup_table} {temp_file.name} {width_out} {nlines_out} 2')
        execute(f'data2geotiff {dem_par} {temp_file.name} 2 {output_name}')


def rtc_sentinel_gamma(safe_dir,  resolution=30.0, gamma0=True, power=True, dem_matching=False,
                       speckle_filter=False, include_dem=False, include_inc_map=False, include_scattering_area=False):

    orbit_file, _ = downloadSentinelOrbitFile(safe_dir)
    name = get_product_name(safe_dir, orbit_file, resolution, gamma0, power, speckle_filter, dem_matching)
    os.mkdir(name)

    dem = 'dem.image'
    dem_par = 'dem.par'
    with NamedTemporaryFile() as temp_file:
        temp_dem_file, dem_type = getDemFile(safe_dir, temp_file.name, post=resolution)
        utm2dem(temp_dem_file, dem, dem_par)

    for pol in get_polarizations(safe_dir):

        if 'GRD' in safe_dir:
            looks = 6
            annotation_xml = f'{safe_dir}/annotation/*-{pol}-*.xml'
            calibration_xml = f'{safe_dir}/annotation/calibration/calibration*-{pol}-*.xml'
            noise_xml = f'{safe_dir}/annotation/calibration/noise*-{pol}-*.xml'
            tiff = f'{safe_dir}/measurement/*-{pol}-*.tiff'

            execute(f'par_S1_GRD {tiff} {annotation_xml} {calibration_xml} {noise_xml} ingested.par ingested')
            execute(f'S1_OPOD_vec ingested.par {orbit_file}')
            execute(f'multi_look_MLI ingested ingested.par multilooked multilooked.par {looks} {looks} - - - 1')
        elif 'SLC' in safe_dir:
            looks = 3
            burst_counts = []
            for swath in (1, 2, 3):
                annotation_xml = glob(f'{safe_dir}/annotation/*-iw{swath}-slc-{pol}-*.xml')[0]
                calibration_xml = f'{safe_dir}/annotation/calibration/calibration-*-iw{swath}-slc-{pol}-*.xml'
                noise_xml = f'{safe_dir}/annotation/calibration/noise-*-iw{swath}-slc-{pol}-*.xml'
                tiff = f'{safe_dir}/measurement/*-iw{swath}-slc-{pol}-*.tiff'

                execute(f'par_S1_SLC {tiff} {annotation_xml} {calibration_xml} {noise_xml} {swath}.par {swath}.slc {swath}.tops.par')
                execute(f'S1_OPOD_vec {swath}.par {orbit_file}')

                root = etree.parse(annotation_xml)
                burst_counts += root.find('.//burstList').attrib['count']

            with open('SLC1_tab', 'w') as f:
                for swath in (1, 2, 3):
                    f.write(f'{swath}.slc {swath}.par {swath}.tops.par\n')
            with open('burst_tab', 'w') as f:
                for burst_count in burst_counts:
                    f.write(f'1 {burst_count}\n')
            execute('SLC_copy_S1_TOPS SLC1_tab SLC2_tab burst_tab')

            execute(f'SLC_mosaic_S1_TOPS SLC2_tab multilooked multilooked.par {looks*5} {looks}')
            execute(f'multi_look_ScanSAR SLC2_tab multilooked multilooked.par {looks*5} {looks}')
        else:
            raise NotImplementedError('Only GRD and SLC are implemented')

        if speckle_filter:
            width = getParameter('multilooked.par', 'range_samples')
            execute(f'enh_lee multilooked filtered {width} {looks*30} 1 7 7')
            shutil.move('filtered', 'multilooked')

        if not os.path.exists('dem_seg'):
            execute(f'mk_geo_radcal2 multilooked multilooked.par {dem} {dem_par} dem_seg dem_seg.par . corrected {resolution} 0 -q')

            if dem_matching:
                try:
                    execute(f'mk_geo_radcal2 multilooked multilooked.par {dem} {dem_par} dem_seg dem_seg.par . corrected {resolution} 1 -q')
                    execute(f'mk_geo_radcal2 multilooked multilooked.par {dem} {dem_par} dem_seg dem_seg.par . corrected {resolution} 2 -q')
                    check_coreg(None, resolution, max_offset=75, max_error=2.0)
                except (ExecuteError, CoregistrationError):
                    log.warning('Coregistration check has failed; defaulting to dead reckoning')
                    os.remove('corrected.diff_par')

        execute(f'mk_geo_radcal2 multilooked multilooked.par {dem} {dem_par} dem_seg dem_seg.par . corrected {resolution} 3 -q -c {int(gamma0)}')

        if power:
            shutil.copy('corrected_cal_map.mli.tif', f'{name}/{name}_{pol.upper()}.tif')
        else:
            createAmp('corrected_cal_map.mli.tif', nodata=0)
            shutil.move('corrected_cal_map.mli_amp.tif', f'{name}/{name}_{pol.upper()}.tif')

    execute(f'data2geotiff dem_seg.par corrected.ls_map 5 {name}/{name}_ls_map.tif')
    if include_dem:
        execute(f'data2geotiff dem_seg.par dem_seg 2 {name}/{name}_dem.tif')
    if include_inc_map:
        execute(f'data2geotiff dem_seg.par corrected.inc_map 2 {name}/{name}_inc_map.tif')
    if include_scattering_area:
        create_area_geotiff('corrected_gamma0.pix', 'corrected_1.map_to_rdc', 'multilooked.par', 'dem_seg.par', f'{name}/{name}_area.tif')

    fix_geotiff_locations(dir=name)
    cogify_dir(directory=name)

    return name

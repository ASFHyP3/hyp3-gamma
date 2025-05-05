"""Process Sentinel-1 data into interferograms using GAMMA"""

import argparse
import glob
import logging
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_hex

from hyp3lib import GranuleError
from hyp3lib.SLC_copy_S1_fullSW import SLC_copy_S1_fullSW
from hyp3lib.execute import execute
from hyp3lib.par_s1_slc_single import par_s1_slc_single
from hyp3lib.system import gamma_version
from lxml import etree, objectify
from s1_orbits import fetch_for_scene

import hyp3_gamma
from hyp3_gamma.get_parameter import get_parameter
from hyp3_gamma.insar.getDemFileGamma import get_dem_file_gamma
from hyp3_gamma.insar.interf_pwr_s1_lt_tops_proc import interf_pwr_s1_lt_tops_proc
from hyp3_gamma.insar.unwrapping_geocoding import unwrapping_geocoding
from hyp3_gamma.make_asf_browse import make_asf_browse
from hyp3_gamma.metadata import create_metadata_file_set_insar


log = logging.getLogger(__name__)


def get_bursts(mydir, name):
    back = os.getcwd()
    os.chdir(os.path.join(mydir, 'annotation'))

    total_bursts = None
    time = []
    for myfile in os.listdir('.'):
        if name in myfile:
            root = etree.parse(myfile)
            for coord in root.iter('azimuthAnxTime'):
                text = coord.text
                assert text is not None
                time.append(float(text))
            for count in root.iter('burstList'):
                total_bursts = int(count.attrib['count'])

    os.chdir(back)

    return time, total_bursts


def get_burst_overlaps(reference_dir, secondary_dir):
    log.info(f'Calculating burst overlaps; in directory {os.getcwd()}')
    burst_tab1 = '%s_burst_tab' % reference_dir[17:25]
    burst_tab2 = '%s_burst_tab' % secondary_dir[17:25]

    with open(burst_tab1, 'w') as f1:
        with open(burst_tab2, 'w') as f2:
            for name in ['001.xml', '002.xml', '003.xml']:
                time1, total_bursts1 = get_bursts(reference_dir, name)
                log.info(f'total_bursts1, time1 {total_bursts1} {time1}')
                time2, total_bursts2 = get_bursts(secondary_dir, name)
                log.info(f'total_bursts2, time2 {total_bursts2} {time2}')
                cnt = 1
                start1 = 0
                start2 = 0
                found = 0
                x = time1[0]
                for y in time2:
                    if abs(x - y) < 0.20:
                        log.info('Found burst match at 1 %s' % cnt)
                        found = 1
                        start1 = 1
                        start2 = cnt
                    cnt += 1

                if found == 0:
                    y = time2[0]
                    cnt = 1
                    for x in time1:
                        if abs(x - y) < 0.20:
                            log.info('Found burst match at %s 1' % cnt)
                            start1 = cnt
                            start2 = 1
                        cnt += 1

                size1 = total_bursts1 - start1 + 1
                size2 = total_bursts2 - start2 + 1

                if size1 > size2:
                    size = size2
                else:
                    size = size1

                f1.write('%s %s\n' % (start1, start1 + size - 1))
                f2.write('%s %s\n' % (start2, start2 + size - 1))

    return burst_tab1, burst_tab2


def get_copol(granule_name):
    polarization = granule_name[14:16]
    if polarization in ['SV', 'DV']:
        return 'vv'
    if polarization in ['SH', 'DH']:
        return 'hh'
    raise GranuleError(f'Cannot determine co-polarization of granule {granule_name}')


def least_precise_orbit_of(orbits):
    if any([orb is None for orb in orbits]):
        return 'O'
    if any(['RESORB' in orb for orb in orbits]):
        return 'R'
    return 'P'


def timedetla_in_days(delta):
    seconds_in_a_day = 60 * 60 * 24
    total_seconds = abs(delta.total_seconds())
    return round(total_seconds / seconds_in_a_day)


def get_product_name(
    reference_name,
    secondary_name,
    orbit_files,
    pixel_spacing=80,
    apply_water_mask=False,
):
    plat1 = reference_name[2]
    plat2 = secondary_name[2]

    datetime1 = reference_name[17:32]
    datetime2 = secondary_name[17:32]

    ref_datetime = datetime.strptime(datetime1, '%Y%m%dT%H%M%S')
    sec_datetime = datetime.strptime(datetime2, '%Y%m%dT%H%M%S')
    days = timedetla_in_days(ref_datetime - sec_datetime)

    pol1 = reference_name[15:16]
    pol2 = secondary_name[15:16]
    orb = least_precise_orbit_of(orbit_files)
    mask = 'w' if apply_water_mask else 'u'
    product_id = token_hex(2).upper()

    return (
        f'S1{plat1}{plat2}_{datetime1}_{datetime2}_{pol1}{pol2}{orb}{days:03}_INT{pixel_spacing}_G_{mask}eF_'
        f'{product_id}'
    )


def get_orbit_parameters(reference_file):
    """input: manifest.safe in the reference.safe directory
    return: {"orbitnumber": orbitnumber, "relative_orbitnumber":relative_orbitnumber,
    "cyclenumber":cyclenumber, "pass_direction":pass_direction}
    """
    file = os.path.join(reference_file, 'manifest.safe')

    if os.path.exists(file):
        with open(file, 'rb') as f:
            xml = f.read()
            root = objectify.fromstring(xml)

            meta = root.find('metadataSection')
            assert meta is not None
            xmldata = meta.find('*[@ID="measurementOrbitReference"]').metadataWrap.xmlData  # type: ignore[union-attr]
            orbit = xmldata.find('safe:orbitReference', root.nsmap)
            orbitnumber = orbit.find('safe:orbitNumber', root.nsmap)
            relative_orbitnumber = orbit.find('safe:relativeOrbitNumber', root.nsmap)
            cyclenumber = orbit.find('safe:cycleNumber', root.nsmap)
            pass_direction = (
                orbit.find('safe:extension', root.nsmap)
                .find('s1:orbitProperties', root.nsmap)
                .find('s1:pass', root.nsmap)
            )

            return {
                'orbitnumber': orbitnumber,
                'relative_orbitnumber': relative_orbitnumber,
                'cyclenumber': cyclenumber,
                'pass_direction': pass_direction,
            }

    return {
        'orbitnumber': None,
        'relative_orbitnumber': None,
        'cyclenumber': None,
        'pass_direction': None,
    }


def move_output_files(
    output,
    reference,
    prod_dir,
    long_output,
    include_displacement_maps,
    include_look_vectors,
    include_wrapped_phase,
    include_inc_map,
    include_dem,
):
    inName = f'{reference}.mli.geo.tif'
    outName = f'{os.path.join(prod_dir, long_output)}_amp.tif'
    shutil.copy(inName, outName)

    inName = 'water_mask.tif'
    outName = f'{os.path.join(prod_dir, long_output)}_water_mask.tif'
    shutil.copy(inName, outName)

    inName = f'{output}.cc.geo.tif'
    outName = f'{os.path.join(prod_dir, long_output)}_corr.tif'
    if os.path.isfile(inName):
        shutil.copy(inName, outName)

    inName = f'{output}.adf.unw.geo.tif'
    outName = f'{os.path.join(prod_dir, long_output)}_unw_phase.tif'
    shutil.copy(inName, outName)

    if include_wrapped_phase:
        inName = f'{output}.diff0.man.adf.geo.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_wrapped_phase.tif'
        shutil.copy(inName, outName)

    if include_dem:
        inName = f'{output}.dem.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_dem.tif'
        shutil.copy(inName, outName)

    if include_displacement_maps:
        inName = f'{output}.los.disp.geo.org.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_los_disp.tif'
        shutil.copy(inName, outName)
        inName = f'{output}.vert.disp.geo.org.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_vert_disp.tif'
        shutil.copy(inName, outName)

    if include_inc_map:
        inName = f'{output}.inc.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_inc_map.tif'
        shutil.copy(inName, outName)
        inName = f'{output}.inc_ell.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_inc_map_ell.tif'
        shutil.copy(inName, outName)

    if include_look_vectors:
        inName = f'{output}.lv_theta.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_lv_theta.tif'
        shutil.copy(inName, outName)
        inName = f'{output}.lv_phi.tif'
        outName = f'{os.path.join(prod_dir, long_output)}_lv_phi.tif'
        shutil.copy(inName, outName)

    make_asf_browse(
        f'{output}.diff0.man.adf.bmp.geo.tif',
        f'{os.path.join(prod_dir, long_output)}_color_phase',
        use_nn=True,
    )

    make_asf_browse(
        f'{output}.adf.unw.geo.bmp.tif',
        f'{os.path.join(prod_dir, long_output)}_unw_phase',
        use_nn=True,
    )


def make_parameter_file(
    mydir,
    parameter_file_name,
    alooks,
    rlooks,
    dem_source,
    coords,
    ref_point_info,
    phase_filter_parameter,
):
    res = 20 * int(alooks)

    reference_date = mydir[:15]
    secondary_date = mydir[17:]
    reference_date_short = reference_date[:8]

    log.info(f'In directory {os.getcwd()} looking for file with date {reference_date_short}')
    reference_file = glob.glob('*%s*.SAFE' % reference_date)[0]
    secondary_file = glob.glob('*%s*.SAFE' % secondary_date)[0]

    parfile = f'{reference_date_short}.mli.par'
    erad_nadir = get_parameter(parfile, 'earth_radius_below_sensor')
    erad_nadir = erad_nadir.split()[0]
    sar_to_earth_center = get_parameter(parfile, 'sar_to_earth_center')
    sar_to_earth_center = sar_to_earth_center.split()[0]
    height = float(sar_to_earth_center) - float(erad_nadir)
    near_slant_range = get_parameter(parfile, 'near_range_slc')
    near_slant_range = near_slant_range.split()[0]
    center_slant_range = get_parameter(parfile, 'center_range_slc')
    center_slant_range = center_slant_range.split()[0]
    far_slant_range = get_parameter(parfile, 'far_range_slc')
    far_slant_range = far_slant_range.split()[0]

    with open('baseline.log') as f:
        for line in f:
            if 'estimated baseline perpendicular component' in line:
                # FIXME: RE is overly complicated here. this is two simple string splits
                t = re.split(':', line)
                s = re.split(r'\s+', t[1])
                baseline = float(s[1])

    back = os.getcwd()
    os.chdir(os.path.join(reference_file, 'annotation'))

    utctime = None
    for myfile in os.listdir('.'):
        if '001.xml' in myfile:
            root = etree.parse(myfile)
            for coord in root.iter('productFirstLineUtcTime'):
                utc = coord.text
                assert utc is not None
                log.info(f'Found utc time {utc}')
                t = utc.split('T')
                log.info(f'{t}')
                s = t[1].split(':')
                log.info(f'{s}')
                utctime = ((int(s[0]) * 60 + int(s[1])) * 60) + float(s[2])
    os.chdir(back)

    heading = None
    name = f'{reference_date[:8]}.mli.par'
    with open(name) as f:
        for line in f:
            if 'heading' in line:
                t = re.split(':', line)
                # FIXME: RE is overly complicated here. this is two simple string splits
                s = re.split(r'\s+', t[1])
                heading = float(s[1])

    reference_orbit_parameters = get_orbit_parameters(reference_file)
    secondary_orbit_parameters = get_orbit_parameters(secondary_file)

    reference_file = reference_file.replace('.SAFE', '')
    secondary_file = secondary_file.replace('.SAFE', '')

    phase_filter = 'adf' if phase_filter_parameter > 0.0 else 'none'

    with open(parameter_file_name, 'w') as f:
        f.write('Reference Granule: %s\n' % reference_file)
        f.write('Secondary Granule: %s\n' % secondary_file)
        f.write('Reference Pass Direction: %s\n' % reference_orbit_parameters['pass_direction'])
        f.write('Reference Orbit Number: %s\n' % reference_orbit_parameters['orbitnumber'])
        f.write('Secondary Pass Direction: %s\n' % secondary_orbit_parameters['pass_direction'])
        f.write('Secondary Orbit Number: %s\n' % secondary_orbit_parameters['orbitnumber'])
        f.write('Baseline: %s\n' % baseline)
        f.write('UTC time: %s\n' % utctime)
        f.write('Heading: %s\n' % heading)
        f.write('Spacecraft height: %s\n' % height)
        f.write('Earth radius at nadir: %s\n' % erad_nadir)
        f.write('Slant range near: %s\n' % near_slant_range)
        f.write('Slant range center: %s\n' % center_slant_range)
        f.write('Slant range far: %s\n' % far_slant_range)
        f.write('Range looks: %s\n' % rlooks)
        f.write('Azimuth looks: %s\n' % alooks)
        f.write(f'INSAR phase filter: {phase_filter}\n')
        f.write('Phase filter parameter: %s\n' % phase_filter_parameter)
        f.write('Resolution of output (m): %s\n' % res)
        f.write('Range bandpass filter: no\n')
        f.write('Azimuth bandpass filter: no\n')
        f.write('DEM source: %s\n' % dem_source)
        f.write('DEM resolution (m): %s\n' % (res * 2))
        f.write('Unwrapping type: mcf\n')
        f.write('Phase at reference point: %s\n' % ref_point_info['refoffset'])
        f.write('Azimuth line of the reference point in SAR space: %s\n' % coords['row_s'])
        f.write('Range pixel of the reference point in SAR space: %s\n' % coords['col_s'])
        f.write('Y coordinate of the reference point in the map projection: %s\n' % coords['y'])
        f.write('X coordinate of the reference point in the map projection: %s\n' % coords['x'])
        f.write('Latitude of the reference point (WGS84): %s\n' % coords['lat'])
        f.write('Longitude of the reference point (WGS84): %s\n' % coords['lon'])
        f.write('Unwrapping threshold: none\n')
        f.write('Speckle filter: no\n')


def insar_sentinel_gamma(
    reference_file,
    secondary_file,
    rlooks=20,
    alooks=4,
    include_look_vectors=False,
    include_displacement_maps=False,
    include_wrapped_phase=False,
    include_inc_map=False,
    include_dem=False,
    apply_water_mask=False,
    phase_filter_parameter=0.6,
):
    log.info('\n\nSentinel-1 differential interferogram creation program\n')

    wrk = os.getcwd()
    reference_date = reference_file[17:32]
    reference = reference_file[17:25]
    secondary_date = secondary_file[17:32]
    secondary = secondary_file[17:25]

    igramName = f'{reference_date}_{secondary_date}'
    if 'IW_SLC__' not in reference_file:
        raise GranuleError(f'Reference file {reference_file} is not of type IW_SLC!')
    if 'IW_SLC__' not in secondary_file:
        raise GranuleError(f'Secondary file {secondary_file} is not of type IW_SLC!')

    pol = get_copol(reference_file)
    log.info(f'Processing the {pol} polarization')

    # Ingest the data files into gamma format
    log.info('Starting par_S1_SLC')
    orbit_files = []
    for granule in (reference_file, secondary_file):
        log.info(f'Downloading orbit file for {granule}')
        orbit_file = str(fetch_for_scene(granule))
        log.info(f'Got orbit file {orbit_file} from s1_orbits')
        par_s1_slc_single(granule, pol, os.path.abspath(orbit_file))
        orbit_files.append(orbit_file)

    # Fetch the DEM file
    log.info('Getting a DEM file')
    dem_source = 'GLO-30'
    dem_pixel_size = int(alooks) * 40  # typically 160 or 80; IFG pixel size will be half the DEM pixel size (80 or 40)
    get_dem_file_gamma('big.dem', 'big.par', reference_file, pixel_size=dem_pixel_size)
    log.info(f'Got dem of type {dem_source}')

    # Figure out which bursts overlap between the two swaths
    burst_tab1, burst_tab2 = get_burst_overlaps(reference_file, secondary_file)
    log.info(f'Finished calculating overlap - in directory {os.getcwd()}')
    shutil.move(burst_tab1, f'{reference}/{burst_tab1}')
    shutil.move(burst_tab2, f'{secondary}/{burst_tab2}')

    # Mosaic the swaths together and copy SLCs over
    log.info('Starting SLC_copy_S1_fullSW.py')
    os.chdir(reference)
    SLC_copy_S1_fullSW(
        wrk,
        reference,
        'SLC_TAB',
        burst_tab1,
        mode=1,
        dem='big',
        dempath=wrk,
        raml=rlooks,
        azml=alooks,
    )
    os.chdir('..')
    os.chdir(secondary)
    SLC_copy_S1_fullSW(wrk, secondary, 'SLC_TAB', burst_tab2, mode=2, raml=rlooks, azml=alooks)
    os.chdir('..')

    # Interferogram creation, matching, refinement
    log.info('Starting interf_pwr_s1_lt_tops_proc.py 0')
    hgt = f'DEM/HGT_SAR_{rlooks}_{alooks}'
    interf_pwr_s1_lt_tops_proc(reference, secondary, hgt, rlooks=rlooks, alooks=alooks, iterations=3, step=0)

    log.info('Starting interf_pwr_s1_lt_tops_proc.py 1')
    interf_pwr_s1_lt_tops_proc(reference, secondary, hgt, rlooks=rlooks, alooks=alooks, step=1)

    log.info('Starting interf_pwr_s1_lt_tops_proc.py 2')
    interf_pwr_s1_lt_tops_proc(reference, secondary, hgt, rlooks=rlooks, alooks=alooks, iterations=3, step=2)

    g = open('offsetfit3.log')
    offset = '1.0'
    for line in g:
        if 'final azimuth offset poly. coeff.:' in line:
            offset = line.split(':')[1]
    if float(offset) > 0.02:
        log.error(f'ERROR: Found azimuth offset of {offset}!')
        sys.exit(1)
    else:
        log.info(f'Found azimuth offset of {offset}!')

    output = f'{reference}_{secondary}'

    log.info('Starting s1_coreg_overlap')
    execute(
        f'ScanSAR_coreg_overlap.py SLC1_tab SLC2R_tab {output} {output}.off.it {output}.off.it.corrected',
        uselogging=True,
    )

    log.info('Starting interf_pwr_s1_lt_tops_proc.py 3')
    interf_pwr_s1_lt_tops_proc(reference, secondary, hgt, rlooks=rlooks, alooks=alooks, step=3)

    # Perform phase unwrapping and geocoding of results
    log.info('Starting phase unwrapping and geocoding')

    coords, ref_point_info = unwrapping_geocoding(
        reference,
        secondary,
        step='man',
        rlooks=rlooks,
        alooks=alooks,
        alpha=phase_filter_parameter,
        apply_water_mask=apply_water_mask,
    )

    # Generate metadata
    log.info('Collecting metadata and output files')

    os.chdir(wrk)

    # Move the outputs to the product directory
    pixel_spacing = int(alooks) * 20
    product_name = get_product_name(reference_file, secondary_file, orbit_files, pixel_spacing, apply_water_mask)
    os.mkdir(product_name)
    move_output_files(
        output,
        reference,
        product_name,
        product_name,
        include_displacement_maps,
        include_look_vectors,
        include_wrapped_phase,
        include_inc_map,
        include_dem,
    )

    reference_granule = os.path.splitext(os.path.basename(reference_file))[0]
    secondary_granule = os.path.splitext(os.path.basename(secondary_file))[0]

    create_metadata_file_set_insar(
        product_dir=Path(product_name),
        reference_granule_name=reference_granule,
        secondary_granule_name=secondary_granule,
        processing_date=datetime.now(timezone.utc),
        looks=f'{rlooks}x{alooks}',
        dem_name='GLO-30',
        water_mask_applied=apply_water_mask,
        plugin_name=hyp3_gamma.__name__,
        plugin_version=hyp3_gamma.__version__,
        processor_name='GAMMA',
        processor_version=gamma_version(),
        ref_point_coords=coords,
        phase_filter_parameter=phase_filter_parameter,
    )

    execute(
        f'base_init {reference}.slc.par {secondary}.slc.par - - base > baseline.log',
        uselogging=True,
    )

    make_parameter_file(
        igramName,
        f'{product_name}/{product_name}.txt',
        alooks,
        rlooks,
        dem_source,
        coords,
        ref_point_info,
        phase_filter_parameter,
    )

    log.info('Done!!!')
    return product_name


def main():
    """Main entrypoint"""
    parser = argparse.ArgumentParser(
        prog='ifm_sentinel.py',
        description=__doc__,
    )
    parser.add_argument('reference', help='Reference input file')
    parser.add_argument('secondary', help='Secondary input file')
    parser.add_argument('-r', '--rlooks', default=20, help='Number of range looks (def=20)')
    parser.add_argument('-a', '--alooks', default=4, help='Number of azimuth looks (def=4)')
    parser.add_argument('-d', action='store_true', help='Add DEM file to product bundle')
    parser.add_argument(
        '-i',
        action='store_true',
        help='Create local and ellipsoidal incidence angle maps',
    )
    parser.add_argument('-l', action='store_true', help='Create look vector theta and phi files')
    parser.add_argument(
        '-s',
        action='store_true',
        help='Create both line of sight and vertical displacement files',
    )
    parser.add_argument('-w', action='store_true', help='Create wrapped phase file')
    parser.add_argument('-m', action='store_true', help='Apply water mask')
    parser.add_argument(
        '-p',
        '--phase-filter-parameter',
        default=0.6,
        help='Adaptive phase filter parameter',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO,
    )

    insar_sentinel_gamma(
        args.reference,
        args.secondary,
        rlooks=args.rlooks,
        alooks=args.alooks,
        include_look_vectors=args.l,
        include_displacement_maps=args.s,
        include_wrapped_phase=args.w,
        include_inc_map=args.i,
        include_dem=args.d,
        apply_water_mask=args.m,
        phase_filter_parameter=args.phase_filter_parameter,
    )


if __name__ == '__main__':
    main()

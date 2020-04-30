def meta_init():
    m = {}
    m['meta_version'] = ('3.6', '')

    # General block
    m['general.name'] = ('???', 'File name')
    m['general.sensor'] = ('???', 'Imaging satellite')
    m['general.sensor_name'] = ('???', 'Imaging sensor')
    m['general.mode'] = ('???', 'Imaging mode')
    m['general.receiving_station'] = ('???', 'Downlinking ground station')
    m['general.processor'] = ('???', 'Name and Version of Processor')
    m['general.data_type'] = ('???', 'Type of samples (e.g. REAL64)')
    m['general.image_data_type'] = \
        ('???', 'Image data type (e.g. AMPLITUDE_IMAGE')
    m['general.radiometry'] = ('AMPLITUDE', 'Radiometry (e.g. SIGMA)')
    m['general.acquisition_date'] = ('???', 'Acquisition date of the data')
    m['general.orbit'] = ('-999999999', 'Orbit Number for this datatake')
    m['general.orbit_direction'] = ('?', "Ascending 'A', or descending 'D'")
    m['general.frame'] = ('-999999999', 'Frame for this image [-1 if n/a]')
    m['general.band_count'] = ('1', 'Number of bands in image')
    m['general.bands'] = ('???', 'Band of the sensor')
    m['general.line_count'] = ('-999999999', 'Number of lines in image')
    m['general.sample_count'] = ('-999999999', 'Number of samples in image')
    m['general.start_line'] = \
        ('-999999999', 'First line relative to original image')
    m['general.start_sample'] = \
        ('-999999999', 'First sample relative to original image')
    m['general.x_pixel_size'] = ('NaN', 'Range pixel size [m]')
    m['general.y_pixel_size'] = ('NaN', 'Azimuth pixel size [m]')
    m['general.center_latitude'] = ('NaN', 'Approximate image center latitude')
    m['general.center_longitude'] = ('NaN', 'Approximate image center longitude')
    m['general.re_major'] = ('NaN', 'Major (equator) Axis of earth [m]')
    m['general.re_minor'] = ('NaN', 'Minor (polar) Axis of earth [m]')
    m['general.bit_error_rate'] = ('NaN', 'Fraction of bits which are in error')
    m['general.missing_lines'] = \
        ('-999999999', 'Number of missing lines in data take')
    m['general.no_data'] = ('NaN', 'Value indicating no data for a pixel')

    return m


def meta_init_sar(m):
    m['sar.polarization'] = ('???', 'Signal polarization')
    m['sar.image_type'] = \
        ('?', '[S=slant range; G=ground range; P=map projected; R=georeferenced]')
    m['sar.look_direction'] = \
        ('?', 'SAR Satellite look direction [R=right; L=left]')
    m['sar.azimuth_look_count'] = \
        ('-999999999', 'Number of looks in azimuth direction')
    m['sar.range_look_count'] = \
        ('-999999999', 'Number of looks in range direction')
    m['sar.multilook'] = ('-999999999', 'Image multilooked? [1=yes; 0=no]')
    m['sar.deskewed'] = \
        ('-999999999', 'Image moved to zero doppler? [1=yes; 0=no]')
    m['sar.original_line_count'] = \
        ('-999999999', 'Number of lines in original image')
    m['sar.original_sample_count'] = \
        ('-999999999', 'Number of samples in original image')
    m['sar.line_increment'] = ('1', 'Line increment for sampling')
    m['sar.sample_increment'] = ('1', 'Sample increment for sampling')
    m['sar.range_time_per_pixel'] = ('NaN', 'Time per pixel in range [s]')
    m['sar.azimuth_time_per_pixel'] = ('NaN', 'Time per pixel in azimuth [s]')
    m['sar.slant_range_first_pixel'] = ('NaN', 'Slant range to first pixel [m]')
    m['sar.slant_shift'] = ('0', 'Error correction factor, in slant range [m]')
    m['sar.time_shift'] = ('0', 'Error correction factor, in time [s]')
    m['sar.wavelength'] = ('NaN', 'SAR carrier wavelength [m]')
    m['sar.prf'] = ('NaN', 'Pulse Repetition Frequency [Hz]')
    m['sar.earth_radius'] = ('NaN', 'Earth radius at scene center [m]')
    m['sar.earth_radius_pp'] = \
        ('NaN', 'Earth radius used by the PP during L0 processsing. [m]')
    m['sar.satellite_height'] = \
        ('NaN', "Satellite height from earth's center [m]")
    m['sar.satellite_binary_time'] = ('???', 'Satellite Binary Time')
    m['sar.satellite_clock_time'] = ('???', 'Satellite Clock Time (UTC)')
    m['sar.dopRangeCen'] = ('NaN', 'Range doppler centroid [Hz]')
    m['sar.dopRangeLin'] = ('NaN', 'Range doppler per range pixel [Hz/pixel]')
    m['sar.dopRangeQuad'] = \
        ('NaN', 'Range doppler per range pixel sq. [Hz/(pixel^2)]')
    m['sar.dopAzCen'] = ('NaN', 'Azimuth doppler centroid [Hz]')
    m['sar.dopAzLin'] = ('NaN', 'Azimuth doppler per azimuth pixel [Hz/pixel]')
    m['sar.dopAzQuad'] = \
        ('NaN', 'Azimuth doppler per azimuth pixel sq. [Hz/(pixel^2)]')
    m['sar.pitch'] = ('NaN', 'Platform pitch [degrees]')
    m['sar.roll'] = ('NaN', 'Platform roll [degrees]')
    m['sar.yaw'] = ('NaN', 'Platform yaw [degrees]')
    m['sar.azimuth_bandwidth'] = ('NaN', 'Azimuth processing bandwidth [Hz]')
    m['sar.chirp_rate'] = ('NaN', 'Chirp rate [Hz/sec]')
    m['sar.pulse_duration'] = ('NaN', 'Pulse duration [s]')
    m['sar.range_samp_rate'] = ('NaN', 'Range sampling rate [Hz]')
    m['sar.incid_a(0)'] = ('NaN', 'Incidence angle transformation parameter')
    m['sar.incid_a(1)'] = ('NaN', 'Incidence angle transformation parameter')
    m['sar.incid_a(2)'] = ('NaN', 'Incidence angle transformation parameter')
    m['sar.incid_a(3)'] = ('NaN', 'Incidence angle transformation parameter')
    m['sar.incid_a(4)'] = ('NaN', 'Incidence angle transformation parameter')
    m['sar.incid_a(5)'] = ('NaN', 'Incidence angle transformation parameter')

    return m


def meta_init_location(m):
    # Location block
    m['location.lat_start_near_range'] = \
        ('NaN', 'Latitude at image start in near range')
    m['location.lon_start_near_range'] = \
        ('NaN', 'Longitude at image start in near range')
    m['location.lat_start_far_range'] = \
        ('NaN', 'Latitude at image start in far range')
    m['location.lon_start_far_range'] = \
        ('NaN', 'Longitude at image start in far range')
    m['location.lat_end_near_range'] = \
        ('NaN', 'Latitude at image end in near range')
    m['location.lon_end_near_range'] = \
        ('NaN', 'Longitude at image end in near range')
    m['location.lat_end_far_range'] = \
        ('NaN', 'Latitude at image end in far range')
    m['location.lon_end_far_range'] = \
        ('NaN', 'Longitude at image end in far range')

    return m


def get_meta_sections(m):
    key_names = (
        'general', 'sar', 'optical', 'thermal', 'projection',
        'transform', 'airsar', 'uavsar', 'statistics',
        'state', 'location', 'calibration', 'colormap',
        'doppler', 'insar', 'dem', 'latlon', 'quality',
    )

    s = {}
    for key_name in key_names:
        if key_name in m.keys():
            s[key_name] = True
        else:
            s[key_name] = False

    return s


def writeStr(outF, m, key):
    value = m[key][0]
    comment = m[key][1]
    line = ''
    name = key.split('.')
    for i in range(1, len(name)):
        line += '    '
    line += name[len(name) - 1] + ': ' + value
    while len(line) < 42 + (len(name) - 1) * 4:
        line += ' '
    line += ' # ' + comment + '\n'
    outF.write(line)


def write_asf_meta(m, metaFile):
    # Get metadata sections
    s = get_meta_sections(m)

    # Write header comments
    with open(metaFile, 'w') as outF:
        outF.write('# This file contains the metadata for satellite capture file '
                   'of the same base name.\n')
        outF.write("#      '?' is likely an unknown single character value.\n")
        outF.write("#      '???' is likely an unknown string of characters.\n")
        outF.write("#      '-999999999' is likely an unknown integer value.\n")
        outF.write("#      'nan' is likely an unknown Real value.\n\n")
        outF.write('meta_version: ' + m['meta_version'][0] + '\n\n')

        # General block
        outF.write('general {                                  # Begin parameters'
                   ' generally used in remote sensing\n')
        writeStr(outF, m, 'general.name')
        writeStr(outF, m, 'general.sensor')
        writeStr(outF, m, 'general.sensor_name')
        writeStr(outF, m, 'general.mode')
        writeStr(outF, m, 'general.receiving_station')
        writeStr(outF, m, 'general.processor')
        writeStr(outF, m, 'general.data_type')
        writeStr(outF, m, 'general.image_data_type')
        writeStr(outF, m, 'general.radiometry')
        writeStr(outF, m, 'general.acquisition_date')
        writeStr(outF, m, 'general.orbit')
        writeStr(outF, m, 'general.orbit_direction')
        writeStr(outF, m, 'general.frame')
        writeStr(outF, m, 'general.band_count')
        writeStr(outF, m, 'general.bands')
        writeStr(outF, m, 'general.line_count')
        writeStr(outF, m, 'general.sample_count')
        writeStr(outF, m, 'general.start_line')
        writeStr(outF, m, 'general.start_sample')
        writeStr(outF, m, 'general.x_pixel_size')
        writeStr(outF, m, 'general.y_pixel_size')
        writeStr(outF, m, 'general.center_latitude')
        writeStr(outF, m, 'general.center_longitude')
        writeStr(outF, m, 'general.re_major')
        writeStr(outF, m, 'general.re_minor')
        writeStr(outF, m, 'general.bit_error_rate')
        writeStr(outF, m, 'general.missing_lines')
        writeStr(outF, m, 'general.no_data')
        outF.write('}                                          # End general\n\n')

        # SAR block
        if s['sar']:
            outF.write('sar {                                      # Begin '
                       'parameters used specifically in SAR imaging\n')
            writeStr(outF, m, 'sar.polarization')
            writeStr(outF, m, 'sar.image_type')
            writeStr(outF, m, 'sar.look_direction')
            writeStr(outF, m, 'sar.azimuth_look_count')
            writeStr(outF, m, 'sar.range_look_count')
            writeStr(outF, m, 'sar.multilook')
            writeStr(outF, m, 'sar.deskewed')
            writeStr(outF, m, 'sar.original_line_count')
            writeStr(outF, m, 'sar.original_sample_count')
            writeStr(outF, m, 'sar.line_increment')
            writeStr(outF, m, 'sar.sample_increment')
            writeStr(outF, m, 'sar.range_time_per_pixel')
            writeStr(outF, m, 'sar.azimuth_time_per_pixel')
            writeStr(outF, m, 'sar.slant_range_first_pixel')
            writeStr(outF, m, 'sar.slant_shift')
            writeStr(outF, m, 'sar.time_shift')
            writeStr(outF, m, 'sar.wavelength')
            writeStr(outF, m, 'sar.prf')
            writeStr(outF, m, 'sar.earth_radius')
            writeStr(outF, m, 'sar.earth_radius_pp')
            writeStr(outF, m, 'sar.satellite_height')
            writeStr(outF, m, 'sar.satellite_binary_time')
            writeStr(outF, m, 'sar.satellite_clock_time')
            writeStr(outF, m, 'sar.dopRangeCen')
            writeStr(outF, m, 'sar.dopRangeLin')
            writeStr(outF, m, 'sar.dopRangeQuad')
            writeStr(outF, m, 'sar.dopAzCen')
            writeStr(outF, m, 'sar.dopAzLin')
            writeStr(outF, m, 'sar.dopAzQuad')
            writeStr(outF, m, 'sar.pitch')
            writeStr(outF, m, 'sar.roll')
            writeStr(outF, m, 'sar.yaw')
            writeStr(outF, m, 'sar.azimuth_bandwidth')
            writeStr(outF, m, 'sar.chirp_rate')
            writeStr(outF, m, 'sar.pulse_duration')
            writeStr(outF, m, 'sar.range_samp_rate')
            writeStr(outF, m, 'sar.incid_a(0)')
            writeStr(outF, m, 'sar.incid_a(1)')
            writeStr(outF, m, 'sar.incid_a(2)')
            writeStr(outF, m, 'sar.incid_a(3)')
            writeStr(outF, m, 'sar.incid_a(4)')
            writeStr(outF, m, 'sar.incid_a(5)')
            outF.write('}                                          # End sar\n\n')

        # Projection block
        if s['projection']:
            outF.write('projection {                               # Map Projection'
                       ' parameters\n')
            writeStr(outF, m, 'projection.type')
            writeStr(outF, m, 'projection.startX')
            writeStr(outF, m, 'projection.startY')
            writeStr(outF, m, 'projection.perX')
            writeStr(outF, m, 'projection.perY')
            writeStr(outF, m, 'projection.units')
            writeStr(outF, m, 'projection.hem')
            writeStr(outF, m, 'projection.spheroid')
            writeStr(outF, m, 'projection.re_major')
            writeStr(outF, m, 'projection.re_minor')
            writeStr(outF, m, 'projection.datum')
            writeStr(outF, m, 'projection.height')
            if 'projection.param.utm.zone' in m.keys():
                outF.write('    param {                                    # '
                           'Projection specific parameters\n')
                outF.write('        utm {                                      # '
                           'Begin Universal Transverse Mercator Projection\n')
                writeStr(outF, m, 'projection.param.utm.zone')
                writeStr(outF, m, 'projection.param.utm.false_easting')
                writeStr(outF, m, 'projection.param.utm.false_northing')
                writeStr(outF, m, 'projection.param.utm.latitude')
                writeStr(outF, m, 'projection.param.utm.longitude')
                writeStr(outF, m, 'projection.param.utm.scale_factor')
                outF.write('        }                                          # End '
                           'utm\n')
                outF.write('    }                                          # End '
                           'param\n\n')
            elif 'projection.param.ps.slat' in m.keys():
                outF.write('    param {                                    # '
                           'Projection specific parameters\n')
                outF.write('        ps {                                       # '
                           'Begin Polar Stereographic Projection\n')
                writeStr(outF, m, 'projection.param.ps.slat')
                writeStr(outF, m, 'projection.param.ps.slon')
                writeStr(outF, m, 'projection.param.ps.false_easting')
                writeStr(outF, m, 'projection.param.ps.false_northing')
                outF.write('        }                                          # End '
                           'ps\n')
                outF.write('    }                                          # End '
                           'param\n\n')
            outF.write('}                                          # End projection'
                       '\n')

        # Location block
        if s['location']:
            outF.write('location {                                 # Block '
                       'containing image corner coordinates\n')
            writeStr(outF, m, 'location.lat_start_near_range')
            writeStr(outF, m, 'location.lon_start_near_range')
            writeStr(outF, m, 'location.lat_start_far_range')
            writeStr(outF, m, 'location.lon_start_far_range')
            writeStr(outF, m, 'location.lat_end_near_range')
            writeStr(outF, m, 'location.lon_end_near_range')
            writeStr(outF, m, 'location.lat_end_far_range')
            writeStr(outF, m, 'location.lon_end_far_range')
            outF.write('}                                          # End location'
                       '\n\n')

    outF.close()

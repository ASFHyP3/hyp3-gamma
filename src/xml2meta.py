#!/usr/bin/python

import argparse
from argparse import RawTextHelpFormatter
import os
import sys
import lxml.etree as et
from osgeo import ogr
from osgeo import ogr, osr
import datetime
import scipy.constants as sc
from asf_utils import *
import logging
import asf.log


# establish a stub root logger to avoid syntax errors
# we'll configure this later on using asf.log
log = logging.getLogger()


def sentinel2meta(xmlFile):

  m = meta_init()
  m = meta_init_sar(m)
  m = meta_init_location(m)
  parser = et.XMLParser(remove_blank_text=True)
  meta = et.parse(xmlFile, parser)
  
  # Determine location and centroid
  ring = ogr.Geometry(ogr.wkbLinearRing)
  poly = ogr.Geometry(ogr.wkbPolygon)
  bounds = meta.xpath('//boundary')
  for bound in bounds:

    lat = bound.xpath('polygon/point[@id="1"]/lat')[0].text
    m['location.lat_start_near_range'] = \
      (lat, m['location.lat_start_near_range'][1])
    lon = bound.xpath('polygon/point[@id="1"]/lon')[0].text
    m['location.lon_start_near_range'] = \
      (lon, m['location.lon_start_near_range'][1])
    ring.AddPoint(float(lat), float(lon))

    lat = bound.xpath('polygon/point[@id="2"]/lat')[0].text
    m['location.lat_start_far_range'] = \
      (lat, m['location.lat_start_far_range'][1])
    lon = bound.xpath('polygon/point[@id="2"]/lon')[0].text
    m['location.lon_start_far_range'] = \
      (lon, m['location.lon_start_far_range'][1])
    ring.AddPoint(float(lat), float(lon))

    lat = bound.xpath('polygon/point[@id="3"]/lat')[0].text
    m['location.lat_end_far_range'] = \
      (lat, m['location.lat_end_near_range'][1])
    lon = bound.xpath('polygon/point[@id="3"]/lon')[0].text
    m['location.lon_end_far_range'] = \
      (lon, m['location.lon_end_near_range'][1])
    ring.AddPoint(float(lat), float(lon))

    lat = bound.xpath('polygon/point[@id="4"]/lat')[0].text
    m['location.lat_end_near_range'] = \
      (lat, m['location.lat_end_far_range'][1])
    lon = bound.xpath('polygon/point[@id="4"]/lon')[0].text
    m['location.lon_end_near_range'] = \
      (lon, m['location.lon_end_far_range'][1])
    ring.AddPoint(float(lat), float(lon))

    ring.CloseRings()
    poly.AddGeometry(ring)
    centroid = poly.Centroid()
    point = centroid.GetPoint(0)

  # General block  
  name = meta.xpath('/sentinel/metadata/image/file')[0].text
  m['general.name'] = (name, m['general.name'][1])
  sensor = meta.xpath('/sentinel/metadata/image/platform')[0].text
  m['general.sensor'] = (sensor, m['general.sensor'][1])
  sensor_name = meta.xpath('/sentinel/metadata/image/sensor')[0].text
  m['general.sensor_name'] = (sensor_name, m['general.sensor_name'][1])
  mode = meta.xpath('/sentinel/metadata/image/beam_mode')[0].text
  m['general.mode'] = (mode, m['general.mode'][1])
  processor = meta.xpath('/sentinel/processing/software')[0].text
  version = meta.xpath('/sentinel/processing/software_version')[0].text
  m['general.processor'] = \
    (processor + ' (' + version + ')', m['general.processor'][1])
  m['general.data_type'] = ('REAL32', m['general.data_type'][1])
  m['general.image_data_type'] = \
    ('AMPLITUDE_IMAGE', m['general.image_data_type'][1])
  m['general.radiometry'] = ('AMPLITUDE', m['general.radiometry'][1])
  acquisition_date = meta.xpath('/sentinel/extent/start_datetime')[0].text
  m['general.acquisition_date'] = \
    (acquisition_date, m['general.acquisition_date'][1])
  orbit = meta.xpath('/sentinel/metadata/image/absolute_orbit')[0].text
  m['general.orbit]'] = (orbit, m['general.orbit'][1])
  orbit_direction = \
    meta.xpath('/sentinel/metadata/image/flight_direction')[0].text
  if orbit_direction == 'ASCENDING':
    m['general.orbit_direction'] = ('A', m['general.orbit_direction'][1])
  elif orbit_direction == 'DESCENDING':
    m['general.orbit_direction'] = ('D', m['general.orbit_direction'][1])
  polarization = meta.xpath('/sentinel/metadata/image/polarization')[0].text
  if polarization == 'SH' or polarization == 'HH':
    m['general.band_count'] = ('1', m['general.band_count'][1])
    m['general.bands'] = ('HH', m['general.bands'][1])
  elif polarization == 'HV':
    m['general.band_count'] = ('1', m['general.band_count'][1])
    m['general.bands'] = ('HV', m['general.bands'][1])
  elif polarization == 'VH':
    m['general.band_count'] = ('1', m['general.band_count'][1])
    m['general.bands'] = ('VH', m['general.bands'][1])
  elif polarization == 'SV' or polarization == 'VV':
    m['general.band_count'] = ('1', m['general.band_count'][1])
    m['general.bands'] = ('VV', m['general.bands'][1])
  elif polarization == 'DH':
    m['general.band_count'] = ('2', m['general.band_count'][1])
    m['general.bands'] = ('HH,HV', m['general.bands'][1])
  elif polarization == 'DV':
    m['general.band_count'] = ('2', m['general.band_count'][1])
    m['general.bands'] = ('VV,VH', m['general.bands'][1])
  line_count = meta.xpath('/sentinel/metadata/image/height')[0].text
  m['general.line_count'] = (line_count, m['general.line_count'][1])
  sample_count = meta.xpath('/sentinel/metadata/image/width')[0].text
  m['general.sample_count'] = (sample_count, m['general.sample_count'][1])
  m['general.start_line'] = ('0', m['general.start_line'][1])
  m['general.start_sample'] = ('0', m['general.start_sample'][1])
  x_pixel_size = meta.xpath('/sentinel/metadata/image/x_spacing')[0].text
  m['general.x_pixel_size'] = (x_pixel_size, m['general.x_pixel_size'][1])
  y_pixel_size = meta.xpath('/sentinel/metadata/image/y_spacing')[0].text
  m['general.y_pixel_size'] = (y_pixel_size, m['general.y_pixel_size'][1])  
  m['general.center_latitude'] = \
    (str(point[0]), m['general.center_latitude'][1])
  m['general.center_longitude'] = \
    (str(point[1]), m['general.center_longitude'][1])
  # The spatial reference functionality works in Python 2.7
  # Hardwire axes for the moment
  # ref = osr.SpatialReference()
  # ref.ImportFromEPSG(4326)
  # m['general.re_major'] = (str(ref.GetSemiMajor()), m['general.re_major'][1])
  # m['general.re_minor'] = (str(ref.GetSemiMinor()), m['general.re_minor'][1])
  m['general.re_major'] = ('6378137.0', m['general.re_major'][1])
  m['general.re_minor'] = ('6356752.31425', m['general.re_minor'][1])
  
  # SAR block
  if polarization == 'SH' or polarization == 'HH':
    m['sar.polarization'] = ('HH', m['sar.polarization'][1])
  elif polarization == 'HV':
    m['sar.polarization'] = ('HV', m['sar.polarization'][1])
  elif polarization == 'VH':
    m['sar.polarization'] = ('VH', m['sar.polarization'][1])
  elif polarization == 'SV' or polarization == 'VV':
    m['sar.polarization'] = ('VV', m['sar.polarization'][1])
  elif polarization == 'DH':
    m['sar.polarization'] = ('HH,HV', m['sar.polarization'][1])
  elif polarization == 'DV':
    m['sar.polarization'] = ('VV,VH', m['sar.polarization'][1])
  product_type = meta.xpath('/sentinel/metadata/image/product_type')[0].text
  if product_type == 'RAW' or product_type == 'SLC':
    m['sar.image_type'] = ('S', m['sar.image_type'][1])
    m['multilook'] = ('0', m['multilook'][1])
  elif product_type == 'GRD':
    m['sar.image_type'] = ('G', m['sar.image_type'][1])
    m['sar.multilook'] = ('1', m['sar.multilook'][1])
  m['sar.look_direction'] = ('R', m['sar.look_direction'][1])
  '''
  Look counts are different for each beam in the ScanSAR imagery
  sar.azimuth_look_count
  sar.range_look_count
  '''
  m['sar.deskewed'] = ('1', m['sar.deskewed'][1])
  m['sar.original_line_count'] = \
    (m['general.line_count'][0], m['sar.original_line_count'][1])
  m['sar.original_sample_count'] = \
    (m['general.sample_count'][0], m['sar.original_sample_count'][1])
  m['sar.line_increment'] = ('1', m['sar.line_increment'][1])
  m['sar.sample_increment'] = ('1', m['sar.sample_increment'][1])
  '''
  range_time_per_pixel: 3.125e-08
  azimuth_time_per_pixel: 0.00091480755475
  slant_range_first_pixel: 853461.85215
  '''
  m['sar.slant_shift'] = ('0', m['sar.slant_shift'][1])
  m['sar.time_shift'] = ('0', m['sar.time_shift'][1])
  frequency = meta.xpath('/sentinel/metadata/image/radar_frequency')[0].text
  wavelength = sc.c/float(frequency)
  m['sar.wavelength'] = (str(wavelength), m['sar.wavelength'][1])
  '''
  prf: 2141.3276231
  earth_radius: 6362363.0798
  satellite_height: 7065911.9034
  dopRangeCen: 50.5405526
  dopRangeLin: -0.0002221
  dopRangeQuad: 0
  dopAzCen: 50.5405526
  dopAzLin: 0
  dopAzQuad: 0
  pitch: NaN
  roll: NaN
  yaw: NaN
  azimuth_bandwidth: 1516.25
  chirp_rate: 0
  pulse_duration: 2.7e-05
  range_samp_rate: 32000000
  incid_a(0): 288.16310464
  incid_a(1): -0.98116986722
  incid_a(2): 0.00069761807297
  incid_a(3): 9.9271558273e-07
  incid_a(4): -1.5988761359e-09
  incid_a(5): 6.0266559732e-13
  '''
  
  return m


if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='xml2meta',
    description='Converts an XML metadata file into an ASF metadata file',
    formatter_class=RawTextHelpFormatter)
  parser.add_argument('data', help='name of data source')
  parser.add_argument('xmlFile', help='name of the XML metadata file (input)')
  parser.add_argument('metaFile', help='name of the metadata file (output)')
  parser.add_argument('-s --screen', action = 'store_true', dest = 'screen', help = 'log to the console (as well as to syslog)')
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  args = parser.parse_args()
  log = asf.log.getLogger(screen = args.screen)

  if not os.path.exists(args.xmlFile):
    log.error('XML metadata file (%s) does not exist!' % args.xmlFile)
    sys.exit(1)

  if args.data == 'sentinel':
    log.info('Converting Sentinel XML file (%s) ...' % args.xmlFile)
    m = sentinel2meta(args.xmlFile)
    write_asf_meta(m, args.metaFile)
  else:
    log.error("Conversion for '%s' data not defined!" % args.data)

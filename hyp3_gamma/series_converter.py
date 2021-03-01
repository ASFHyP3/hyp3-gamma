"""Create a netcdf format data file using a single HyP3 RTC Gamma product"""

import argparse
import logging
import os
import re
from datetime import datetime

import numpy as np
import pycrs
import rasterio as rio
import rioxarray
import xarray as xr
from osgeo import gdal
from converter import gamma_to_netcdf
from converter import parse_asf_rtc_name


def create_output_file_name(infiles, start_time, last_time, prod_type, pixel_spacing):
    prod = prod_type[0:2]
    int_spacing = int(pixel_spacing)
    scene = parse_asf_rtc_name(infiles[0])
    gamsig = scene['radiometry'][0]
    amppower = scene['scale'][0]  
    if 'no' in scene['filtered']:
        filt = 'n'
    else:
        filt = 'f'
    name = f"S1_IW_{prod}{int_spacing}_{start_time}_{last_time}_G_{gamsig}{amppower}{filt}.nc"
    return(name)

def prepare_time_dimension(time_0_str, all_time, projected_data_set_1):

    # calculate milliseconds since first image in stack    
    time_0 = np.datetime64(time_0_str, 'ms').astype(np.float)

    # Set the times relative to the first frame
    new_times = []
    for i in range(0, len(all_time)):
        milliseconds_since = (np.datetime64(all_time[i], 'ms').astype(np.float)-time_0)
        new_times.append(milliseconds_since)

    projected_data_set_1 = projected_data_set_1.assign_coords(time=new_times)
    projected_data_set_1.time.attrs['axis'] = "T"
    projected_data_set_1.time.attrs['units'] = "milliseconds since {}".format(time_0_str)
    projected_data_set_1.time.attrs['calendar'] = "proleptic_gregorian"
    projected_data_set_1.time.attrs['long_name'] = "Time"


def series_to_netcdf(product_type, infiles, output_scale, pixel_spacing, drop_vars):
    infiles.sort
    projected_data_set_1 = gamma_to_netcdf(product_type, infiles[0], output_scale, pixel_spacing, drop_vars)
    all_time = [] 
    print(f"projected_data_set_1['acquisition_start_time'] {projected_data_set_1['acquisition_start_time']}")
    start = f'{projected_data_set_1.acquisition_start_time.values}'
    start_time = datetime(int(start[0:4]), int(start[4:6]), int(start[6:8]),
                          int(start[9:11]), int(start[11:13]), int(start[13:15]),0)
    time_0_str = start_time
    all_time.append(start_time)
    print(f'all_time = {all_time}')
    for cnt in np.arange(1, len(infiles)):
        projected_data_set_2 = gamma_to_netcdf(product_type, infiles[cnt], output_scale, pixel_spacing, drop_vars)
        last_time = f'{projected_data_set_2.acquisition_start_time.values}'
        frame_time = datetime(int(last_time[0:4]), int(last_time[4:6]), int(last_time[6:8]),
                             int(last_time[9:11]), int(last_time[11:13]), int(last_time[13:15]), 0)
        all_time.append(frame_time)
        print(f'all_time = {all_time}')
        projected_data_set_1 = xr.concat([projected_data_set_1, projected_data_set_2], dim='time')

    prepare_time_dimension(time_0_str, all_time, projected_data_set_1)
    outfile = create_output_file_name(infiles, start, last_time, product_type, pixel_spacing)
    projected_data_set_1.to_netcdf(outfile, unlimited_dims=['time'])

    logging.info('Successful Completion!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='series_converter.py',
                                     description='Converts a HyP3 RTC stack product from.tif format into netCDF',
                                     epilog='The log and README files must be in the same directory as the .tif')

    parser.add_argument('product_type', help='Type of data being stacked (RTC or INSAR)', metavar='InputType',
                        choices=['INSAR', 'RTC'])

    parser.add_argument('-d', '--drop_vars', help='Comma delimited list of variables to be dropped from the final stack',
                        metavar='DropVars')
    parser.add_argument('-o', '--output_scale', help='Output scale type\n', choices=['power', 'amp', 'dB'],
                        default='power')
    parser.add_argument('-p', '--pixel_spacing', help='Desired output pixel_spacing', type=float)
    parser.add_argument('infiles',nargs='*', help='Name of input geotiff files')
    args = parser.parse_args()

    if args.drop_vars:
        drop_list = [item for item in args.drop_vars.split(',')]
    else:
        drop_list = None

    logFile = 'series_to_netcdf_{}.log'.format(os.getpid())
    logging.basicConfig(filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info('Starting run')


    series_to_netcdf(args.product_type, args.infiles, args.output_scale, args.pixel_spacing, drop_list)


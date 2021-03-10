"""Create a netcdf format data file using a single HyP3 RTC Gamma product"""

import argparse
import logging
import os
from datetime import datetime

import numpy as np
import xarray as xr
from converter import gamma_to_netcdf
from converter import parse_asf_rtc_name
from hyp3lib.cutGeotiffsByLine import cutGeotiffsByLine


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


def prepare_time_dimension(time_0_str, all_time, ds1):

    # calculate seconds since first image in stack
    time_0 = np.datetime64(time_0_str, 's').astype(np.float)

    # Set the times relative to the first frame
    new_times = []
    for i in range(0, len(all_time)):
        seconds_since = (np.datetime64(all_time[i], 's').astype(np.float)-time_0)
        new_times.append(seconds_since)

    ds1 = ds1.assign_coords(time=new_times)
    ds1.time.attrs['axis'] = "T"
    ds1.time.attrs['units'] = "seconds since {}".format(time_0_str)
    ds1.time.attrs['calendar'] = "gregorian"
    ds1.time.attrs['long_name'] = 'time'
    ds1.time.attrs['standard_name'] = 'time'
    return ds1


def func(x):
    return(x)


def series_to_netcdf(product_type, infiles, output_scale, pixel_spacing, drop_vars):
    infiles.sort
 
    cut_files = cutGeotiffsByLine(infiles)
    ds1 = gamma_to_netcdf(product_type, cut_files[0], output_scale=output_scale,
                          pixel_spacing=pixel_spacing, drop_vars=drop_vars, write_file=False)

    # Get rid of spurious 'transverse_mercator' coordinate
    ds1 = ds1.reset_coords()
    all_time = []
    print(f"ds1['acquisition_start_time'] {ds1['acquisition_start_time']}")
    start = f'{ds1.acquisition_start_time.values}'
    start_time = datetime(int(start[0:4]), int(start[4:6]), int(start[6:8]),
                          int(start[9:11]), int(start[11:13]), int(start[13:15]), 0)
    time_0_str = start_time
    all_time.append(start_time)
    print(f'all_time = {all_time}')
    for cnt in np.arange(1, len(cut_files)):
        ds2 = gamma_to_netcdf(product_type, cut_files[cnt], output_scale=output_scale, 
                              pixel_spacing=pixel_spacing, drop_vars=drop_vars, write_file=False)

        # Get rid of spurious 'transverse_mercator' coordinate
        ds2 = ds2.reset_coords()

        last_time = f'{ds2.acquisition_start_time.values}'
        frame_time = datetime(int(last_time[0:4]), int(last_time[4:6]), int(last_time[6:8]),
                              int(last_time[9:11]), int(last_time[11:13]), int(last_time[13:15]), 0)
        all_time.append(frame_time)
        print(f'all_time = {all_time}')
        ds1 = xr.concat([ds1, ds2], dim='time')

    ds1 = prepare_time_dimension(time_0_str, all_time, ds1)

    # get rid of time dimension for projection
    ds1['transverse_mercator'] = ds1.transverse_mercator.reduce(func, keep_attrs=True)
    ds1['transverse_mercator'] = ds1.transverse_mercator[0]
    ds1['transverse_mercator'].attrs['standard_name'] = 'transverse_mercator'

    # write out the file 
    outfile = create_output_file_name(cut_files, start, last_time, product_type, pixel_spacing)
    ds1.to_netcdf(outfile, unlimited_dims=['time'])

    logging.info('Successful Completion!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='series_converter.py',
                                     description='Converts a HyP3 RTC stack product from.tif format into netCDF',
                                     epilog='The log and README files must be in the same directory as the .tif')

    parser.add_argument('product_type', help='Type of data being stacked (RTC or INSAR)', metavar='InputType',
                        choices=['INSAR', 'RTC'])

    parser.add_argument('-d', '--drop_vars', help='Comma delimited list of variables to be dropped from final stack',
                        metavar='DropVars')
    parser.add_argument('-o', '--output_scale', help='Output scale type\n', choices=['power', 'amp', 'dB'],
                        default='power')
    parser.add_argument('-p', '--pixel_spacing', help='Desired output pixel_spacing', type=float)
    parser.add_argument('infiles', nargs='*', help='Name of input geotiff files')
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

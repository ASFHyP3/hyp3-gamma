import numpy as np
from osgeo import gdal

from hyp3_gamma.rtc import gdal_file


def get_sigma_cutoffs(fi):
    file_handle = gdal.Open(fi)
    (x, y, trans, proj, data) = gdal_file.read(file_handle)
    data = data.astype(float)
    data[data == 0] = np.nan
    top = np.nanpercentile(data, 99)
    data[data > top] = top
    stddev = np.nanstd(data)
    mean = np.nanmean(data)
    lo = mean - 2 * stddev
    hi = mean + 2 * stddev
    return lo, hi


def byte_sigma_scale(infile, outfile):
    lo, hi = get_sigma_cutoffs(infile)
    print('2-sigma cutoffs are {} {}'.format(lo, hi))
    gdal.Translate(
        outfile, infile, outputType=gdal.GDT_Byte, scaleParams=[[lo, hi, 1, 255]], resampleAlg='average', noData='0'
    )

    # For some reason, I'm still getting zeros in my byte images eventhough I'm using 1,255 scaling!
    # The following in an attempt to fix that!
    input_file_handle, output_file_handle = gdal.Open(infile), gdal.Open(outfile)
    (x, y, trans, proj, data) = gdal_file.read(input_file_handle)
    mask = (data > 0).astype(bool)
    (x, y, trans, proj, data) = gdal_file.read(output_file_handle)
    mask2 = (data > 0).astype(bool)
    mask3 = mask ^ mask2
    data[mask3 is True] = 1
    gdal_file.write_byte(outfile, trans, proj, data, nodata=0)

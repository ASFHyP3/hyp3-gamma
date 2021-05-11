"""Create and apply a water body mask"""

import os
import argparse
import logging

from osgeo import ogr, osr, gdal

from hyp3lib import saa_func_lib as saa

from hyp3_gamma.dem import get_geometry_from_kml

def reproject_shapefile(tif_file, inshape, outshape, safe_dir):

    # Get source projection from the SAFE dir
    geometry = get_geometry_from_kml(f'{safe_dir}/preview/map-overlay.kml')
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource =   driver.Open(inshape, 0)
    layer = dataSource.GetLayer()
    sourceprj = layer.GetSpatialRef()

    # get target projection from tif_file
    tif = gdal.Open(tif_file)
    targetprj = osr.SpatialReference(wkt = tif.GetProjection())

    # set up the transform and create empty layer
    transform = osr.CoordinateTransformation(sourceprj, targetprj)
    to_fill = ogr.GetDriverByName("Esri Shapefile")
    ds = to_fill.CreateDataSource(outshape)
    outlayer = ds.CreateLayer('', targetprj, ogr.wkbPolygon)
    outlayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))

    # fill the empty layer, converting intersecting features to 
    # a new shapefile
    i = 0
    for feature in layer:
        if feature.GetGeometryRef().Intersects(geometry):

            transformed = feature.GetGeometryRef()
            transformed.Transform(transform)

            geom = ogr.CreateGeometryFromWkb(transformed.ExportToWkb())
            defn = outlayer.GetLayerDefn()
            feat = ogr.Feature(defn)
            feat.SetField('id', i)
            feat.SetGeometry(geom)
            outlayer.CreateFeature(feat)
            i += 1
            feat = None

    ds = None
    return 


def get_water_mask(in_tif, upper_left, lower_right, res, safe_dir, mask_value=1):
    mask_location = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK'

    xmin, ymax = upper_left
    xmax, ymin = lower_right

    shape_file = f'{mask_location}/GSHHG/GSHHS_f_L1.shp'
    reproj_shape_file = 'reproj_shape_file.shp'
    reproject_shapefile(in_tif, shape_file, reproj_shape_file, safe_dir)

    src_ds = ogr.Open(reproj_shape_file)
    src_lyr = src_ds.GetLayer()

    logging.info("Using xmin, xmax {} {}, ymin, ymax {} {}".format(xmin, xmax, ymin, ymax))

    ncols = int((xmax - xmin) / res + 0.5)
    nrows = int((ymax - ymin) / res + 0.5)

    logging.info("Creating water body mask of size {} x {} (lxs) using {}".format(nrows, ncols, 
                 reproj_shape_file))

    geotransform = (xmin, res, 0, ymax, 0, -res)
    dst_ds = gdal.GetDriverByName('MEM').Create('', ncols, nrows, 1, gdal.GDT_Byte)
    dst_rb = dst_ds.GetRasterBand(1)
    dst_rb.Fill(0)
    dst_rb.SetNoDataValue(0)
    dst_ds.SetGeoTransform(geotransform)

    _ = gdal.RasterizeLayer(dst_ds, [mask_value], src_lyr)
    dst_ds.FlushCache()
    mask = dst_ds.GetRasterBand(1).ReadAsArray()
    del dst_ds

    return mask


def apply_water_mask(tiffile, outfile, safe_dir, maskval=0, band=1):
    """
    Given a tiffile input, create outfile, filling in all water areas with the maskval.
    """

    logging.info(f"Using mask value of {maskval}")
    tif_info = gdal.Info(tiffile, format='json')
    upper_left = tif_info['cornerCoordinates']['upperLeft']
    lower_right = tif_info['cornerCoordinates']['lowerRight']

    src_ds = gdal.Open(tiffile)
    data = src_ds.GetRasterBand(band).ReadAsArray()
    proj = src_ds.GetProjection()
    trans = src_ds.GetGeoTransform()
    del src_ds

    logging.info("Applying water body mask")
    mask = get_water_mask(tiffile, upper_left, lower_right, trans[1], safe_dir)
    saa.write_gdal_file_byte("final_mask.tif",trans,proj, mask) 
    data[mask == 0] = maskval
    saa.write_gdal_file_byte("final_dem.tif",trans,proj, data) 

    dst_ds = gdal.GetDriverByName('GTiff').Create(
        outfile, data.shape[1], data.shape[0], band, gdal.GDT_Float32
    )
    dst_ds.SetProjection(proj)
    dst_ds.SetGeoTransform(trans)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds.GetRasterBand(1).SetNoDataValue(maskval)
    del dst_ds


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='mask_water_bodies.py',
      description='Create and employ a water body mask wherein all water is 0 and land is 1')
    
    parser.add_argument('tiffile',help='Name of tif file to mask')
    parser.add_argument('outfile',help='Name of output masked file')
    parser.add_argument('-m','--mask_value',help='Mask value to apply; default 0',type=float,default=0)
    args = parser.parse_args()

    logFile = "apply_water_mask_{}_log.txt".format(os.getpid())
    logging.basicConfig(filename=logFile,format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Starting run")

    apply_water_mask(args.tiffile, args.outfile, mask_value=args.mask_value)

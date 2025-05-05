"""generates boundary shapefile from GeoTIFF file"""

import os

import numpy as np
from hyp3lib import asf_geometry
from hyp3lib.asf_time_series import raster_metadata
from osgeo import gdal, ogr, osr
from scipy import ndimage


def raster_boundary_to_shape(inFile, threshold, outShapeFile, use_closing=True, fill_holes=False, pixel_shift=False):
    print('Extracting raster information ...')
    (fields, values, spatialRef) = raster_metadata(inFile)

    print('Initial origin {x},{y}'.format(x=values[0]['originX'], y=values[0]['originY']))

    if spatialRef.GetAttrValue('AUTHORITY', 0) == 'EPSG':
        epsg = int(spatialRef.GetAttrValue('AUTHORITY', 1))

    print('Extracting boundary geometry ...')
    (data, colFirst, rowFirst, geoTrans, proj) = geotiff_to_boundary_mask(
        inFile,
        epsg,
        threshold,
        use_closing=use_closing
    )
    (rows, cols) = data.shape

    print('After geotiff2boundary_mask origin {x},{y}'.format(x=geoTrans[0], y=geoTrans[3]))

    if fill_holes:
        data = ndimage.binary_fill_holes(data).astype(bool)

        #    if pixel_shift:
        if values[0]['pixel']:
            minx = geoTrans[0]
            maxy = geoTrans[3]
            # maxx = geoTrans[0] + cols*geoTrans[1]
            # miny = geoTrans[3] + rows*geoTrans[5]

            # compute the pixel-aligned bounding box (larger than the feature's bbox)
            left = minx - (geoTrans[1] / 2)
            top = maxy - (geoTrans[5] / 2)

            values[0]['originX'] = left
            values[0]['originY'] = top

    print('After pixel_shift origin {x},{y}'.format(x=values[0]['originX'], y=values[0]['originY']))

    values[0]['rows'] = rows
    values[0]['cols'] = cols

    print('Writing boundary to shapefile ...')
    data_geometry_to_shape(data, fields, values, spatialRef, geoTrans, outShapeFile)


def geotiff_to_boundary_mask(inGeotiff, tsEPSG, threshold, use_closing=True):
    inRaster = gdal.Open(inGeotiff)
    proj = osr.SpatialReference()
    proj.ImportFromWkt(inRaster.GetProjectionRef())
    if proj.GetAttrValue('AUTHORITY', 0) == 'EPSG':
        epsg = int(proj.GetAttrValue('AUTHORITY', 1))

    if tsEPSG != 0 and epsg != tsEPSG:
        print('Reprojecting ...')
        inRaster = asf_geometry.reproject2grid(inRaster, tsEPSG)
        proj.ImportFromWkt(inRaster.GetProjectionRef())
        if proj.GetAttrValue('AUTHORITY', 0) == 'EPSG':
            epsg = int(proj.GetAttrValue('AUTHORITY', 1))

    geoTrans = inRaster.GetGeoTransform()
    inBand = inRaster.GetRasterBand(1)
    noDataValue = inBand.GetNoDataValue()
    data = inBand.ReadAsArray()
    minValue = np.min(data)

    # Check for black fill
    if minValue > 0:
        data /= data
        colFirst = 0
        rowFirst = 0
    else:
        data[np.isnan(data) is True] = noDataValue
        if threshold is not None:
            print('Applying threshold ({0}) ...'.format(threshold))
            data[data < np.float64(threshold)] = noDataValue
        if np.isnan(noDataValue):
            data[np.isnan(data) is False] = 1
        else:
            data[data > noDataValue] = 1
        if use_closing:
            data = ndimage.binary_closing(data, iterations=10, structure=np.ones((3, 3))).astype(data.dtype)
        inRaster = None

        (data, colFirst, rowFirst, geoTrans) = asf_geometry.cut_blackfill(data, geoTrans)

    return (data, colFirst, rowFirst, geoTrans, proj)


def data_geometry_to_shape(data, fields, values, spatialRef, geoTrans, shapeFile):
    return data_geometry_to_shape_ext(data, fields, values, spatialRef, geoTrans, None, 0, None, shapeFile)


def data_geometry_to_shape_ext(data, fields, values, spatialRef, geoTrans, classes, threshold, background, shapeFile):
    # Check input
    if threshold is not None:
        threshold = float(threshold)
    if background is not None:
        background = int(background)

    # Buffer data
    (rows, cols) = data.shape
    pixelSize = geoTrans[1]
    originX = geoTrans[0] - 10 * pixelSize
    originY = geoTrans[3] + 10 * pixelSize
    geoTrans = (originX, pixelSize, 0, originY, 0, -pixelSize)
    mask = np.zeros((rows + 20, cols + 20), dtype=np.float32)
    mask[10: rows + 10, 10: cols + 10] = data
    data = mask

    # Save in memory
    (rows, cols) = data.shape
    data = data.astype(np.byte)
    gdalDriver = gdal.GetDriverByName('Mem')
    outRaster = gdalDriver.Create('value', cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(spatialRef.ExportToWkt())
    outBand = outRaster.GetRasterBand(1)
    outBand.WriteArray(data)

    # Write data to shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(shapeFile):
        driver.DeleteDataSource(shapeFile)
    outShape = driver.CreateDataSource(shapeFile)
    outLayer = outShape.CreateLayer('polygon', srs=spatialRef)
    outField = ogr.FieldDefn('value', ogr.OFTInteger)
    outLayer.CreateField(outField)
    gdal.Polygonize(outBand, None, outLayer, 0, [], callback=None)
    for field in fields:
        fieldDefinition = ogr.FieldDefn(field['name'], field['type'])
        if field['type'] == ogr.OFTString:
            fieldDefinition.SetWidth(field['width'])
        outLayer.CreateField(fieldDefinition)
    fieldDefinition = ogr.FieldDefn('area', ogr.OFTReal)
    fieldDefinition.SetWidth(16)
    fieldDefinition.SetPrecision(3)
    outLayer.CreateField(fieldDefinition)
    fieldDefinition = ogr.FieldDefn('centroid', ogr.OFTString)
    fieldDefinition.SetWidth(50)
    outLayer.CreateField(fieldDefinition)
    if classes:
        fieldDefinition = ogr.FieldDefn('size', ogr.OFTString)
        fieldDefinition.SetWidth(25)
        outLayer.CreateField(fieldDefinition)
    _ = outLayer.GetLayerDefn()
    for outFeature in outLayer:
        for value in values:
            for field in fields:
                name = field['name']
                outFeature.SetField(name, value[name])
        cValue = outFeature.GetField('value')
        fill = False
        if cValue == 0:
            fill = True
        if background is not None and cValue == background:
            fill = True
        geometry = outFeature.GetGeometryRef()
        area = float(geometry.GetArea())
        outFeature.SetField('area', area)
        if classes:
            for ii in range(len(classes)):
                if area > classes[ii]['minimum'] and area < classes[ii]['maximum']:
                    outFeature.SetField('size', classes[ii]['class'])
        centroid = geometry.Centroid().ExportToWkt()
        outFeature.SetField('centroid', centroid)
        if fill is False and area > threshold:
            outLayer.SetFeature(outFeature)
        else:
            outLayer.DeleteFeature(outFeature.GetFID())
    outShape.Destroy()

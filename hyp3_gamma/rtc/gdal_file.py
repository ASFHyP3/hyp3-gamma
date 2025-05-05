from osgeo import gdal


def read(filehandle, band=1, gcps=False):
    geotransform = filehandle.GetGeoTransform()
    geoproj = filehandle.GetProjection()
    banddata = filehandle.GetRasterBand(band)
    # type = gdal.GetDataTypeName(banddata.DataType).lower()
    data_min = banddata.GetMinimum()
    data_max = banddata.GetMaximum()
    if data_min is None or data_max is None:
        (data_min, data_max) = banddata.ComputeRasterMinMax(1)
    data = banddata.ReadAsArray()
    if gcps is False:
        return filehandle.RasterXSize, filehandle.RasterYSize, geotransform, geoproj, data
    else:
        gcp = filehandle.GetGCPs()
        gcpproj = filehandle.GetGCPProjection()
        return filehandle.RasterXSize, filehandle.RasterYSize, geotransform, geoproj, gcp, gcpproj, data


def write_float(filename, geotransform, geoproj, data, nodata=None):
    (x, y) = data.shape
    image_format = 'GTiff'
    driver = gdal.GetDriverByName(image_format)
    dst_datatype = gdal.GDT_Float32
    dst_ds = driver.Create(filename, y, x, 1, dst_datatype)
    northing = geotransform[0]
    weres = geotransform[1]
    rotation = geotransform[2]
    easting = geotransform[3]
    rotation = geotransform[4]
    nsres = geotransform[5]

    dst_ds.GetRasterBand(1).WriteArray(data)
    if nodata is not None:
        dst_ds.GetRasterBand(1).SetNoDataValue(nodata)
    # dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetGeoTransform([northing, weres, rotation, easting, rotation, nsres])
    dst_ds.SetProjection(geoproj)


def write_byte(filename, geotransform, geoproj, data, nodata=None):
    (x, y) = data.shape
    image_format = 'GTiff'
    driver = gdal.GetDriverByName(image_format)
    dst_datatype = gdal.GDT_Byte
    dst_ds = driver.Create(filename, y, x, 1, dst_datatype)
    geotransform = [item for item in geotransform]
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.GetRasterBand(1).WriteArray(data)
    if nodata is not None:
        dst_ds.GetRasterBand(1).SetNoDataValue(nodata)
    dst_ds.SetProjection(geoproj)

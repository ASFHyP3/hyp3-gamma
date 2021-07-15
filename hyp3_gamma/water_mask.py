"""Create and apply a water body mask"""
from osgeo import gdal

gdal.UseExceptions()


def create_water_mask(input_tif: str, output_tif: str):
    """Create a water mask GeoTIFF with the same geometry as a given input GeoTIFF

    The water mask is assembled from GSHHG v2.3.7 Level 1 (boundary between land and ocean, except Antarctica) at full
    resolution. To learn more, visit https://www.soest.hawaii.edu/pwessel/gshhg/

    Shoreline data is buffered to 3 km to reduce the possibility of near-shore features being excluded. Pixel values of
    1 indicate land and 0 indicate water.

    Args:
        input_tif: Path for the input GeoTIFF
        output_tif: Path for the output GeoTIFF
    """
    mask_location = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/GSHHG/GSHHS_f_L1.shp'
    src_ds = gdal.Open(input_tif)

    dst_ds = gdal.GetDriverByName('GTiff').Create(output_tif, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjection())
    dst_ds.SetMetadataItem('AREA_OR_POINT', src_ds.GetMetadataItem('AREA_OR_POINT'))
    gdal.Rasterize(dst_ds, mask_location, burnValues=[1])

    del src_ds, dst_ds
    return output_tif

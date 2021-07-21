"""Create and apply a water body mask"""
from osgeo import gdal
import pyproj
import geopandas as gpd
from shapely.geometry import shape, Polygon
from tempfile import NamedTemporaryFile, TemporaryDirectory

from hyp3_gamma.polygon_splitter import split_polygon

gdal.UseExceptions()


def reprojshapefile(in_shp_file, ref_file, temp_dir):
    """reproject in_shap_file to the same crs as that defined in the ref_file. reprojected shapefile is out_shp_file.
    """
    ref = gdal.Open(ref_file)
    ref_crs = ref.GetProjection()
    gjs = gdal.Info(ref_file,format='json')['wgs84Extent']
    geom = split_polygon(gjs, output_format='polygons')
    index=list(range(len(geom)))
    poly = gpd.GeoDataFrame(index=index, crs="EPSG:4326", geometry=geom)
    shp = gpd.read_file(in_shp_file, mask=poly)
    shp_proj = shp.to_crs(ref_crs)
    shp_proj.to_file(f'{temp_dir}/reproj.shp')


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
    with TemporaryDirectory() as temp_dir:
        reprojshapefile(mask_location, input_tif, temp_dir)
        src_ds = gdal.Open(input_tif)
        dst_ds = gdal.GetDriverByName('GTiff').Create(output_tif, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
        dst_ds.SetProjection(src_ds.GetProjection())
        dst_ds.SetMetadataItem('AREA_OR_POINT', src_ds.GetMetadataItem('AREA_OR_POINT'))
        gdal.Rasterize(dst_ds, f'{temp_dir}/reproj.shp', burnValues=[1])
        del src_ds, dst_ds

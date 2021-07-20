"""Create and apply a water body mask"""
from osgeo import gdal
from affine import Affine
import fiona
import pyproj
import geopandas as gpd
from shapely.geometry import shape, Polygon

gdal.UseExceptions()


def reprojshapefile(in_shp_file, ref_file, safe_dir, out_shp_file):
    """reproject in_shap_file to the same crs as that defined in the ref_file. reprojected shapefile is out_shp_file.
    """
    fiona.drvsupport.supported_drivers['libkml'] = 'rw'
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
    gdf_mask =gpd.read_file(f'{safe_dir}/preview/map-overlay.kml')
    shp = gpd.read_file(in_shp_file, mask=gdf_mask)
    ref = gdal.Open(ref_file)
    ref_crs = ref.GetProjection()
    shp_proj = shp.to_crs(ref_crs)
    shp_proj.to_file(out_shp_file)


def calc_ij_coord(gt, col, row):
        transform = Affine.from_gdal(*gt)
        x, y = transform * (col, row)
        return x, y



def get_corners_lonlat(ref_file):
    '''
    returns the corner cordinators of the ref_file in lon/lat.
    format of the return variable is ((ul_x, ul_y),(ur_x, ur_y),(lr_x, lr_y),(ll_x, ll_y))
    '''
    ds = gdal.Open(ref_file)
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    gt  = ds.GetGeoTransform()

    from_crs = pyproj.crs.CRS(ds.GetProjection())    
    to_crs = pyproj.crs.CRS('EPSG:4326')
    proj = pyproj.Transformer.from_crs(from_crs, to_crs, always_xy=True)
    ul_x, ul_y = calc_ij_coord(gt, 0, 0)
    ul_lon, ul_lat = proj.transform(ul_x, ul_y)

    ur_x, ur_y = calc_ij_coord(gt, xsize, 0)
    ur_lon, ur_lat = proj.transform(ur_x, ur_y)

    lr_x, lr_y = calc_ij_coord(gt, xsize, ysize)
    lr_lon, lr_lat = proj.transform(lr_x, lr_y)

    ll_x, ll_y = calc_ij_coord(gt, 0, ysize)
    ll_lon, ll_lat = proj.transform(ll_x, ll_y)

    corners_xy = ((ul_x, ul_y),(ur_x, ur_y),(lr_x, lr_y),(ll_x, ll_y))

    corners_ll = ((ul_lon, ul_lat),(ur_lon, ur_lat),(lr_lon, lr_lat),(ll_lon, ll_lat))

    return corners_xy, corners_ll 


def reprojshapefile2(in_shp_file, ref_file, out_shp_file):
    """reproject in_shap_file to the same crs as that defined in the ref_file. reprojected shapefile is out_shp_file.
    """
    # read the global shapefile and reproject to the same projection as the ref_file
    shp = gpd.read_file(in_shp_file)
    ref = gdal.Open(ref_file)
    ref_crs = ref.GetProjection()
    shp_proj = shp.to_crs(ref_crs)
    shp_proj.to_file('glb_proj.shp')
    
    # mask with extent of the ref_file
    corners_xy,_ = get_corners_lonlat(ref_file)
    geom = Polygon(corners_xy)
    poly = gpd.GeoDataFrame(index=[0], crs=ref_crs, geometry=[geom])
    poly.to_file("extent.shp")

    # read the extent.shp and use it to mask the glb_proj.shp, 
    # mask shapefile in the projection coordinate to avoid the problem of crossing of the antimeridaim.
    poly_back =gpd.read_file("extent.shp")
    shp_out = gpd.read_file("glb_proj.shp", mask=poly_back)
    shp_out.to_file(out_shp_file)


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
    mask_location = "GSHHS_f_L1.shp"
    reprojshapefile2(mask_location, input_tif, 'reproj.shp')

    src_ds = gdal.Open(input_tif)

    dst_ds = gdal.GetDriverByName('GTiff').Create(output_tif, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjection())
    dst_ds.SetMetadataItem('AREA_OR_POINT', src_ds.GetMetadataItem('AREA_OR_POINT'))
    gdal.Rasterize(dst_ds, 'reproj.shp', burnValues=[1])

    del src_ds, dst_ds

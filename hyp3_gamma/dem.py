import json
from subprocess import PIPE, run

from hyp3lib import dem
from osgeo import ogr


def get_geometry_from_kml(kml_file: str) -> ogr.Geometry:
    cmd = [
        'ogr2ogr',
        '-wrapdateline',
        '-datelineoffset',
        '20',
        '-f',
        'GeoJSON',
        '-mapfieldtype',
        'DateTime=String',
        '/vsistdout',
        kml_file,
    ]
    geojson_str = run(cmd, stdout=PIPE, check=True).stdout
    geometry = json.loads(geojson_str)['features'][0]['geometry']
    return ogr.CreateGeometryFromJson(json.dumps(geometry))


def utm_from_lon_lat(lon: float, lat: float) -> int:
    hemisphere = 32600 if lat >= 0 else 32700
    zone = int(lon // 6 + 30) % 60 + 1
    return hemisphere + zone


def prepare_dem_geotiff(output_name: str, geometry: ogr.Geometry, pixel_size: float = 30.0) -> None:
    """Create a DEM mosaic GeoTIFF covering a given geometry.

    The DEM mosaic is assembled from the Copernicus GLO-30 Public DEM. The output GeoTIFF covers the input geometry
    buffered by 0.15 degrees, is projected to the UTM zone of the geometry centroid, and has a pixel size of 30m.

    Args:
        output_name: Path for the output GeoTIFF
        geometry: Geometry in EPSG:4326 (lon/lat) projection for which to prepare a DEM mosaic
        pixel_size: Pixel size for the output GeoTIFF in meters

    """
    centroid = geometry.Centroid()


    epsg_code = utm_from_lon_lat(centroid.GetX(), centroid.GetY())
    dem.prepare_dem_geotiff(output_name,
                            geometry,
                            epsg_code=epsg_code,
                            pixel_size=pixel_size,
                            buffer_size_in_degrees=0.15)

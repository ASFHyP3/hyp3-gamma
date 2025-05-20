import json
from pathlib import Path
from subprocess import PIPE, run

import numpy as np
from hyp3lib import dem
from osgeo import ogr


def crosses_antimeridian(geometry: dict) -> bool:
    if geometry['type'] != 'Polygon':
        raise ValueError(f'Geometry type {geometry["type"]} is invalid; only Polygon is supported.')
    longitudes = [point[0] for point in geometry['coordinates'][0]]
    return any(lon < -160 for lon in longitudes) and any(160 < lon for lon in longitudes)


def get_geometry_from_kml(kml_file: str) -> ogr.Geometry:
    cmd = ['ogr2ogr', '-f', 'GeoJSON', '-mapfieldtype', 'DateTime=String', '/vsistdout', kml_file]
    geojson_str = run(cmd, stdout=PIPE, check=True).stdout
    geojson = json.loads(geojson_str)
    geometry = geojson['features'][0]['geometry']
    if crosses_antimeridian(geometry):
        for point in geometry['coordinates'][0]:
            if point[0] < 0:
                point[0] += 360
    return ogr.CreateGeometryFromJson(json.dumps(geometry))


def get_buffer_distance(lat_in_dd: float, buffer_in_km: float) -> tuple[float, float]:
    """Given a latitude and a buffer distance in kilometers, return the
    corresponding buffer distance in degrees for both longitude and latitude.

    Calculation from:
    https://en.wikipedia.org/wiki/Longitude#Length_of_a_degree_of_longitude
    https://en.wikipedia.org/wiki/Latitude#Length_of_a_degree_of_latitude

    Args:
        lat_in_dd: Latitude to perform the calculation at in decimal degrees
        buffer_in_km: Buffer distance in kilometers

    Returns:
        A tuple containing the buffer distance in degrees for longitude and latitude
    """
    assert lat_in_dd > -90 and lat_in_dd < 90, 'Latitude must be between -90 and 90 degrees'
    one_lat_degree_length = 111.32
    buffer_lat_in_dd = buffer_in_km / one_lat_degree_length
    buffer_lon_in_dd = buffer_in_km / (one_lat_degree_length * np.cos(np.deg2rad(lat_in_dd)))
    return buffer_lon_in_dd, buffer_lat_in_dd


def get_buffer_in_degrees_for(geometry: ogr.Geometry, buffer_distance_km: float) -> float:
    _, _, min_lat, max_lat = geometry.GetEnvelope()
    geometry_lat = max(np.abs(min_lat), np.abs(max_lat))
    lon_buffer, _ = get_buffer_distance(geometry_lat, buffer_distance_km)[0]

    return lon_buffer


def utm_from_lon_lat(lon: float, lat: float) -> int:
    hemisphere = 32600 if lat >= 0 else 32700
    zone = int(lon // 6 + 30) % 60 + 1
    return hemisphere + zone


def prepare_dem_geotiff(output_name: str, geometry: ogr.Geometry, pixel_size: float = 30.0) -> None:
    """Create a DEM mosaic GeoTIFF covering a given geometry.

    The DEM mosaic is assembled from the Copernicus GLO-30 Public DEM. The output GeoTIFF covers the input geometry
    buffered by 15km, is projected to the UTM zone of the geometry centroid, and has a pixel size of 30m.

    Args:
        output_name: Path for the output GeoTIFF
        geometry: Geometry in EPSG:4326 (lon/lat) projection for which to prepare a DEM mosaic
        pixel_size: Pixel size for the output GeoTIFF in meters

    """
    centroid = geometry.Centroid()

    buffer_distance_km = 15.0
    buffer_in_degrees = get_buffer_in_degrees_for(geometry, buffer_distance_km)

    epsg_code = utm_from_lon_lat(centroid.GetX(), centroid.GetY())
    dem.prepare_dem_geotiff(
        Path(output_name),
        geometry,
        epsg_code=epsg_code,
        pixel_size=pixel_size,
        buffer_size_in_degrees=buffer_in_degrees,
    )

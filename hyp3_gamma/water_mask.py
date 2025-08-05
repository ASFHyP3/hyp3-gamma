"""Create and apply a water body mask"""

import subprocess
import tempfile

import hyp3lib.fetch
import numpy as np
from osgeo import gdal
from pyproj import CRS


gdal.UseExceptions()

TILE_PATH = 'https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/'


def get_extent(filename: str, epsg: str = 'EPSG:4326') -> list:
    """Get the extent of the image [min x, min y, max x, max y].

    Args:
        filename: The path to the input image.
        epsg: The EPSG code to open the image in.
    """
    with tempfile.NamedTemporaryFile() as tmp_file:
        ds = gdal.Warp(
            tmp_file.name,
            filename,
            dstSRS=epsg,
            creationOptions=['COMPRESS=LZW', 'TILED=YES', 'NUM_THREADS=all_cpus'],
        )
        geotransform = ds.GetGeoTransform()
        x_min = geotransform[0]
        x_max = x_min + geotransform[1] * ds.RasterXSize
        y_max = geotransform[3]
        y_min = y_max + geotransform[5] * ds.RasterYSize
    return [x_min, y_min, x_max, y_max]


def get_corners(filename: str) -> list:
    """Get all four corners of the given image

    Args:
        filename: The path to the input image.
    """
    info = gdal.Info(filename, format='json')
    return info['wgs84Extent']['coordinates'][0][:-1]


def coord_to_tile(coord: tuple[float, float]) -> str:
    """Get the filename of the tile which encloses the inputted coordinate.

    Args:
        coord: The (lon, lat) tuple containing the desired coordinate.
    """
    lat_rounded = np.floor(coord[1] / 5) * 5
    lon_rounded = np.floor(coord[0] / 5) * 5
    if lat_rounded >= 0:
        lat_part = 'n' + str(int(lat_rounded)).zfill(2)
    else:
        lat_part = 's' + str(int(np.abs(lat_rounded))).zfill(2)
    if lon_rounded >= 0:
        lon_part = 'e' + str(int(lon_rounded)).zfill(3)
    else:
        lon_part = 'w' + str(int(np.abs(lon_rounded))).zfill(3)
    return lat_part + lon_part + '.tif'


def get_tiles(filename: str) -> list:
    """Get the URLs to the tiles necessary to cover the inputted file.

    Args:
        filename: The path to the input file.
    """
    tiles = {TILE_PATH + coord_to_tile(corner) for corner in get_corners(filename)}
    return list(tiles)


def create_water_mask(input_image: str, output_image: str, gdal_format='GTiff') -> None:
    """Create a water mask GeoTIFF with the same geometry as a given input GeoTIFF

    The water mask is assembled from OpenStreetMaps data.

    Shoreline data is unbuffered and pixel values of 1 indicate land touches the pixel and 0 indicates there is no
    land in the pixel.

    Args:
        input_image: Path for the input GDAL-compatible image
        output_image: Path for the output image
        gdal_format: GDAL format name to create output image as
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        # Ensures that the input image is not using Ground Control Points.
        input_image_tmp = f'{tmp_path}/input.tif'
        ds = gdal.Warp(input_image_tmp, input_image)
        input_image = input_image_tmp

        pixel_size = ds.GetGeoTransform()[1]
        proj = CRS.from_wkt(ds.GetProjection())
        epsg = f'EPSG:{proj.to_epsg()}'

        tiles = get_tiles(input_image)
        if len(tiles) < 1:
            raise ValueError(f'No water mask tiles found for {input_image}.')

        downloaded_tiles = [hyp3lib.fetch.download_file(tile, tmp_path) for tile in tiles]

        merged_vrt_path = f'{tmp_path}/merged.vrt'
        gdal.BuildVRT(merged_vrt_path, downloaded_tiles)

        merged_warped_path = f'{tmp_path}/merged_warped.tif'
        gdal.Warp(
            merged_warped_path,
            merged_vrt_path,
            outputBounds=get_extent(input_image, epsg=epsg),
            xRes=pixel_size,
            yRes=pixel_size,
            dstSRS=epsg,
            format='GTiff',
            creationOptions=['COMPRESS=LZW', 'NUM_THREADS=all_cpus'],
        )

        flip_values_command = [
            'gdal_calc.py',
            '-A',
            merged_warped_path,
            f'--outfile={output_image}',
            '--calc="numpy.abs((A.astype(numpy.int16) + 1) - 2)"',  # Change 1's to 0's and 0's to 1's.
            f'--format={gdal_format}',
        ]
        subprocess.run(flip_values_command, check=True)

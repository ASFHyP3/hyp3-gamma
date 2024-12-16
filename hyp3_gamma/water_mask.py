"""Create and apply a water body mask"""

import subprocess
from pathlib import Path
from typing import Optional

import numpy as np
from osgeo import gdal
from pyproj import CRS

gdal.UseExceptions()

TILE_PATH = '/vsicurl/https://asf-dem-west.s3.amazonaws.com/WATER_MASK/TILES/'


def get_extent(filename, tmp_path: Optional[Path], epsg='EPSG:4326'):
    """Get the extent of the image [min x, min y, max x, max y].

    Args:
        filename: The path to the input image.
        tmp_path: An optional path to a temporary directory for temp files.
        epsg: The EPSG code to open the image in.
    """
    tmp_file = 'tmp.tif' if not tmp_path else str(tmp_path / Path('tmp.tif'))
    ds = gdal.Warp(
        tmp_file,
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


def get_corners(filename, tmp_path: Optional[Path]):
    """Get all four corners of the given image: [upper_left, bottom_left, upper_right, bottom_right].

    Args:
        filename: The path to the input image.
        tmp_path: An optional path to a temporary directory for temp files.
    """
    tmp_file = 'tmp.tif' if not tmp_path else str(tmp_path / Path('tmp.tif'))
    ds = gdal.Warp(
        tmp_file,
        filename,
        dstSRS='EPSG:4326',
        creationOptions=['COMPRESS=LZW', 'TILED=YES', 'NUM_THREADS=all_cpus'],
    )
    geotransform = ds.GetGeoTransform()
    x_min = geotransform[0]
    x_max = x_min + geotransform[1] * ds.RasterXSize
    y_max = geotransform[3]
    y_min = y_max + geotransform[5] * ds.RasterYSize
    upper_left = [x_min, y_max]
    bottom_left = [x_min, y_min]
    upper_right = [x_max, y_max]
    bottom_right = [x_max, y_min]
    return [upper_left, bottom_left, upper_right, bottom_right]


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


def get_tiles(filename: str, tmp_path: Optional[Path]) -> None:
    """Get the AWS vsicurl path's to the tiles necessary to cover the inputted file.

    Args:
        filename: The path to the input file.
        tmp_path: An optional path to a temporary directory for temp files.
    """
    tiles = []
    corners = get_corners(filename, tmp_path=tmp_path)
    for corner in corners:
        tile = TILE_PATH + coord_to_tile(corner)
        if tile not in tiles:
            tiles.append(tile)
    return tiles


def create_water_mask(
    input_image: str,
    output_image: str,
    gdal_format='GTiff',
    tmp_path: Optional[Path] = Path('.'),
):
    """Create a water mask GeoTIFF with the same geometry as a given input GeoTIFF

    The water mask is assembled from OpenStreetMaps data.

    Shoreline data is unbuffered and pixel values of 1 indicate land touches the pixel and 0 indicates there is no
    land in the pixel.

    Args:
        input_image: Path for the input GDAL-compatible image
        output_image: Path for the output image
        gdal_format: GDAL format name to create output image as
        tmp_path: An optional path to a temporary directory for temp files.
    """

    # Ensures that the input image is not using Ground Control Points.
    input_image_tmp = 'input.tif'
    ds = gdal.Warp(input_image_tmp, input_image)
    input_image = input_image_tmp

    pixel_size = ds.GetGeoTransform()[1]
    proj = CRS.from_wkt(ds.GetProjection())
    epsg = f'EPSG:{proj.to_epsg()}'

    tiles = get_tiles(input_image, tmp_path=tmp_path)

    if len(tiles) < 1:
        raise ValueError(f'No water mask tiles found for {tiles}.')

    merged_tif_path = str(tmp_path / 'merged.tif')
    merged_vrt_path = str(tmp_path / 'merged.vrt')
    merged_warped_path = str(tmp_path / 'merged_warped.tif')
    shape_path = str(tmp_path / 'tmp.shp')

    # This is WAY faster than using gdal_merge, because of course it is.
    if len(tiles) > 1:
        build_vrt_command = ['gdalbuildvrt', merged_vrt_path] + tiles
        subprocess.run(build_vrt_command, check=True)
        translate_command = [
            'gdal_translate',
            '-co',
            'COMPRESS=LZW',
            '-co',
            'NUM_THREADS=all_cpus',
            merged_vrt_path,
            merged_tif_path,
        ]
        subprocess.run(translate_command, check=True)

    shapefile_command = ['gdaltindex', shape_path, input_image]
    subprocess.run(shapefile_command, check=True)

    warp_filename = merged_tif_path if len(tiles) > 1 else tiles[0]
    corners = get_extent(input_image, tmp_path=tmp_path, epsg=epsg)
    gdal.Warp(
        merged_warped_path,
        warp_filename,
        outputBounds=corners,
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

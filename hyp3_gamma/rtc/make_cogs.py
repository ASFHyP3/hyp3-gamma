import logging
import os
import shutil
from glob import glob
from tempfile import NamedTemporaryFile

from hyp3lib.execute import execute
from osgeo import gdal


def cogify_dir(directory: str, file_pattern: str = '*.tif'):
    path_expression = os.path.join(directory, file_pattern)
    logging.info(f'Converting files to COGs for {path_expression}')
    for filename in glob(path_expression):
        cogify_file(filename)


def cogify_file(filename: str):
    logging.info(f'Converting {filename} to COG')
    execute(f'gdaladdo -r average {filename} 2 4 8 16', uselogging=True)
    creation_options = ['TILED=YES', 'COMPRESS=DEFLATE', 'NUM_THREADS=ALL_CPUS', 'COPY_SRC_OVERVIEWS=YES']
    with NamedTemporaryFile() as temp_file:
        shutil.copy(filename, temp_file.name)
        gdal.Translate(filename, temp_file.name, format='GTiff', creationOptions=creation_options)

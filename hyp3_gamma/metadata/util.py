import re
import shutil
from base64 import b64encode
from datetime import datetime
from glob import glob
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from osgeo import osr

import hyp3_metadata
from hyp3_metadata import data

SUPPORTED_DEMS = ['EU_DEM_V11', 'GIMP', 'IFSAR', 'NED13', 'NED1', 'NED2', 'REMA', 'SRTMGL1', 'SRTMGL3', 'GLO-30']


def populate_example_data(product_dir: Path):
    product_files = glob(str(Path(data.__file__).parent / 'rtc*'))
    for f in product_files:
        shutil.copy(f, product_dir / f'{Path(f).name.replace("rtc", product_dir.name)}')


def get_environment() -> Environment:
    env = Environment(
        loader=PackageLoader('hyp3_metadata', 'templates'),
        autoescape=select_autoescape(['html.j2', 'xml.j2']),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    return env


def render_template(template: str, payload: dict) -> str:
    env = get_environment()
    template = env.get_template(template)
    rendered = template.render(payload)
    return rendered


def get_dem_template_id(dem_name: str) -> Optional[str]:
    if dem_name.startswith('EU'):
        return 'eu'
    if dem_name.startswith('GIMP'):
        return 'gimp'
    if dem_name.startswith('IFSAR'):
        return 'ifsar'
    if dem_name.startswith('NED'):
        return 'ned'
    if dem_name.startswith('REMA'):
        return 'rema'
    if dem_name.startswith('SRTM'):
        return 'srtm'
    if dem_name == 'GLO-30':
        return 'cop'


def get_projection(srs_wkt) -> str:
    srs = osr.SpatialReference()
    srs.ImportFromWkt(srs_wkt)
    return srs.GetAttrValue('projcs')


def get_granule_type(granule_name) -> Dict[str, str]:
    granule_type = granule_name[7:10]
    if granule_type == 'SLC':
        return {'granule_type': 'SLC', 'granule_description': 'Single Look Complex'}
    if granule_type == 'GRD':
        return {'granule_type': 'GRD', 'granule_description': 'Ground Range Detected'}
    raise NotImplementedError(f'Unknown granule type: {granule_name}')


def get_polarizations(product_polarization):
    mapping = {
        'SH': ('HH',),
        'SV': ('VV',),
        'DH': ('HH', 'HV'),
        'DV': ('VV', 'VH'),
    }
    return mapping[product_polarization]


def decode_product(product_name: str) -> dict:
    product_parts = product_name.split('_')
    user_options = product_parts[-2]

    return {
        'pixel_spacing': int(product_parts[-4][-2:]),
        'radiometry': 'gamma-0' if user_options[0] == 'g' else 'sigma-0',
        'scale': 'power' if user_options[1] == 'p' else 'amplitude',
        'masked': False if user_options[2] == 'u' else True,
        'filter_applied': False if user_options[3] == 'n' else True,
        'clipped': False if user_options[4] == 'e' else True,
        'matching': False if user_options[5] == 'd' else True,
        'polarizations': get_polarizations(product_parts[-5][:2]),
    }


def strip_polarization(file_name: str) -> str:
    return re.sub(r'_(VV|VH|HH|HV)', '', file_name)


def get_thumbnail_encoded_string(reference_file: Path, size: Tuple[int, int] = (200, 200)) -> str:
    browse_file = reference_file.with_suffix('.png')
    browse_file = browse_file.parent / strip_polarization(browse_file.name)
    if not browse_file.exists():
        return ''

    image = Image.open(browse_file)
    image = image.convert('RGB')
    image.thumbnail(size)

    data = BytesIO()
    image.save(data, format='JPEG')
    return b64encode(data.getvalue()).decode()


def marshal_metadata(product_dir: Path, granule_name: str, dem_name: str, processing_date: datetime, looks: int,
                     plugin_name: str, plugin_version: str, processor_name: str, processor_version: str) -> dict:
    payload = locals()
    payload['metadata_version'] = hyp3_metadata.__version__

    payload.update(decode_product(product_dir.name))

    payload.update(get_granule_type(granule_name))

    return payload

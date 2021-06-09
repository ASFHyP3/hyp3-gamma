import re
from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Dict, Tuple

from PIL import Image
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from osgeo import osr


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


def strip_polarization(file_name: str) -> str:
    return re.sub(r'_(VV|VH|HH|HV)', '', file_name)


def get_thumbnail_encoded_string(browse_file: Path, size: Tuple[int, int] = (200, 200)) -> str:
    if not browse_file.exists():
        return ''

    image = Image.open(browse_file)
    image = image.convert('RGB')
    image.thumbnail(size)

    data = BytesIO()
    image.save(data, format='JPEG')
    return b64encode(data.getvalue()).decode()

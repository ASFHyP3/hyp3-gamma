import re
from base64 import b64encode
from copy import deepcopy
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from osgeo import gdal, osr

import hyp3_metadata


def get_environment() -> Environment:
    env = Environment(
        loader=PackageLoader('hyp3_metadata', '.'),
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


def create_metadata_file_set(product_dir: Path, granule_name: str, dem_name: str, processing_date: datetime,
                             looks: int, plugin_name: str, plugin_version: str, processor_name: str,
                             processor_version: str) -> List[Path]:
    payload = marshal_metadata(
        product_dir=product_dir,
        granule_name=granule_name,
        dem_name=dem_name,
        processing_date=processing_date,
        looks=looks,
        plugin_name=plugin_name,
        plugin_version=plugin_version,
        processor_name=processor_name,
        processor_version=processor_version,
    )
    files = []
    generators = [
        create_product_xmls,
        create_browse_xmls,
        create_readme,
        create_dem_xml,
        create_inc_map_xml,
        create_ls_map_xml,
        create_area_xml,
    ]
    for generator in generators:
        output = generator(payload)
        if isinstance(output, list):
            files.extend(output)
        elif isinstance(output, Path):
            files.append(output)

    return files


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


def get_projection(srs_wkt) -> str:
    srs = osr.SpatialReference()
    srs.ImportFromWkt(srs_wkt)
    return srs.GetAttrValue('projcs')


def get_granule_type(granule_name) -> Dict[str, str]:
    granule_type = granule_name[7:10]
    if granule_type == 'SLC':
        return {'granule_type': 'SLC', 'granule_description': 'Single-Look Complex'}
    if granule_type == 'GRD':
        return {'granule_type': 'GRD', 'granule_description': 'Ground Range Detected'}
    raise NotImplementedError(f'Unknown granule type: {granule_name}')


# FIXME: in hyp3_rtc_gamma.rtc_sentinel as well -- move to hyp3lib?
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


def create_readme(payload: dict) -> Path:
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_{payload["polarizations"][0]}.tif'

    return create_metadata_file(
        payload, 'readme.md.txt.j2', reference_file, out_ext='README.md.txt', strip_ext=True, strip_pol=True
    )


def create_product_xmls(payload: dict) -> List[Path]:
    payload = deepcopy(payload)

    output_files = []
    for pol in payload['polarizations']:
        payload['pol'] = pol
        reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_{pol}.tif'

        output_files.append(
            create_metadata_file(payload, 'product.xml.j2', reference_file)
        )

    return output_files


def create_dem_xml(payload: dict) -> Path:
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_dem.tif'

    dem_template_id = get_dem_template_id(payload['dem_name'])
    if dem_template_id is not None:
        return create_metadata_file(payload, f'dem/dem-{dem_template_id}.xml.j2', reference_file)


def create_browse_xmls(payload: dict) -> List[Path]:
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}.png'

    output_files = [
        create_metadata_file(payload, 'browse/browse-greyscale.xml.j2', reference_file),
    ]

    rgb_file = payload['product_dir'] / f'{payload["product_dir"].name}_rgb.png'
    if rgb_file.exists():
        output_files.append(
            create_metadata_file(payload, 'browse/browse-color.xml.j2', rgb_file)
        )

    return output_files


def create_inc_map_xml(payload: dict) -> Path:
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_inc_map.tif'
    return create_metadata_file(payload, 'inc_map.xml.j2', reference_file)


def create_ls_map_xml(payload: dict) -> Path:
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_ls_map.tif'
    return create_metadata_file(payload, 'ls_map.xml.j2', reference_file)


def create_area_xml(payload: dict) -> Path:
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_area.tif'
    return create_metadata_file(payload, 'area.xml.j2', reference_file)


def create_metadata_file(payload: dict, template: str, reference_file: Path, out_ext: str = 'xml',
                         strip_ext: bool = False, strip_pol: bool = False) -> Optional[Path]:
    if not reference_file.exists():
        return None

    payload = deepcopy(payload)
    info = gdal.Info(str(reference_file), format='json')
    payload['pixel_spacing'] = info['geoTransform'][1]
    payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

    payload['thumbnail_encoded_string'] = get_thumbnail_encoded_string(reference_file)

    content = render_template(template, payload)
    out_name = reference_file.name if not strip_ext else reference_file.stem
    if strip_pol:
        out_name = strip_polarization(out_name)
    output_file = reference_file.parent / f'{out_name}.{out_ext}'
    with open(output_file, 'w') as f:
        f.write(content)

    return output_file

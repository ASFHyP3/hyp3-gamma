import copy
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from osgeo import gdal, osr

from hyp3_metadata import __version__


def get_environment():
    env = Environment(
        loader=PackageLoader('hyp3_metadata', '.'),
        autoescape=select_autoescape(['html.j2', 'xml.j2']),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    return env


def render_template(template: str, payload: dict):
    env = get_environment()
    template = env.get_template(template)
    rendered = template.render(payload)
    return rendered


def get_dem_resolution(dem_name: str):
    data = {
        'NED13': '1/3 arc seconds (about 10 meters)',
        'NED1': '1 arc second (about 30 meters)',
        'NED2': '2 arc seconds (about 60 meters)',
        'SRTMGL1': '1 arc second (about 30 meters)',
        'SRTMGL3': '3 arc seconds (about 90 meters)',
    }
    return data[dem_name]


def get_dem_template_id(dem_name: str):
    if dem_name.startswith('EU'):
        return 'eu'
    if dem_name.startswith('GIMP'):
        return 'gimp'
    if dem_name.startswith('NED'):
        return 'ned'
    if dem_name.startswith('REMA'):
        return 'rema'
    if dem_name.startswith('SRTM'):
        return 'srtm'
    raise NotImplementedError(f'Unkown DEM: {dem_name}')


def get_projection(srs_wkt):
    srs = osr.SpatialReference()
    srs.ImportFromWkt(srs_wkt)
    return srs.GetAttrValue('projcs')


def get_granule_type(granule_name):
    granule_type = granule_name[7:10]
    if granule_type == 'SLC':
        return 'SLC', 'Single-Look Complex'
    if granule_type == 'GRD':
        return 'GRD', 'Ground Range Detected'


def marshal_metadata(product_dir: Path, granule_name: str, dem_name: str, processing_date: datetime,
                     resolution: float, radiometry: str, scale: str, filter_applied: bool, looks: int,  # TODO parse arguments on this line from product dir
                     plugin_name: str, plugin_version: str, processor_name: str, processor_version: str):
    payload = locals()
    payload['metadata_version'] = __version__

    payload['granule_type'], payload['granule_description'] = get_granule_type(granule_name)

    payload['dem_resolution'] = get_dem_resolution(dem_name)
    if product_dir.name[37] == 'p':  # TODO name decoding function?
        payload['scale'] = 'power'
    else:
        payload['scale'] = 'amplitude'

    return payload


def create_readme(payload: dict):
    payload = copy.deepcopy(payload)
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}.png'  # FIXME: use product(s)?

    info = gdal.Info(str(reference_file), format='json')
    payload['pixel_spacing'] = info['geoTransform'][1]
    payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

    content = render_template(f'readme.md.txt.j2', payload)
    output_file = payload['product_dir'] / f'{payload["product_dir"].name}.README.md.txt'
    with open(output_file, 'w') as f:
        f.write(content)

    return output_file


def create_dem_xml(payload: dict):
    payload = copy.deepcopy(payload)
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_dem.tif'

    info = gdal.Info(str(reference_file), format='json')
    payload['pixel_spacing'] = info['geoTransform'][1]
    payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

    payload['thumbnail_binary_string'] = b''  # TODO

    dem_template_id = get_dem_template_id(payload['dem_name'])
    content = render_template(f'dem-{dem_template_id}.xml.j2', payload)
    output_file = reference_file.parent / f'{reference_file.name}.xml'
    with open(output_file, 'w') as f:
        f.write(content)

    return output_file


def create_browse_xml(payload: dict):
    payload = copy.deepcopy(payload)
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}.png'

    if reference_file.name.endswith('_rgb.png'):
        browse_scale = 'color'
    else:
        browse_scale = 'greyscale'

    info = gdal.Info(str(reference_file), format='json')
    payload['pixel_spacing'] = info['geoTransform'][1]
    payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

    payload['thumbnail_binary_string'] = b''  # TODO

    content = render_template(f'browse-{browse_scale}.xml.j2', payload)
    output_file = reference_file.parent / f'{reference_file.name}.xml'
    with open(output_file, 'w') as f:
        f.write(content)

    return output_file

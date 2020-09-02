from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape, StrictUndefined
from osgeo import gdal, osr

from hyp3_metadata import __version__


def get_environment():
    env = Environment(
        loader=PackageLoader('hyp3_metadata', '.'),
        autoescape=select_autoescape(['html', 'xml']),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def render_template(template: str, payload: dict):
    env = get_environment()
    template = env.get_template(template)
    rendered = template.render(payload)
    return rendered


def get_dem_resolution(dem_name):
    data = {
        'NED13': '1/3 arc seconds (about 10 meters)',
        'NED1': '1 arc second (about 30 meters)',
        'NED2': '2 arc seconds (about 60 meters)',
        'SRTMGL1': '1 arc second (about 30 meters)',
        'SRTMGL3': '3 arc seconds (about 90 meters)',
    }
    return data[dem_name]


def get_projection(srs_wkt):
    srs = osr.SpatialReference()
    srs.ImportFromWkt(srs_wkt)
    return srs.GetAttrValue('projcs')


def get_granule_type(granule_name):
    type = granule_name[7:10]
    if type == 'SLC':
        return 'SLC', 'Single-Look Complex'
    if type == 'GRD':
        return 'GRD', 'Ground Range Detected'


def create_rtc_gamma_readme(readme_filename: Path, granule_name: str, resolution: float, radiometry: str,
                            scale: str, filter_applied: bool, looks: int, projection: str, dem_name: str,
                            plugin_version: str, gamma_version: str, processing_date: datetime):
    payload = locals()
    payload['dem_resolution'] = get_dem_resolution(dem_name)
    content = render_template('GAMMA/RTC/README_RTC_GAMMA.txt', payload)
    with open(readme_filename, 'w') as f:
        f.write(content)


def create_dem_xml(output_filename: Path, dem_filename: Path, dem_name: str, processing_date: datetime,
                   plugin_version: str, gamma_version: str, granule_name: str):
    payload = locals()

    payload['dem_resolution'] = get_dem_resolution(dem_name)

    payload['granule_type'], payload['granule_description'] = get_granule_type(granule_name)

    if dem_filename.name[37] == 'p':  # TODO name decoding function?
        payload['scale'] = 'power'
    else:
        payload['scale'] = 'amplitude'

    info = gdal.Info(str(dem_filename), format='json')
    payload['pixel_spacing'] = info['geoTransform'][1]
    payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

    payload['thumbnail_binary_string'] = b''  # TODO

    content = render_template('GAMMA/RTC/RTC_GAMMA_Template_dem_SRTM.xml', payload)
    with open(output_filename, 'w') as f:
        f.write(content)


def create_browse_xml(output_filename: Path, browse_filename: Path, processing_date: datetime,
                      dem_name: str, plugin_name: str, plugin_version: str, gamma_version: str, granule_name: str):
    payload = locals()
    payload['metadata_version'] = __version__

    payload['granule_type'], payload['granule_description'] = get_granule_type(granule_name)

    if browse_filename.name[37] == 'p':  # TODO name decoding function?
        payload['scale'] = 'power'
    else:
        payload['scale'] = 'amplitude'

    if browse_filename.name.endswith('_rgb.png'):
        browse_scale = 'color'
    else:
        browse_scale = 'greyscale'

    info = gdal.Info(str(browse_filename), format='json')
    payload['pixel_spacing'] = info['geoTransform'][1]
    payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

    payload['thumbnail_binary_string'] = b''  # TODO

    content = render_template(f'browse-{browse_scale}.j2', payload)
    with open(output_filename, 'w') as f:
        f.write(content)

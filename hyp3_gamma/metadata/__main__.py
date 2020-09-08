import copy
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from osgeo import gdal, osr

from hyp3_metadata import __version__


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


def get_rtc_metadata_files(product_dir: Path, granule_name: str, dem_name: str, processing_date: datetime, 
                           looks: int, plugin_name: str, plugin_version: str, processor_name: str, 
                           processor_version: str) -> Path:
    payload = marshal_metadata(
        product_dir=product_dir,
        granule_name=granule_name,
        dem_name=dem_name,
        processing_date=processing_date.strptime('2020-01-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z'),
        looks=looks,
        plugin_name=plugin_name,
        plugin_version=plugin_version,
        processor_name=processor_name,
        processor_version=processor_version,
    )
    create_readme(payload)
    create_product_xmls(payload)
    create_dem_xml(payload)
    create_browse_xml(payload)
    create_inc_map_xml(payload)
    create_ls_map_xml(payload)

def get_dem_resolution(dem_name: str) -> str:
    data = {
        'NED13': '1/3 arc seconds (about 10 meters)',
        'NED1': '1 arc second (about 30 meters)',
        'NED2': '2 arc seconds (about 60 meters)',
        'SRTMGL1': '1 arc second (about 30 meters)',
        'SRTMGL3': '3 arc seconds (about 90 meters)',
    }
    return data[dem_name]


def get_dem_template_id(dem_name: str) -> str:
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


def get_projection(srs_wkt) -> str:
    srs = osr.SpatialReference()
    srs.ImportFromWkt(srs_wkt)
    return srs.GetAttrValue('projcs')


def get_granule_type(granule_name) -> Tuple[str, str]:
    granule_type = granule_name[7:10]
    if granule_type == 'SLC':
        return 'SLC', 'Single-Look Complex'
    if granule_type == 'GRD':
        return 'GRD', 'Ground Range Detected'


# FIXME: in hyp3_rtc_gamma.rtc_sentinel as well -- move to hyp3lib?
def get_polarizations(product_polarization):
    mapping = {
        'SH': ('HH',),
        'SV': ('VV',),
        'DH': ('HH', 'HV'),
        'DV': ('VV', 'VH'),
    }
    return mapping[product_polarization]


def decode_product(product_dir: Path) -> dict:
    product_parts = product_dir.name.split('_')
    user_options = product_parts[-2]

    return {'resolution': int(product_parts[-4][-2:]),
            'radiometry': 'gamma-0' if user_options[0] == 'g' else 'sigma-0',
            'scale': 'power' if user_options[1] == 'p' else 'amplitude',
            'masked': False if user_options[2] == 'u' else True,
            'filter_applied': False if user_options[3] == 'n' else True,
            'clipped': False if user_options[4] == 'e' else True,
            'matching': False if user_options[5] == 'd' else True,
            'polarizations': product_parts[-5][:2],
            }


def marshal_metadata(product_dir: Path, granule_name: str, dem_name: str, processing_date: datetime, looks: int,
                     plugin_name: str, plugin_version: str, processor_name: str, processor_version: str) -> dict:
    payload = locals()
    payload['metadata_version'] = __version__

    payload.update(decode_product(product_dir))

    payload['granule_type'], payload['granule_description'] = get_granule_type(granule_name)

    payload['dem_resolution'] = get_dem_resolution(dem_name)

    create_readme(payload)
    create_product_xmls(payload)
    create_dem_xml(payload)
    create_browse_xml(payload)
    create_inc_map_xml(payload)
    create_ls_map_xml(payload)


def create_readme(payload: dict) -> Path:
    payload = copy.deepcopy(payload)

    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}.png'  # FIXME: use product(s)?

    return create(payload, 'readme.md.txt.j2', reference_file, out_ext='README.md.txt',
                  strip_ext=True, thumbnail=False)


def create_product_xmls(payload: dict) -> List[Path]:
    payload = copy.deepcopy(payload)

    output_files = []
    for pol in get_polarizations(payload['polarizations']):
        payload['pol'] = pol
        reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_{pol}.tif'

        output_files.append(
            create(payload, 'product.xml.j2', reference_file)
        )

    return output_files


def create_dem_xml(payload: dict) -> Path:
    payload = copy.deepcopy(payload)
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_dem.tif'

    dem_template_id = get_dem_template_id(payload['dem_name'])

    return create(payload, f'dem/dem-{dem_template_id}.xml.j2', reference_file)


def create_browse_xml(payload: dict) -> Path:
    payload = copy.deepcopy(payload)
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}.png'

    if reference_file.name.endswith('_rgb.png'):
        browse_scale = 'color'
    else:
        browse_scale = 'greyscale'

    return create(payload, f'browse/browse-{browse_scale}.xml.j2', reference_file)


def create_inc_map_xml(payload: dict) -> Path:
    payload = copy.deepcopy(payload)
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_inc_map.tif'
    return create(payload, 'inc_map.xml.j2', reference_file)


def create_ls_map_xml(payload: dict) -> Path:
    payload = copy.deepcopy(payload)
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_ls_map.tif'
    return create(payload, 'ls_map.xml.j2', reference_file)


def create(payload: dict, template: str, reference_file: Path = None, out_ext: str = 'xml',
           strip_ext: bool = False, thumbnail: bool = True) -> Path:
    if reference_file:
        info = gdal.Info(str(reference_file), format='json')
        payload['pixel_spacing'] = info['geoTransform'][1]
        payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

    if reference_file and thumbnail:
        payload['thumbnail_binary_string'] = b''  # TODO

    content = render_template(template, payload)
    out_name = reference_file.name if not strip_ext else reference_file.stem
    output_file = reference_file.parent / f'{out_name}.{out_ext}'
    with open(output_file, 'w') as f:
        f.write(content)

    return output_file

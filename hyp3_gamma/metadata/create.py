from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from osgeo import gdal

from hyp3_metadata.util import render_template, get_dem_template_id, get_projection, \
    strip_polarization, get_thumbnail_encoded_string, marshal_metadata


def create_metadata_file_set_rtc(product_dir: Path, granule_name: str, dem_name: str, processing_date: datetime,
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
        create_rgb_xml,
    ]
    for generator in generators:
        output = generator(payload)
        if isinstance(output, list):
            files.extend(output)
        elif isinstance(output, Path):
            files.append(output)

    return files


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


def create_rgb_xml(payload: dict) -> Path:
    reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_rgb.tif'
    return create_metadata_file(payload, 'rgb.xml.j2', reference_file)


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

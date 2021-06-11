import shutil
from copy import deepcopy
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import List, Optional

from osgeo import gdal

import hyp3_metadata
from hyp3_metadata import data
from hyp3_metadata import util


SUPPORTED_DEMS = ['EU_DEM_V11', 'GIMP', 'IFSAR', 'NED13', 'NED1', 'NED2', 'REMA', 'SRTMGL1', 'SRTMGL3', 'GLO-30']


class RtcMetadataWriter:
    def __init__(self, payload: dict):
        self.payload = payload

    def create_metadata_file_set(self):
        files = []
        generators = [
            self.create_product_xmls,
            self.create_browse_xmls,
            self.create_readme,
            self.create_dem_xml,
            self.create_inc_map_xml,
            self.create_ls_map_xml,
            self.create_area_xml,
            self.create_rgb_xml,
        ]
        for generator in generators:
            output = generator()
            if isinstance(output, list):
                files.extend(output)
            elif isinstance(output, Path):
                files.append(output)

        return files

    def create_readme(self) -> Path:
        reference_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}_' \
                                                       f'{self.payload["polarizations"][0]}.tif'

        return self.create_metadata_file(self.payload, 'rtc/readme.md.txt.j2', reference_file, out_ext='README.md.txt',
                                         strip_ext=True, strip_pol=True
                                         )

    def create_product_xmls(self) -> List[Path]:
        payload = deepcopy(self.payload)

        output_files = []
        for pol in payload['polarizations']:
            payload['pol'] = pol
            reference_file = payload['product_dir'] / f'{payload["product_dir"].name}_{pol}.tif'

            output_files.append(
                self.create_metadata_file(payload, 'rtc/product.xml.j2', reference_file)
            )
        return output_files

    def create_dem_xml(self) -> Path:
        reference_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}_dem.tif'

        dem_template_id = get_dem_template_id(self.payload['dem_name'])
        if dem_template_id is not None:
            return self.create_metadata_file(self.payload, f'dem/dem-{dem_template_id}.xml.j2', reference_file)

    def create_browse_xmls(self) -> List[Path]:
        reference_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}.png'

        output_files = [
            self.create_metadata_file(self.payload, 'browse/browse-greyscale.xml.j2', reference_file),
        ]

        rgb_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}_rgb.png'
        if rgb_file.exists():
            output_files.append(
                self.create_metadata_file(self.payload, 'browse/browse-color.xml.j2', rgb_file)
            )
        return output_files

    def create_inc_map_xml(self) -> Path:
        reference_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}_inc_map.tif'
        return self.create_metadata_file(self.payload, 'rtc/inc_map.xml.j2', reference_file)

    def create_ls_map_xml(self) -> Path:
        reference_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}_ls_map.tif'
        return self.create_metadata_file(self.payload, 'rtc/ls_map.xml.j2', reference_file)

    def create_area_xml(self) -> Path:
        reference_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}_area.tif'
        return self.create_metadata_file(self.payload, 'rtc/area.xml.j2', reference_file)

    def create_rgb_xml(self) -> Path:
        reference_file = self.payload['product_dir'] / f'{self.payload["product_dir"].name}_rgb.tif'
        return self.create_metadata_file(self.payload, 'rtc/rgb.xml.j2', reference_file)

    @classmethod
    def create_metadata_file(cls, payload: dict, template: str, reference_file: Path, out_ext: str = 'xml',
                             strip_ext: bool = False, strip_pol: bool = False) -> Optional[Path]:
        if not reference_file.exists():
            return None

        payload = deepcopy(payload)
        info = gdal.Info(str(reference_file), format='json')
        payload['reference_file'] = reference_file.name
        payload['pixel_spacing'] = info['geoTransform'][1]
        payload['projection'] = util.get_projection(info['coordinateSystem']['wkt'])

        browse_file = reference_file.with_suffix('.png')
        browse_file = browse_file.parent / util.strip_polarization(browse_file.name)
        payload['thumbnail_encoded_string'] = util.get_thumbnail_encoded_string(browse_file)

        content = util.render_template(template, payload)
        out_name = reference_file.name if not strip_ext else reference_file.stem
        if strip_pol:
            out_name = util.strip_polarization(out_name)
        output_file = reference_file.parent / f'{out_name}.{out_ext}'
        with open(output_file, 'w') as f:
            f.write(content)

        return output_file


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
        'polarizations': util.get_polarizations(product_parts[-5][:2]),
    }


def marshal_metadata(product_dir: Path, granule_name: str, dem_name: str, processing_date: datetime, looks: int,
                     plugin_name: str, plugin_version: str, processor_name: str, processor_version: str) -> dict:
    payload = locals()
    payload['metadata_version'] = hyp3_metadata.__version__

    payload.update(decode_product(product_dir.name))

    payload.update(util.get_granule_type(granule_name))

    return payload


def populate_example_data(product_dir: Path):
    product_files = glob(str(Path(data.__file__).parent / 'rtc' / 'rtc*'))
    for f in product_files:
        shutil.copy(f, product_dir / f'{Path(f).name.replace("rtc", product_dir.name)}')

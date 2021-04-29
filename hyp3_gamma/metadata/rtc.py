from copy import deepcopy
from pathlib import Path
from typing import List, Optional

from osgeo import gdal

from hyp3_metadata.util import get_dem_template_id, get_projection, get_thumbnail_encoded_string, render_template, \
    strip_polarization


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

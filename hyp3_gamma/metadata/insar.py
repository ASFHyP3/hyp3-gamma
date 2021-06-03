import shutil
from copy import deepcopy
from glob import glob
from pathlib import Path
from typing import List, Optional

from osgeo import gdal

import hyp3_metadata
from hyp3_metadata import data
from hyp3_metadata.util import get_granule_type, get_projection, get_thumbnail_encoded_string, render_template


class InSarMetadataWriter:
    def __init__(self, payload: dict):
        self.payload = payload
        self.dir = payload['product_dir']
        self.file_name = payload['product_dir'].name

    def create_metadata_file_set(self):
        files = []
        generators = [
            self.create_readme,
            self.create_amp_xml,
            self.create_coherence_xml,
            self.create_dem_tif_xml,
            self.create_los_displacement_xml,
            self.create_look_vector_xmls,
            self.create_browse_xmls,
            self.create_unwrapped_phase_xml,
            self.create_vertical_displacement_xml,
            self.create_wrapped_phase_xml,
        ]
        for generator in generators:
            output = generator()
            if isinstance(output, list):
                files.extend(output)
            elif isinstance(output, Path):
                files.append(output)

        return files

    def create_readme(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_amp.tif'

        return self.create_metadata_file(self.payload, 'insar/readme.md.txt.j2', reference_file,
                                         out_ext='README.md.txt',
                                         strip_ext=True, name_only=True)

    def create_amp_xml(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_amp.tif'
        return self.create_metadata_file(self.payload, 'insar/amp_tif.xml.j2', reference_file)

    def create_coherence_xml(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_corr.tif'
        return self.create_metadata_file(self.payload, 'insar/corr_tif.xml.j2', reference_file)

    def create_dem_tif_xml(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_dem.tif'
        return self.create_metadata_file(self.payload, 'insar/dem.xml.j2', reference_file)

    def create_los_displacement_xml(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_los_disp.tif'
        return self.create_metadata_file(self.payload, 'insar/los_disp_tif.xml.j2', reference_file)

    def create_look_vector_xmls(self) -> List[Path]:
        reference_file_phi = self.dir / f'{self.file_name}_lv_phi.tif'
        reference_file_theta = self.dir / f'{self.file_name}_lv_theta.tif'
        output_files = [
            self.create_metadata_file(self.payload, 'insar/lv_phi_tif.xml.j2', reference_file_phi),
            self.create_metadata_file(self.payload, 'insar/lv_theta_tif.xml.j2', reference_file_theta),
        ]
        return output_files

    def create_browse_xmls(self) -> Path:
        reference_file_col = self.dir / f'{self.file_name}_color_phase.png'
        reference_file_unw = self.dir / f'{self.file_name}_unw_phase.png'
        output_files = [
            self.create_metadata_file(self.payload, 'insar/color_phase_png.xml.j2', reference_file_col),
            self.create_metadata_file(self.payload, 'insar/unw_phase_png.xml.j2', reference_file_unw),
        ]
        return output_files

    def create_unwrapped_phase_xml(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_unw_phase.tif'
        return self.create_metadata_file(self.payload, 'insar/unw_phase_tif.xml.j2', reference_file)

    def create_vertical_displacement_xml(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_vert_disp.tif'
        return self.create_metadata_file(self.payload, 'insar/vert_disp_tif.xml.j2', reference_file)

    def create_wrapped_phase_xml(self) -> Path:
        reference_file = self.dir / f'{self.file_name}_wrapped_phase.tif'
        return self.create_metadata_file(self.payload, 'insar/wrapped_phase_tif.xml.j2', reference_file)

    @classmethod
    def create_metadata_file(cls, payload: dict, template: str, reference_file: Path, out_ext: str = 'xml',
                             strip_ext: bool = False, name_only=False) -> Optional[Path]:
        if not reference_file.exists():
            return None

        payload = deepcopy(payload)
        info = gdal.Info(str(reference_file), format='json')
        payload['pixel_spacing'] = info['geoTransform'][1]
        payload['projection'] = get_projection(info['coordinateSystem']['wkt'])

        payload['thumbnail_encoded_string'] = get_thumbnail_encoded_string(reference_file)

        content = render_template(template, payload)
        out_name = reference_file.name if not strip_ext else reference_file.stem
        if name_only:
            out_name = payload['product_dir'].name

        output_file = reference_file.parent / f'{out_name}.{out_ext}'
        with open(output_file, 'w') as f:
            f.write(content)

        return output_file


def decode_product(product_name):
    product_parts = product_name.split('_')
    return {
        'pol': product_parts[3][:2]
    }


def marshal_metadata(product_dir, granule_name_ref, granule_name_sec, processing_date, looks, dem_name,
                     plugin_name, plugin_version, processor_name, processor_version):
    payload = locals()
    payload['metadata_version'] = hyp3_metadata.__version__
    payload['granule_type'] = get_granule_type(granule_name_ref)['granule_type']
    payload['num_looks'] = looks
    payload['num_looks_range'] = looks[:2]
    payload['num_looks_azimuth'] = looks[3:]

    payload.update(decode_product(product_dir.name))

    return payload


def populate_example_data(product_dir: Path):
    product_files = glob(str(Path(data.__file__).parent / 'insar' / 'insar*'))
    for f in product_files:
        shutil.copy(f, product_dir / f'{Path(f).name.replace("insar", product_dir.name)}')

import shutil
from tempfile import NamedTemporaryFile

from hyp3lib.execute import execute

from hyp3_gamma.dem import get_geometry_from_kml, prepare_dem_geotiff
from hyp3_gamma.insar.water_mask import apply_water_mask


def get_dem_file_gamma(dem_image: str, dem_par: str, safe_dir: str, pixel_size: int, water_masking: bool):
    geometry = get_geometry_from_kml(f'{safe_dir}/preview/map-overlay.kml')
    with NamedTemporaryFile() as dem_tif:
        prepare_dem_geotiff(dem_tif.name, geometry, pixel_size)
        if water_masking:
            apply_water_mask(dem_tif.name, "tmp_masked_file.tif", safe_dir)
            shutil.move("tmp_masked_file.tif", dem_tif.name)

        execute(f'dem_import {dem_tif.name} {dem_image} {dem_par} - - $DIFF_HOME/scripts/egm2008-5.dem '
            f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - - -', uselogging=True)
        #else:
        #    execute(f'dem_import {dem_tif.name} {dem_image} {dem_par} - - $DIFF_HOME/scripts/egm2008-5.dem '
        #        f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - 1', uselogging=True)

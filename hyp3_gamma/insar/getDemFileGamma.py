from tempfile import NamedTemporaryFile

from hyp3lib.execute import execute

from hyp3_gamma.dem import get_geometry_from_kml, prepare_dem_geotiff
from hyp3_gamma.insar.water_mask import get_water_mask

def get_dem_file_gamma(dem_image: str, dem_par: str, safe_dir: str, pixel_size: int):
    geometry = get_geometry_from_kml(f'{safe_dir}/preview/map-overlay.kml')
    with NamedTemporaryFile() as dem_tif:
        prepare_dem_geotiff(dem_tif.name, geometry, pixel_size)
        _ = get_water_mask(dem_tif.name, safe_dir, mask_value=1)
        execute(f'dem_import {dem_tif.name} {dem_image} {dem_par} - - $DIFF_HOME/scripts/egm2008-5.dem '
                f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - - -', uselogging=True)

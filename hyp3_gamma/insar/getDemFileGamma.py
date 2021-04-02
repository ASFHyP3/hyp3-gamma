from typing import Tuple

from hyp3lib.execute import execute

from hyp3_gamma.dem import get_geometry_from_kml, prepare_dem_geotiff


def get_dem_file_gamma(safe_dir: str, azimuth_looks: float) -> Tuple[str, str]:
    dem_tif = 'dem.tif'
    dem_name = 'GLO-30'
    dem_image = 'big.dem'
    dem_par = 'big.par'
    pixel_size = int(azimuth_looks) * 40

    geometry = get_geometry_from_kml(f'{safe_dir}/preview/map-overlay.kml')
    prepare_dem_geotiff(dem_tif, geometry, pixel_size)
    execute(f'dem_import {dem_tif} {dem_image} {dem_par} - - $DIFF_HOME/scripts/egm2008-5.dem '
            f'$DIFF_HOME/scripts/egm2008-5.dem_par - - - 1', uselogging=True)

    return 'big', dem_name

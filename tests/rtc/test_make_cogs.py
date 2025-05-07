import os
import shutil

from osgeo_utils.samples.validate_cloud_optimized_geotiff import validate

from hyp3_gamma.rtc.make_cogs import cogify_dir, cogify_file


def _is_cog(filename):
    warnings, errors, details = validate(filename, full_check=True)
    return errors == []


def test_make_cog(geotiff):
    assert not _is_cog(geotiff)
    cogify_file(geotiff)
    assert _is_cog(geotiff)


def test_cogify_dir(geotiff):
    base_dir = os.path.dirname(geotiff)
    copy_names = [os.path.join(base_dir, '1.tif'), os.path.join(base_dir, '2.tif')]

    for name in copy_names:
        shutil.copy(geotiff, name)

    # Only cogify our copied files
    cogify_dir(base_dir, file_pattern='?.tif')

    for name in copy_names:
        assert _is_cog(name)

    assert not _is_cog(geotiff)

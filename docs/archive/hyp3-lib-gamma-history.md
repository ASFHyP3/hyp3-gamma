# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/) 
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.0](https://scm.asf.alaska.edu/hyp3/hyp3-lib/compare/v0.8.1...v1.0.0)

This is a significant refactor of `hyp3-lib` into a `pip` installable package called `hyp3lib`.

**NOTE:** There are significant changes to the overall repository structure and this will break all 
existing HyP3 workflows!
 
### Removed
 * Any official python 2 support (Note: this version will *likely* still work with python 2, but future versions are
  not expected to)

### Added
* A packaging and testing structure -- now `pip` installable and testing is done via `pytest` and `tox` 
* `hyp3lib.draw_polygon_on_raster` has been included from the depreciated `python_data_utils`
* `hyp3lib.get_asf` has been included from the (now) depreciated `asf_api_assistant`
* A `mkdir_p` function has been added to `hyp3lib.file_subroutines` that will create a directory, and all parent
  directories as needed (works like unix `mkdir -p`)
* 

### Changed
*  All python modules have the `from __future__ import print_function, absolute_import, division, unicode_literals` 
 imports added to make python 2 behave more like python 3 (NOTE: Python 2 is not longer officially supported, but it
  *should* work for this version)
* All of `hyp3-lib/src` is now contained in the `hyp3lib` package
* Any "script" in in hyp3-lib has been turned into an entrypoint with the same name and should mostly function
 identically if `hpy3lib` in installed. This includes:
  * `apply_wb_mask.py`
  * `byteSigmaScale.py`
  * `copy_metadata.py`
  * `createAmp.py`
  * `cutGeotiffsByLine.py`
  * `cutGeotiffs.py`
  * `draw_polygon_on_raster.py`
  * `dem2isce.py`
  * `enh_lee_filter.py`
  * `extendDateline.py`
  * `geotiff_lut.py`
  * `get_bounding.py`
  * `getDemFor.py`
  * `get_asf.py`
  * `get_dem.py`
  * `get_orb.py`
  * `iscegeo2geotif.py`
  * `make_arc_thumb.py`
  * `makeAsfBrowse.py`
  * `makeChangeBrowse.py`
  * `make_cogs.py`
  * `makeColorPhase.py`
  * `makeKml.py`
  * `offset_xml.py`
  * `par_s1_slc_single.py`
  * `ps2dem.py`
  * `raster_boundary2shape.py`
  * `rasterMask.py`
  * `resample_geotiff.py`
  * `rtc2colordiff.py`
  * `rtc2color.py`
  * `simplify_shapefile.py`
  * `SLC_copy_S1_fullSW.py`
  * `subset_geotiff_shape.py`
  * `tileList2shape.py`
  * `utm2dem.py`
  * `verify_opod.py`
* Config files are packaged and accessible programmatically from 
  `os.path.join(os.path.dirname(hyp3lib.etc.__file__), "config")`
* The `repackage_into_cogs.sh` script has been moved into `hyp3lib/etc/bin` 
 and will be distributed as package data. You can get the location
 programmatically via `os.path.abspath(os.path.join(os.path.dirname(hyp3lib.etc.__file__), "bin"))` 
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0](https://github.com/ASFHyP3/hyp3-lib/compare/v1.5.0...v1.6.0)

### Added
* Methodology [documentation of our RGB Decomposition](https://github.com/ASFHyP3/hyp3-lib/blob/develop/docs/rgb_decomposition.md) images created from dual-pol RTC products
* Helper functions for HyP3v2 entrypoints
  * `hyp3lib.aws` for working with AWS
  * `hyp3lib.fetch.write_credentials_to_netrc_file` to write a set of credentials to a `~/.netrc` file
  * `hyp3lib.image` for working with images
  * `hyp3lib.scene` for working with Sentinel-1 scenes
  * `hyp3lib.util` for small utility functions
* `hyp3lib.system.isce_version` to attempt to determine the ISCE version installed


### Fixed
* `hyp3lib.apply_wb_mask` now pulls the base masks from AWS instead of a local directory for portability

### Changed
* Water mask "creation" functions have been merged to `hyp3lib.apply_wb_mask.get_water_mask`. These are
  internal helper functions and not expected to impact users

## [1.5.0](https://github.com/ASFHyP3/hyp3-lib/compare/v1.4.1...v1.5.0)

### Added
* Documented contribution guidelines in `CONTRIBUTING.md`
* `get_dem.get_dem` has a new `dem_type` parameter with options of `utm` (default), `latlon`, and `isce`

### Changed
* Requires python >= 3.6
* `S1_OPOD_vec` calls to apply S1 state vectors to SLC products are now logged. Logging was already in place for GRD
  products.
* Configuration of the `hyp3lib.get_dem` module has seen the following changes:
  * The module will attempt to load `~/.hyp3/get_dem.cfg`; if not found it will load `hyp3lib/etc/config/get_dem.cfg`.
  * `get_dem.cfg` must be a space-delimited file of the form `<dem_name> <location> <epsg_code>`
  * `<location>` may be either a local path (e.g. `/foo/bar/`) or a url prefix (e.g. `https://foo.com/bar/`).
    S3 prefixes are no longer supported (e.g. `s3://foo/bar/`).
  * Shapefiles describing each DEM's coverage are no longer packaged with hyp3lib.  They must now be provided at
    `<location>/coverage/<dem_name>_coverage.shp`.

### Removed
* Removed `hyp3lib.raster_boundary2shape.raster_metadata` because it was an exact duplicate of
  `hyp3lib.asf_time_series.rater_metadata`
* Removed `get_dem.get_ISCE_dem` and `get_dem.get_ll_dem`.  This functionality is now exposed via the new
  `dem_type='isce'` and `dem_type='latlon'` options in `get_dem.get_dem`

## [1.4.1](https://github.com/ASFHyP3/hyp3-lib/compare/v1.4.0...v1.4.1)

### Added
* `get_orb.downloadSentinelOrbitFile`: new `orbit_types` argument to to specify a tuple of orbit types to search
  for, e.g. `('AUX_POEORB', 'AUX_RESORB')`

### Changed
* `ingest_S1_granule`, `par_s1_slc_single`: errors thrown by `S1_OPOD_vec` when applying orbit files are now raised
  rather than caught and ignored
* `get_orb.downloadSentinelOrbitFile`: failures fetching orbits are now logged as warnings and  do not include a stack
  trace
* `get_orb.get_orbit_url`: removed padding on granule start/end times for ESA API searches per example at
  https://qc.sentinel1.eo.esa.int/doc/api/

## [1.4.0](https://github.com/ASFHyP3/hyp3-lib/compare/v1.3.0...v1.4.0)

### Added
* `hyp3lib.OrbitDownloadError` exception that will be raised for fetching orbit file problems
* `hyp3lib.fetch` module with utilities for fetching thing from external endpoints
  * Provides a generic `download_file` utility for downloading files from URLs
* `orbit_file` keyword argument to `hyp3lib.ingest_S1_granule` and `hyp3lib.par_s1_slc_single` to skip fetching an
  already downloaded orbit file
* `providers` keyword argument to `hyp3lib.downloadSentinelOrbitFile` to specify the providers you'd like to check for
  orbit files, in order of preference
* `hyp3lib.get_orb.get_orbit_url` which will determine the OPOD orbit file url for a granule
* `get_orb.py` entrypoint now allows you to download to a specific directory and specify the providers to use in
  order of preference

### Changed
* Unrestricted `gdal` from `2.*` in `conda-env.yml` because there appears to be no GDAL 2 specific code in `hyp3lib`

### Removed
* Unused `par_s1_slc_single.py` entrypoint
* `hyp3lib.get_orb` helper functions that are unused outside of `get_orb`:
  * `getPageContentsESA`, `getOrbitFileESA`, `getPageContents` (ASF), `findOrbFile` (ASF), `getOrbFile` (ASF) have
    all been merged into `get_orbit_url`
  * `dateStr2dateTime` as been removed
  * `fetchOrbitFile` has been eliminated in favor of `hyp3lib.fetch.download_file`
  * `downloadSentinelOrbitFileProvider` functionality has been merged into `downloadSentinelOrbitFile`

## [1.3.0](https://github.com/ASFHyP3/hyp3-lib/compare/v1.2.3...v1.3.0)

### Changed
* Requires `pyproj>=2`
* `makeAsfBrowse.py`
  * now only makes a single `.png` file at the formally `_large.png` resolution
    (by default) as small browse images had little user value
  * CLI includes a `-n`/`--nearest-neighbor` argument to switch from GDAL's cubic
    interpolation to to nearest neighbor when resampling GeoTIFFs.
  * `makeAsfBrose` API includes a `with=2048` keyword argument and the CLI includes
    a `-w`/`--width` to set the browse image width
* `make_cogs.py` no longer includes overviews in cogified files because HyP3's
  products are packaged in a `.zip` file preventing overviews from being accessed
  over the web. This change reduces our output GeoTIFF's by ~25%
  * `make_cog` function that was only used internally has been renamed to
    `cogify_file` to be inline with the `cogify_dir` function provided

### Removed
* `get_dem.py`'s `transform_bounds` and `transform_point` functions that were
  only used internally have been removed because they are no longer relevant with
  the `pyproj` upgrade

### Fixed
* Coordinate transformations in `get_dem` now utilize the `pyproj>=2` syntax
  instead of the depreciated and broken `pyproj<2` syntax

## [1.2.3](https://github.com/ASFHyP3/hyp3-lib/compare/v1.2.2...v1.2.3)

### Fixed
* `get_dem.py` will raise an exception if it cannot determine the NoData value
  for the DEM.

### Changed
* `get_dem.py` will determine the correct NoData value for `SRTMGL3` DEMs

## [1.2.2](https://github.com/ASFHyP3/hyp3-lib/compare/v1.2.1...v1.2.2)

### Fixed
* `rtc2color.py` was applying the cleanup threshold differently to amplitude and
  power data, causing a loss of blue color, which has now been fixed.

### Changed
* `rtc2color.py` no longer performs calculations with the `float16` data type,
  which was selected for memory optimization, and instead uses the native `float32`
  type. Similar memory optimizations have been achieved by refactoring and
  leveraging numpy, with an added benefit of a 6x speedup.

## [1.2.1](https://github.com/ASFHyP3/hyp3-lib/compare/v1.2.0...v1.2.1)

### Added
* `DemError`, `ExecuteError`, and `GeometryError` (subclasses of the generic `Exception`) for
  more targeted error handling

### Fixed
* Updated the `ps2dem.py` to handle the GAMMA 2019 `create_dem_par` interface
* Removed GIMP, REMA, and EU DEMs from the default config (Note: they are still available
  by editing the default config) due to many failures associated with these DEMs
* No library functions will raise a `SystemExit` and will some subclass of `Exception`, as
  would be expected of a library, so that errors can be handled by the calling app
* execute raises a `hyp3lib.ExecuteError` instead of a generic `Exception` for more targeted
  error handling
* `get_asf.py` will not fail silently anymore.

## [1.2.0](https://github.com/ASFHyP3/hyp3-lib/compare/v1.1.0...v1.2.0)

### Added
 * `metadata.add_esa_citation` to add a `ESA_citation.txt` file to a directory
 * `exceptions.GranuleError` for raising issues with granules

## [1.1.0](https://github.com/ASFHyP3/hyp3-lib/compare/v1.0.0...v1.1.0)

### Added
* `GC_map_mod` bash script, which is used by a few science codes (this has been translated to bash from tcsh)
* `hyp3lib.system` module for getting system information needed by the science codes
  * includes a `gamma_version` function which will attempt to determine and validate the GAMMA software version

## [1.0.0](https://github.com/ASFHyP3/hyp3-lib/compare/v0.8.1...v1.0.0)

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

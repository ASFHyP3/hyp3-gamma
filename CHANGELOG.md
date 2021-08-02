# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.7.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.6.0...v4.7.0)

### Added
* Option to apply water masking to output geotiff files produced by gamma processing
  * define the nodata value (minimum_value_datatype) to the dem.tif
    and apply this dem.tif to gamma processing
  * `water_masking` parameter to `ifm_sentinel.insar_sentinel_gamma` function
  * `--apply-watger-mask` parameter to `insar` entrypoint
  * `-m` parameter to `ifm_sentinel.py` script

## [4.6.3](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.6.2...v4.6.3)

### Added
* InSAR products now include an ellipsoidal incidence angle GeoTIFF (in addition to local incidence angle) when
  selecting the `include_inc_map` option.

### Changed
* Upgraded to hyp3-metadata [v1.2.5](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#125)
  from v1.2.4

## [4.6.2](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.6.1...v4.6.2)

### Added
* InSAR products now include a land/water mask GeoTIFF and a corresponding ArcGIS metadata xml file

### Changed
* Upgraded to hyp3-metadata [v1.2.4](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#124)
  from v1.2.3

## [4.6.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.6.0...v4.6.1)

### Changed
* `conda-env.yml` has been renamed to `environment.yml` in-line with community practice

* Upgraded to hyp3-lib [v1.6.8](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#168) from v1.6.7

## [4.6.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.5.1...v4.6.0)

### Added
* `water_map` entrypoint to create a water map product
* Option to output decibel scaled RTC products
  * `--scale` parameter to `rtc` entrypoint now accepts `decibel`
  * `scale` parameter to `rtc_sentinel.rtc_sentinel_gamma` now accepts `decibel`

### Changed
* Upgraded to hyp3-metadata [v1.2.3](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#123)
  from v1.1.0

## [4.5.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.5.0...v4.5.1)

### Added
* `--include-wrapped-phase` option for the `insar` entrypoint to include the wrapped phase GeoTIFF in the output product

### Changed
* Updated the description of the Wrapped Interferogram in the InSAR product README, including the optional GeoTIFF

## [4.5.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.4.0...v4.5.0)

### Added
* Option to include DEM file with InSAR products
  * `include_dem` parameter to `ifm_sentinel.insar_sentinel_gamma` function
  * `--include-dem` parameter to `insar` entrypoint
  * `-d` parameter to `ifm_sentinel.py` script
* Parameter metadata file for InSAR products now includes `Slant range near`, `Slant range center` and  `Slant range far` attributes

## [4.4.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.3.0...v4.4.0)

### Added
* Option to include an Incidence Angle GeoTIFF with InSAR products
  * `include_inc_map` parameter to `ifm_sentinel.insar_sentinel_gamma` function
  * `--include-inc-map` parameter to `insar` entrypoint
  * `-i` parameter to `ifm_sentinel.py` script
* Parameter metadata file for InSAR products now includes `Spacecraft height` and `Earth radius at nadir` attributes

## [4.3.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.2.0...v4.3.0)

### Changed
* InSAR processing via `ifm_sentinel.py` now leverages the
  [Copernicus GLO-30 Public DEM](https://registry.opendata.aws/copernicus-dem/)
* InSAR GeoTIFF files are now aligned to a common 40m (for 10x2 looks) or 80m (for 20x4 looks) pixel grid

## [4.2.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.1.2...v4.2.0)

### Added
* Option for RTC_GAMMA jobs to use either Copernicus GLO-30 Public DEM or legacy SRTM/NED DEMs for processing:
  * `--dem-name` option to `rtc` entrypoint and `rtc_sentinel.py` script
  * `dem_name` parameter to `hyp3_gamma.rtc_sentinel.rtc_sentinel_gamma()`
* `hyp3_gamma.dem` module for preparing GeoTIFF mosaics of the
  [Copernicus GLO-30 Public DEM](https://registry.opendata.aws/copernicus-dem/)

### Changed
* Upgraded to hyp3-metadata [v0.4.2](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#042)
  from v0.2.0

##  [4.1.2](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.1.1...v4.1.2)

### Changed
* Reverted change that allows `ifm_sentinel.py` to proceed with processing when no Restituted or
  Precision orbit file is found. Restituted or Precision orbit files are required.

##  [4.1.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.1.0...v4.1.1)

### Changed
* `ifm_sentinel.py` will now proceed with processing when no Restituted or Precision orbit file is found
* Upgraded to hyp3lib [v1.6.7](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#167) from v1.6.6

## [4.1.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.0.5...v4.1.0)

### Added
* Ability to include an RGB decomposition GeoTIFF in RTC output
  * an `--include-rgb` option has been added to `rtc_sentinel.py`
  * an `include_rgb` keyword argument has been added to `hyp3_gamma.rtc.rtc_sentinel.rtc_sentinel_gamma`

### Changed
* Upgraded to hyp3lib [v1.6.6](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#166) from v1.6.5

## [4.0.5](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.0.4...v4.0.5)

### Changed

* `rtc` now uploads unzipped product files (in addition to the zip archive) when using the `--bucket` option
* Upgraded to hyp3lib [v1.6.5](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#165) from v1.6.4

## [4.0.4](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.0.3...v4.0.4)

### Changed

* `rtc_sentinel.py` will now proceed with processing when no Restituted or Precision orbit file is found

## [4.0.3](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.0.2...v4.0.3)

### Fixed

* Resolved off-by-one error when computing days of separation for InSAR product names in `ifm_sentinel.py`

## [4.0.2](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.0.1...v4.0.2)

### Changed

* Upgraded to hyp3lib [v1.6.4](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#164) from v1.6.3

## [4.0.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v4.0.0...v4.0.1)

### Added

* Added wrapped phase geotiff via command line option `-m` to `ifm_sentinel.py`

## [4.0.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v3.1.0...v4.0.0)

RTC processing via `rtc_sentinel.py` has been significantly refactored, and a number of legacy options have been
removed.

### Added
* `rtc.util.unzip_granule()` unzips a S1 zip file and returns the .SAFE directory name

### Changed
* The parameters to `rtc_sentinel.py` and `rtc.rtc_sentinel.rtc_sentinel_gamma()` have been significantly revised.
  Review the corresponding help for more details:
  * `rtc_sentinel.py --help`
  * `from hyp3_gamma.rtc.rtc_sentinel import rtc_sentinel_gamma; help(rtc_sentinel_gamma)`
* A refactored `rtc.coregistration` module has replaced `rtc.check_coreg`. The `check_coreg.py` entrypoint has been
  removed.
* Upgraded to hyp3_metadata [v0.2.0](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#020)
  from v0.1.4

### Removed
* Legacy support for the GIMP and REMA DEMs has been removed, including the `rtc.smoothem` module and the corresponding
  `smoothem.py` entrypoint.
* User-provided DEMs in GAMMA format are no longer supported. DEMs in GeoTIFF format are still supported.
* The `output/out_name` options to set the name of the output product have been removed.
* The `shape` option to subset to the bounds of a shapefile has been removed. Subsetting to a bounding box or to a
  user-provided DEM are still supported.
* The `terms` option has been removed. DEM matching will always use a one-term offset polynomial.
* The `par` option to provide a pre-generated `diff_par` offset file has been removed.
* The `fail/dead_flag` options have been removed. Processing will always proceed using dead reckoning when
  `dem_matching` is selected and co-registration fails.
* `hyp3_gamma.util.find_and_remove()` has been removed.

## [3.1.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v3.0.0...v3.1.0)

### Added
* `hyp3-insar-gamma` [v2.2.1](https://github.com/ASFHyP3/hyp3-insar-gamma/blob/develop/CHANGELOG.md#221)
  has been merged into HyP3 GAMMA at `hyp3_gamma.insar` to provide InSAR processing
  of Sentinel-1. `hyp3_gamma` now provides these additional entrypoints:
  * `insar` provides the InSAR process interface to HyP3
  * `ifm_sentinel.py` is the InSAR (science code) processor
  * `interf_pwr_s1_lt_tops_proc.py` for coregistering Sentinel-1 SLC data and DEMs
  * `unwrapping_geocoding.py` for unwrapping and geocoding Sentinel-1 INSAR products from GAMMA

### Changed
* `hyp3-gamma` entrypoint now allows InSAR processing through the `++process insar` option

## [3.0.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.4.1...v3.0.0)

**HyP3 RTC GAMMA as been transformed into HyP3 GAMMA; a *processor* based plugin**

### Changed
* `hyp3_rtc_gamma` has been transformed into a `hyp3_gamma` package
    * `hyp3_rtc_gamma.__init__` has moved to `hyp3_gamma.__init__`
    * `hyp3_rtc_gamma.__main__` has moved to `hyp3_gamma.__main__`
    * `hyp3_rtc_gamma.check_coreg` has moved to `hyp3_gamma.rtc.check_coreg`
    * `hyp3_rtc_gamma.rtc_sentinel` has moved to `hyp3_gamma.rtc.rtc_sentinel`
    * `hyp3_rtc_gamma.smoothem` has moved to `hyp3_gamma.rtc.smoothem`

* `hyp3_gamma` now provides these entrypoints:
    * `hyp3_gamma` is the main HyP3 entrypoint
    * `rtc` provides the RTC process interface to HyP3
    * `rtc_sentinel.py` is the RTC (science code) processor
    * `check_coreg.py` for checking the results of the GAMMA coregistration process
    * `smoothdem.py` for smoothing and filling holes in DEMs

## [2.4.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.4.0...v2.4.1)

### Changed
* `rtc_sentinel.py` now uses GAMMA's updated `mk_geo_radcal2` instead of `mk_geo_radcal`
  to remove no-data values in lakes and rivers

* Upgraded to hyp3lib [v1.6.3](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#163) from v1.6.2

## [2.4.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.3.4...v2.4.0)

**HyP3 v1 is no longer supported as of this release.**

### Added
* A new `--include-scattering-area` option has been added to `rtc_sentinel.py` and `hyp3_rtc_gamma_v2`
  to include a geotiff of scattering area in the product package.  This supports creation of composites
  of RTC images using Local Resolution Weighting per Small (2012) https://doi.org/10.1109/IGARSS.2012.6350465.

### Changed
* Upgraded to hyp3_metadata [v0.1.4](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#014) from v0.1.2

### Removed
* `rtc_sentinel.py` no longer creates a flattened backscatter image.
* The `hyp3_rtc_gamma` package entrypoint and HyP3 v1 support has been removed.
* `rtc_gamma` package entrypoint will now pass arguments to the `hyp3_rtc_gamma_v2` entrypoint by default.

### Fixed
* `rtc_sentinel.py` now runs successfully when `--nocrosspol` is specified ([#179](https://github.com/ASFHyP3/hyp3-gamma/issues/179))

## [2.3.4](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.3.3...v2.3.4)

### Changed
- Upgraded to hyp3lib [v1.6.2](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#162) from v1.6.1

## [2.3.3](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.3.2...v2.3.3)

### Changed
- Upgraded to hyp3lib [v1.6.1](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#161) from v1.6.0

## [2.3.2](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.3.1...v2.3.2)

### Changed
- Upgraded to hyp3lib [v1.6.0](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#160) from v1.5.0
- Upgraded to hyp3_metadata [v0.1.2](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#012) from v0.1.1

## [2.3.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.3.0...v2.3.1)

### Changed
* `README.txt` has been renamed to `README.md.txt`
* `README.md.txt` and `.xml` files are now generated using [hyp3-metadata-templates v0.1.1](https://github.com/ASFHyP3/hyp3-metadata-templates/blob/develop/CHANGELOG.md#011)
* `file_type` tags are now applied to browse and thumbnail images uploaded to S3 to facilitate consistent ordering in HyP3 Api responses

### Removed
* Removed the all-white placeholder thumbnail from `_ls_map.tif.xml`

## [2.3.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.2.0...v2.3.0)

### Added
* Added cursory developer setup instructions in `README.md`

### Changed
* Upgraded to [hyp3-lib v1.5.0](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#150) from v1.4.1.

### Removed
* RTC Gamma products no longer include an ISO 19115-2 .iso.xml metadata file.
* ASF MapReady is no longer a dependency and has been removed.

## [2.2.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.1.1...v2.2.0)

### Changed
* Files now get uploaded to S3 with a `file_type` in v2 tag indicating what the file is
* Files no longer get a prefix based on file type in v2
* Removed `lo_flag` from `rtc_sentinel` since it duplicates the functionality of `resolution`

## [2.1.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.1.0...v2.1.1)

### Changed
* Input scenes are now downloaded directly from NGAP distribution endpoint rather than ASF's datapool 
* Updates the output product README to include usage guidelines with acknowledgment and citation information
* Removes the `ESA_citation.txt` file from the output product as it's included in the README
* Drops the "This is an RTc product from ..." blurb from the bottom of product notification emails
* Incompatible granules will fail much earlier in the processing chain

### Removed
* Non-functional support for non-Sentinel-1 products

## [2.1.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.6...v2.1.0)

### Changed
* Implemented new naming convention for output products.  The names of output zips, folders, and files now all share a
  common format.
* Revised README content:
  * Updated description of product naming scheme
  * Removed references to EUDEM, GEMP, and REMA DEMs that are no longer used since v2.0.0.
  * Clarified which RTC processing steps are performed when DEM matching is or is not requested.
* Orbit files are now downloaded once at the start of processing, rather than once for each polarization image.
* Orbit search priority is now POEORB from ESA, POEORB from ASF, RESORB from ESA, RESORB from ASF.
* `main_v2()` now downloads Sentinel-1 data directly from ASF's NGAP distribution endpoint, rather than datapool.
* Upgrade to [hyp3-lib v1.4.1](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#141) from 1.3.0.
* Install hyp3-lib via conda instead of pip

## [2.0.6](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.5...v2.0.6)

### Fixed
* Resolved issue where thumbnail filenames ended in ..png rather than .png

## [2.0.5](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.4...v2.0.5)

### Added
* The v2 entrypoint will now create and upload thumbnail images to S3 in addition to browse images

## [2.0.4](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.3...v2.0.4)

### Changed
* The v2 entrypoint will now upload browse images and thumnail images in addition to the zip file.
* Upgrade to [hyp3-lib 1.3.0](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#130).
  In particular, geotiff products no longer include overviews.
* Eliminated seprate "low-res" (1024x) and "high-res" (2048x) browse image resolutions in favor of a single 2048x image.

## [2.0.3](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.2...v2.0.3)

### Fixed
* Updates the minimum required `hyp3lib` and `hyp3proclib` version to bring in the
  [`get_dem.py` NoData bugfix](https://github.com/ASFHyP3/hyp3-lib/pull/175) and
  the [`default_rtc_resolution` bugfix](https://github.com/asfadmin/hyp3-proc-lib/pull/4),
  respectively

## [2.0.2](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.1...v2.0.2)

### Changed
* The v2 entrypoint will now make up to three retry attempts if it fails to download the input 
  granule from the ASF archive.
* Changed the name of the product README file to `<product_name>.README.txt`,
  e.g. `S1A_IW_RT30_20170708T161200_G_gpn.README.txt`
* Calls to mk_geo_radcal will no longer include the `-j do not use layover-shadow map in the calculation of pixel_area`
  flag.  The layover-shadow map will now be consistently applied to all products.
* Upgraded to [hyp3-lib v1.2.2](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#v122)
* Removed custom blank_bad_data.py from mk_geo_radcal processing.  Border pixels for older GRD products
  are now cleaned using the default `make_edge` setting of `par_S1_GRD`.

## [2.0.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.0...v2.0.1)

### Changed
* hyp3-v2 output products are now packaged in a .zip file similar to hyp3-v1 products

## [2.0.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v1.3.1...v2.0.0)

This is a significant refactor of `hyp3-gamma` into:
* A `pip` installable package called `hyp3_rtc_gamma`
* A stand alone, container-based HyP3 plugin

**NOTE:** There are significant changes to the overall repository structure and
will break all existing HyP3 workflows!

### Removed
* Python 2. This package now requires Python 3.6+
* A patched version of GAMMA's `mk_geo_radcal` and an associated `blank_bad_data.py` script

### Added
* A packaging and testing structure -- now pip installable and testing is done via pytest
  * Previous command line scripts are now registered entrypoints and created when the package is `pip` installed:
    * `check_coreg.py`
    * `rtc_sentinel.py`
    * `smooth_dem_tiles.py`
    * 'xml2meta.py'
* A Dockerfile to build the HyP3 plugin
* A CI/CD workflow setup, which will build and publish the docker container
* The processing script that used to live in the now depreciated `cloud-proj` repository has been moved into the
package as `hyp3_rtc_gamma.__main__` and also registered as a `hyp3_rtc_gamma` entrypoint
* A second, in development, entrypoint for HyP3 v2 has been added to `hyp3_rtc_gamma.__main__`

### Changed
* All of `src/` is now contained in the `hyp3_rtc_gamma` package
* All of `etc/`is now contained in `hyp3_rtc_gamma.etc`
* The version number is now tracked automatically via git tags instead of in `etc/version.txt`

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.3.2...v3.0.0)

This is a MAJOR restucturing of HyP3's GAMMA based processes. Starting with hyp3-rtc-gamma,
hyp3-rtc-gamma [v2.3.2](https://github.com/ASFHyP3/hyp3-gamma/releases/tag/v2.3.2),
hyp3-insar-gamma [v2.2.0](https://github.com/ASFHyP3/hyp3-insar-gamma/releases/tag/v2.2.0),
hyp3-geocode [v1.0.1](https://github.com/asfadmin/hyp3-geocode/releases/tag/v1.0.1),
and the GAMMA specific functionality of hyp3lib [v1.6.0](https://github.com/ASFHyP3/hyp3-lib/releases/tag/v1.6.0)
have been merged into a single hyp3-gamma plugin, as represented here.

### Added
* A unified HyP3v2 entrypoint, `hyp3_gamma`, which will run any of the available science processes
* A Jupter (lab or notebook) prototyping environment to the plugin's `Dockerfile` which is created by
  either targeting the prototype environment (with a `--target prototype` docker build argument) *or by default*.
  HyP3 production containers are built with `--target production` and do not include the prototyping environment.

### Changed
* `hyp3_rtc_gamma_v2` entrypoint is now an `rtc` entrypoint
* `insar_gamma` entrypoint is now an `insar` entrypoint

### Removed
* HyP3v1 entrypoints are no longer provided
* Entrypoints for previously hyp3lib modules `ps2dem.py`, `SLC_copy_S1_fullSW.py`, and `utm2dem.py`
  are no longer provided
* RTC entrypoints `check_coreg.py` and `smooth_dem_tiles.py` are no longer provided
* InSAR entrypoints `interf_pwr_s1_lt_tops_proc.py` and `unwrapping_geocoding.py` are no longer provided

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
* Upgrade to [hyp3-lib 1.3.0](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#130).  In particular, geotiff products no longer include overviews.
* Eliminated seprate "low-res" (1024x) and "high-res" (2048x) browse image resolutions in favor of a single 2048x image.

## [2.0.3](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.2...v2.0.3)

### Fixed
* Updates the minimum required `hyp3lib` and `hyp3proclib` version to bring in the
  [`get_dem.py` NoData bugfix](https://github.com/ASFHyP3/hyp3-lib/pull/175) and
  the [`default_rtc_resolution` bugfix](https://github.com/asfadmin/hyp3-proc-lib/pull/4),
  respectively

## [2.0.2](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.1...v2.0.2)

### Changed
* The v2 entrypoint will now make up to three retry attempts if it fails to download the input granule from the ASF archive.
* Changed the name of the product README file to `<product_name>.README.txt`, e.g. `S1A_IW_RT30_20170708T161200_G_gpn.README.txt`
* Calls to mk_geo_radcal will no longer include the `-j do not use layover-shadow map in the calculation of pixel_area` flag.  The layover-shadow map will now be consistently applied to all products.
* Upgraded to [hyp3-lib v1.2.2](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#v122)
* Removed custom blank_bad_data.py from mk_geo_radcal processing.  Border pixels for older GRD products are now cleaned using the default `make_edge` setting of `par_S1_GRD`.

## [2.0.1](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.0.0...v2.0.1)

### Changed
* hyp3-v2 output products are now packaged in a .zip file similar to hyp3-v1 products

## [2.0.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v1.3.1...v2.0.0)

This is a significant refactor of `hyp3-rtc-gamma` into:
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

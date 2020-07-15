# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.6](https://github.com/ASFHyP3/hyp3-rtc-gamma/compare/v2.0.5...v2.0.6)

### Fixed
* Resolved issue where thumbnail filenames ended in ..png rather than .png

## [2.0.5](https://github.com/ASFHyP3/hyp3-rtc-gamma/compare/v2.0.4...v2.0.5)

### Added
* The v2 entrypoint will now create and upload thumbnail images to S3 in addition to browse images

## [2.0.4](https://github.com/ASFHyP3/hyp3-rtc-gamma/compare/v2.0.3...v2.0.4)

### Changed
* The v2 entrypoint will now upload browse images and thumnail images in addition to the zip file.
* Upgrade to [hyp3-lib 1.3.0](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#130).  In particular, geotiff products no longer include overviews.
* Eliminated seprate "low-res" (1024x) and "high-res" (2048x) browse image resolutions in favor of a single 2048x image.

## [2.0.3](https://github.com/ASFHyP3/hyp3-rtc-gamma/compare/v2.0.2...v2.0.3)

## Fixed
* Updates the minimum required `hyp3lib` and `hyp3proclib` version to bring in the
  [`get_dem.py` NoData bugfix](https://github.com/ASFHyP3/hyp3-lib/pull/175) and
  the [`default_rtc_resolution` bugfix](https://github.com/asfadmin/hyp3-proc-lib/pull/4),
  respectively

## [2.0.2](https://github.com/ASFHyP3/hyp3-rtc-gamma/compare/v2.0.1...v2.0.2)

### Changed
* The v2 entrypoint will now make up to three retry attempts if it fails to download the input granule from the ASF archive.
* Changed the name of the product README file to `<product_name>.README.txt`, e.g. `S1A_IW_RT30_20170708T161200_G_gpn.README.txt`
* Calls to mk_geo_radcal will no longer include the `-j do not use layover-shadow map in the calculation of pixel_area` flag.  The layover-shadow map will now be consistently applied to all products.
* Upgraded to [hyp3-lib v1.2.2](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#v122)
* Removed custom blank_bad_data.py from mk_geo_radcal processing.  Border pixels for older GRD products are now cleaned using the default `make_edge` setting of `par_S1_GRD`.

## [2.0.1](https://github.com/ASFHyP3/hyp3-rtc-gamma/compare/v2.0.0...v2.0.1)

### Changed
* hyp3-v2 output products are now packaged in a .zip file similar to hyp3-v1 products

## [2.0.0](https://github.com/ASFHyP3/hyp3-rtc-gamma/compare/v1.3.1...v2.0.0)

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

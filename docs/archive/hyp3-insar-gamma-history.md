# Changelog

All notable changes to the hyp3-insar-gamma plugin, before being merged into the
general hyp3-gamma plugin, are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/) 
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0](https://github.com/ASFHyP3/hyp3-insar-gamma/compare/v2.1.2...v2.2.0)

**HyP3 v1 is no longer supported as of this release.**

### Added
* Added a `--include-look-vectors` option to `insar_gamma` to include the look vector theta and phi files in the output product package 

### Changed
* Implemented a new product naming scheme, detailed in the `_README.md.txt` file included with each product.

### Removed
* Removed the `--include-inc-map` option from `insar_gamma`.
* The following parameters have been removed from `ifm_sentinel.py`:
  * `output` Output igram directory
  * `--dem` Input DEM file to use
  * `-i` Create incidence angle file
  * `-o` Use opentopo to get the DEM file instead of get_dem
  * `-c` cross pol processing - either hv or vh (default hh or vv)
  * `-t` Start processing at time for length bursts
  * `-m` Apply water body mask to DEM file prior to processing
* The following package entrypoints have been removed:
  * `procS1StackGAMMA.py`: Generating pair-wise interferograms from a list of input scenes is no longer supported.
  * `par_s1_slc.py`: This script has been replaced in favor of `hyp3lib.par_s1_slc_single.`
  * `hyp3_insar_gamma`, `hyp3_insar_gamma_v2`: Support for HyP3 v1 has been removed.  HyP3 processing is now invoked directly via `insar_gamma`.

## [2.1.2](https://github.com/ASFHyP3/hyp3-insar-gamma/compare/v2.1.1...v2.1.2)

### Fixed
* HyP3v1 water mask (beta) option will again mask out water based on 
  [GSHHG f](http://www.soest.hawaii.edu/wessel/gshhg/) shapes, buffered 3000m 
  (seaward) from the coastline
* Upgraded to hyp3-lib v1.6.0 from v1.5.0

## [2.1.1](https://github.com/ASFHyP3/hyp3-insar-gamma/compare/v2.1.0...v2.1.1)

### Changed
* Replaced references to master/slave with reference/secondary, respectively, following recommendations from the InSAR community: https://comet.nerc.ac.uk/about-comet/insar-terminology/

## [2.1.0](https://github.com/ASFHyP3/hyp3-insar-gamma/compare/v2.0.0...v2.1.0)

### Added
* Added `hyp3_insar_gamma_v2` entrypoint for running insar gamma jobs in HyP3 v2
* Added `insar_gamma` as the new default entrypoint, which dispatches to `hyp3_insar_gamma_v2` or the legacy `hyp3_insar_gamma` (default) based on a `++entrypoint` parameter

### Changed
* Upgraded to [hyp3-lib v1.5.0](https://github.com/ASFHyP3/hyp3-lib/blob/develop/CHANGELOG.md#150) from v1.4.1.

## [2.0.0](https://github.com/ASFHyP3/hyp3-insar-gamma/compare/v1.2.1...v2.0.0)

This is a significant refactor of `hyp3-insar-gamma` into:
* A `pip` installable package called `hyp3_insar_gamma`
* A stand alone, container-based HyP3 plugin

**NOTE:** There are significant changes to the overall repository structure that
will break all existing HyP3 workflows!

### Removed
* Python 2. This package now requires python 3.6+
* `GC_map_mod` script has been removed in favor of the one packaged by `hyp3lib`
* Output GeoTIFFs no longer have overviews
* This drops the low-res browse images from the output product package
  * formerly `*.png` was low-res and `*_large.png` was high-res. Now, `*.png` is
    a high-res browse image and `*_large.png` files are no longer produced
* No longer supports the GIMP, REMA, and EU DEMs (due to them being dropped in `hyp3lib`)

### Added
 A packaging and testing structure -- now pip installable and testing is done via pytest
  * Previous command line scripts are now registered entrypoints and created when the 
    package is `pip` installed:
    * `procS1StackGAMMA.py`
    * `ifm_sentinel.py`
    * `interf_pwr_s1_lt_tops_proc.py`
    * `par_s1_slc.py`
    * `unwrapping_geocoding.py`
* A Dockerfile to build the HyP3 plugin
* A CI/CD workflow setup, which will build and publish the docker container
* The processing script that used to live in the now depreciated `cloud-proj` repository 
  has been moved into the package as `hyp3_insar_gamma.__main__` and also registered 
  as a `hyp3_insar_gamma` entrypoint
* A `conda-env.yml` to create conda environments for testing

### Changed
* The underlying GAMMA version has been upgraded to `20191203`
* All of `src/` is now contained in the `hyp3_insar_gamma` package
* All of `etc/` is now contained in `hyp3_insar_gamma.etc`
* The version number is now tracked automatically via git tags instead of in `etc/version.txt`

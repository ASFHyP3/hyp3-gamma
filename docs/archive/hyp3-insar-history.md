# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/) 
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/) 
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.0.0](https://github.com/asfadmin/hyp3-rtc-gamma/compare/v1.3.1...v2.0.0)

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



# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/) 
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.1](https://github.com/asfadmin/hyp3-geocode/compare/v1.0.0...v1.0.1)

This fixes a bug in the sigma-0 to gamma-0 conversion

## [v1.0.0](https://github.com/asfadmin/hyp3-geocode/compare/v0.0.0...v1.0.0)

This is a significant refactor of `hyp3-geocode` into:
 * A `pip` installable package called `hyp3_geocode`
 * A stand alone, container-based HyP3 plugin
 
**NOTE:** There are significant changes to the overall repository structure and this will break all 
existing HyP3 workflows!

### Removed
* Python 2. This package now requires Python 3.6+

### Added
* A packaging and testing structure -- now `pip` installable and testing is done via `pytest` and `tox` 
* A `Dockerfile` to build the HyP3 plugin
* A CI/CD workflow setup for ASF's hosted GitLab, which will build and publish the docker container
* The processing script that used to live in the now depreciated `cloud-proj` repository has been moved into the
 package as `hyp3_geocode.__main__` and also registered as a `hyp3_geocode` entrypoint

### Changed
* All of `src/` is now contained in the `hyp3_geocode` package
* All of `config/` is now contained in the `hyp3_geocode.etc` subpackage
* The `geocode_sentinel.py` "script" in has been moved to the `hyp3_geocode.sentinel` module and turned into an
 entrypoint with the name `geocode_sentinel.py` and should mostly function identically if `hpy3_geocode` is installed.


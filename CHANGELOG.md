# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0](https://github.com/ASFHyP3/hyp3-gamma/compare/v2.3.2...v3.0.0)

This is a MAJOR restucturing of HyP3's GAMMA based processes. Starting with hyp3-rtc-gamma,
hyp3-rtc-gamma [v2.3.2](https://github.com/ASFHyP3/hyp3-rtc-gamma/releases/tag/v2.3.2),
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

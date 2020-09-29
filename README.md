# HyP3 GAMMA

HyP3 plugin for processing SAR data with GAMMA

## Developer Setup

Ubuntu 18.0.4 is recommended for GAMMA support.

1. Install GAMMA
1. Install [conda](https://docs.conda.io/en/latest/miniconda.html)
1. Install hyp3-gamma
   ```
   git clone git@github.com:ASFHyP3/hyp3-gamma.git
   cd hyp3-gamma
   conda env create -f conda-env.yml
   conda activate hyp3-gamma
   pip install -e .[develop]
   ```
1. Run It!


### Run RTC
   ```
   rtc_sentinel.py --help
   rtc_sentinel.py S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8.zip
   ```

### Run Geocode


### Run InSAR


### Run Threshold Change Detection


### Prototype

#### docker
#### jupyter
#### pycharm setup

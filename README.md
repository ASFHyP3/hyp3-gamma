# HyP3 RTC GAMMA

HyP3 plugin for radiometric terrain correction using GAMMA

## Developer Setup

Ubuntu 18.0.4 is recommended for ASF MapReady support.

1. Install [ASF MapReady](https://github.com/asfadmin/ASF_MapReady)
1. Install GAMMA
1. Install [conda](https://docs.conda.io/en/latest/miniconda.html)
1. Install hyp3-rtc-gamma
   ```
   git clone git@github.com:ASFHyP3/hyp3-rtc-gamma.git
   cd hyp3-rtc-gamma
   conda env create -f conda-env.yml
   conda activate hyp3-rtc-gamma
   pip install -e .
   ```
1. Run It!
   ```
   rtc_sentinel.py --help
   rtc_sentinel.py S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8.zip
   ```

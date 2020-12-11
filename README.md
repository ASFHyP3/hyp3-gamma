# HyP3 GAMMA

HyP3 plugin for SAR processing with GAMMA

## Developer Setup

Ubuntu 18.0.4 is recommended for GAMMA support.

1. Install GAMMA
1. Install [conda](https://docs.conda.io/en/latest/miniconda.html)
1. Install `hyp3_gamma`
   ```
   git clone git@github.com:ASFHyP3/hyp3-gamma.git
   cd hyp3-gamma
   conda env create -f conda-env.yml
   conda activate hyp3-gamma
   pip install -e .[develop]
   ```
1. Check hyp3_gamma is installed
   ```
   hyp3_gamma --help
   ```

### Radiometric Terrain Correction (RTC)

To run the RTC science process:
```
rtc_sentinel.py --help
rtc_sentinel.py S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8.zip
```

To run the RTC process through the HyP3 interface:
```
hyp3_gamma ++process rtc --help
hyp3_gamma ++process rtc --username ${EDL_USERNAME} --password ${EDL_PASSWORD} \
    S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8
```

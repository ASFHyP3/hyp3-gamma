# HyP3 GAMMA

HyP3 plugin for SAR processing with GAMMA

## Developer Setup

Ubuntu 20.04 is recommended for GAMMA support.

1. Install GAMMA
1. Install [conda](https://docs.conda.io/en/latest/miniconda.html)
1. Install `hyp3_gamma`
   ```
   git clone git@github.com:ASFHyP3/hyp3-gamma.git
   cd hyp3-gamma
   conda env create -f environment.yml
   conda activate hyp3-gamma
   ```
1. Check hyp3_gamma is installed
   ```
   hyp3_gamma --help
   ```

### Radiometric Terrain Correction (RTC)

SAR datasets inherently contain geometric and radiometric distortions due to terrain
being imaged by a side-looking instrument. Radiometric terrain correction (RTC)
removes these distortions and creates analysis-ready data suitable for use in GIS
applications. RTC processing is a required first step for many amplitude-based SAR
applications.

To run the RTC science process:
```
rtc_sentinel.py --help
rtc_sentinel.py S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8.SAFE
```

To run the RTC process through the HyP3 interface:
```
hyp3_gamma ++process rtc --help
hyp3_gamma ++process rtc --username ${EDL_USERNAME} --password ${EDL_PASSWORD} \
    S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8
```

### Interferometric Synthetic Aperture Radar (InSAR)

Interferometric SAR (InSAR) uses the phase differences from repeat passes over the
same area to identify regions where the distance between the sensor and the Earth's
surface has changed. This allows for the detection and quantification of deformation
or movement.

To run the InSAR science process:
```
ifm_sentinel.py --help
ifm_sentinel.py \
    S1A_IW_SLC__1SDV_20200203T172103_20200203T172122_031091_03929B_3048.SAFE \
    S1A_IW_SLC__1SDV_20200110T172104_20200110T172123_030741_03864E_A996.SAFE
```

To run the InSAR process through the HyP3 interface:
```
hyp3_gamma ++process insar --help
hyp3_gamma ++process insar --username ${EDL_USERNAME} --password ${EDL_PASSWORD} \
    S1A_IW_SLC__1SDV_20200203T172103_20200203T172122_031091_03929B_3048 \
    S1A_IW_SLC__1SDV_20200110T172104_20200110T172123_030741_03864E_A996
```

### Example product metadata

The `hyp3_gamma.metadata` subpackage can generate an example set of product metadata
for each of the supported product types. E.g.:

```
python -m hyp3_gamma.metadata rtc
python -m hyp3_gamma.metadata insar
```

For detailed usage, see [the metadata README](hyp3_gamma/metadata/README.md).

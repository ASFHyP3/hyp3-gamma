# HyP3 GAMMA

HyP3 plugin for processing SAR data with GAMMA

## Developer Setup

Ubuntu 18.0.4 is recommended for GAMMA support.

1. Install GAMMA
1. Install [conda](https://docs.conda.io/en/latest/miniconda.html)
1. Install hyp3-gamma
   ```shell script
   git clone git@github.com:ASFHyP3/hyp3-gamma.git
   cd hyp3-gamma
   conda env create -f conda-env.yml
   conda activate hyp3-gamma
   pip install -e ".[develop]"
   ```
1. Run It!


### Run RTC
```
hyp3_gamma rtc --help
hyp3_gamma rtc --username [EDL_USERNAME] --password [EDL_PASSWORD] \
    S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8
```

Or, for just the science process
```
rtc_sentinel.py --help
rtc_sentinel.py S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8.SAFE
```

### Run InSAR
```
hyp3_gamma insar --help
hyp3_gamma insar --username [EDL_USERNAME] --password [EDL_PASSWORD] \
    S1A_IW_SLC__1SDV_20200203T172103_20200203T172122_031091_03929B_3048 \
    S1A_IW_SLC__1SDV_20200110T172104_20200110T172123_030741_03864E_A996
```

Or, for just the science process
```
ifm_sentinel.py --help
ifm_sentinel.py S1A_IW_SLC__1SDV_20200203T172103_20200203T172122_031091_03929B_3048.SAFE \
    S1A_IW_SLC__1SDV_20200110T172104_20200110T172123_030741_03864E_A996.SAFE
```



### Run Geocode
HyP3v2 entrypoint has not been implemented. To run just the science process
```
geocode_sentinel.py --help
geocode_sentinel.py S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8.SAFE [OUT_FILE]
```


## Prototype

A Jupter (lab or notebook) prototyping environment is provided with this plugin's `Dockerfile`.
To build a docker image with the prototyping environment, you will first need to make sure the
current version of the `hyp3_gamma` python package is available. From the repository root, run:
```
export S3_PYPI_HOST=hyp3-pypi.s3-website-us-east-1.amazonaws.com
export SDIST_VERSION=$(python3 setup.py --version) && echo ${SDIST_VERSION}
python3 setup.py sdist bdist_wheel
s3pypi --bucket hyp3-pypi --verbose
```

Then you can build the docker image:
```
docker build --target prototype \
    --build-arg S3_PYPI_HOST=${S3_PYPI_HOST} \
    --build-arg SDIST_SPEC="==${SDIST_VERSION}" \
    -t [PROTOTYPE_BUILD_TAG] .
```
where `[PROTOTYPE_BUILD_TAG]` is what you'd like to tag this image.

To run the JupyterLab in the prototyping environment, run:
```
docker run --rm \
  -v ${PWD}:/home/conda/hyp3-gamma \
  -p 8888:8888 \
  -it [PROTOTYPE_BUILD_TAG]
```
You can connect to the Jupyter Lab server at the `http://127.0.0.1:8888...` link printed to 
stdout in your terminal.  

**Note:** the `hyp3_gamma` package **will not** be installed initially in the prototyping
so that we can mount it into the container and install it in editable/develop mode
(you're changes locally will be automatically reflected in the container). A `setup-dev.ipynb`
notebook is provided at `hyp3-gamma/prototype` inside the container, which when run will 
install `hyp3_gamma` into the prototyping environment in editable/develop mode. 
(This only needs to be run once per `docker run`.)

Prototyping notebooks and associated should be saved in the `hyp3-gamma/prototype` directory inside
the container and they will be available there outside the container as well.


### Jupyter options

If you'd prefer to specify custom startup options to Jupyter, or prefer to use the 
Jupyter Notebook server instead of Jupyter Lab, you can specify them as part of the
docker run command like:

```
docker run --rm \
  -v ${PWD}:/home/conda/hyp3-gamma \
  -p 8888:8888 \
  -it [PROTOTYPE_BUILD_TAG] {lab,notebook} [JUPYTER_OPTIONS]
``` 

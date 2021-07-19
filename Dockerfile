FROM ubuntu:18.04

# For opencontainers label definitions, see:
#    https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.title="HyP3 GAMMA"
LABEL org.opencontainers.image.description="HyP3 plugin for SAR processing with GAMMA"
LABEL org.opencontainers.image.vendor="Alaska Satellite Facility"
LABEL org.opencontainers.image.authors="ASF APD/Tools Team <uaf-asf-apd@alaska.edu>"
LABEL org.opencontainers.image.licenses="BSD-3-Clause"
LABEL org.opencontainers.image.url="https://github.com/ASFHyP3/hyp3-gamma"
LABEL org.opencontainers.image.source="https://github.com/ASFHyP3/hyp3-gamma"
LABEL org.opencontainers.image.documentation="https://hyp3-docs.asf.alaska.edu"

# Dynamic lables to define at build time via `docker build --label`
# LABEL org.opencontainers.image.created=""
# LABEL org.opencontainers.image.version=""
# LABEL org.opencontainers.image.revision=""

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=true

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential curl gcc gdal-bin \
    gimp gnuplot gnuplot-data gnuplot-qt libblas-dev libblas3 \
    libfftw3-dev libgdal-dev libgdal20 \
    libgtk2.0-bin libgtk2.0-common libgtk2.0-dev \
    libhdf5-100 libhdf5-dev liblapack-dev liblapack3 \
    python3-dev python3-h5py python3-netcdf4 \
    python3-matplotlib python3-pip python3-scipy tcsh unzip vim wget git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir --upgrade pip setuptools wheel

COPY GAMMA_SOFTWARE-20191203 /usr/local/GAMMA_SOFTWARE-20191203/

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal && \
    export C_INCLUDE_PATH=/usr/include/gdal && \
    python3 -m pip install --no-cache-dir GDAL==2.2.3 statsmodels==0.9 pandas==0.23 geopandas==0.9.0 affine=2.3.0

COPY . /hyp3-gamma/
RUN  python3 -m pip install --no-cache-dir /hyp3-gamma \
    && rm -rf /hyp3-gamma

ARG CONDA_GID=1000
ARG CONDA_UID=1000

RUN groupadd -g "${CONDA_GID}" --system conda && \
    useradd -l -u "${CONDA_UID}" -g "${CONDA_GID}" --system -d /home/conda -m  -s /bin/bash conda

USER ${CONDA_UID}
SHELL ["/bin/bash", "-l", "-c"]
ENV PYTHONDONTWRITEBYTECODE=true
ENV GAMMA_HOME=/usr/local/GAMMA_SOFTWARE-20191203
ENV MSP_HOME=$GAMMA_HOME/MSP
ENV ISP_HOME=$GAMMA_HOME/ISP
ENV DIFF_HOME=$GAMMA_HOME/DIFF
ENV DISP_HOME=$GAMMA_HOME/DISP
ENV LAT_HOME=$GAMMA_HOME/LAT
ENV PATH=$PATH:$MSP_HOME/bin:$ISP_HOME/bin:$DIFF_HOME/bin:$LAT_HOME/bin:$DISP_HOME/bin
ENV PATH=$PATH:$MSP_HOME/scripts:$ISP_HOME/scripts:$DIFF_HOME/scripts:$LAT_HOME/scripts
ENV GAMMA_RASTER=BMP

WORKDIR /home/conda/

## ASF TOOLS
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
    && bash Mambaforge-Linux-x86_64.sh -b \
    && rm -f Mambaforge-Linux-x86_64.sh \
    && echo PATH="/home/conda/mambaforge/bin":$PATH >> .profile \
    && echo ". /home/conda/mambaforge/etc/profile.d/conda.sh" >> .profile

ENV PATH=$PATH:/home/conda/mambaforge/bin

RUN conda --version \
    && conda config --set auto_activate_base false

# FIXME: dev branch and cached stale clone
RUN git clone https://github.com/ASFHyP3/asf-tools.git \
    && mamba env create -f asf-tools/environment.yml \
    && mamba clean -afy

RUN conda run -n asf-tools python -m pip install --no-cache-dir ./asf-tools \
    && rm -rf ./asf-tools

ENTRYPOINT ["/usr/local/bin/hyp3_gamma"]
CMD ["-h"]

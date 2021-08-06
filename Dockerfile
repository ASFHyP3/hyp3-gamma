FROM ubuntu:20.04

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

RUN apt update && apt upgrade -y

# 2. Install the FFTW3 libraries
RUN apt install -y libfftw3-3 libfftw3-dev libfftw3-single3
# 3. Install Gnuplot and GIMP programs
RUN apt install -y gnuplot gnuplot-data gimp
# 4. Install the GDAL library
RUN apt install -y gdal-bin libgdal-dev
# 5. Install the HDF5 library (required for COSMO/SKYMED and ICEYE data)
RUN apt install -y libhdf5-dev libhdf5-103
# 6. Install LAPACK and BLAS libraries (for Gamma Software LAT package only)
RUN apt install -y libblas-dev libblas3 liblapack-dev liblapack3 liblapack-doc
# 9. Installation of Python 3
RUN apt install -y python3-numpy python3-matplotlib python3-scipy python3-shapely

RUN apt install -y python3-pip wget git

COPY GAMMA_SOFTWARE-20210701 /usr/local/GAMMA_SOFTWARE-20210701/

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
ENV GAMMA_HOME=/usr/local/GAMMA_SOFTWARE-20210701
ENV MSP_HOME=$GAMMA_HOME/MSP
ENV ISP_HOME=$GAMMA_HOME/ISP
ENV DIFF_HOME=$GAMMA_HOME/DIFF
ENV DISP_HOME=$GAMMA_HOME/DISP
ENV LAT_HOME=$GAMMA_HOME/LAT
ENV PATH=$PATH:$MSP_HOME/bin:$ISP_HOME/bin:$DIFF_HOME/bin:$LAT_HOME/bin:$DISP_HOME/bin
ENV PATH=$PATH:$MSP_HOME/scripts:$ISP_HOME/scripts:$DIFF_HOME/scripts:$LAT_HOME/scripts:$DISP_HOME/scripts
ENV OS=linux64
ENV GAMMA_RASTER=BMP
ENV HDF5_DISABLE_VERSION_CHECK=1

WORKDIR /home/conda/

## ASF TOOLS
RUN wget --progress=dot:mega https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
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

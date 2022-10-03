## ASF TOOLS
ARG ASF_TOOLS_IMAGE='ghcr.io/asfhyp3/asf-tools'
ARG ASF_TOOLS_TAG=0.4.2

FROM ${ASF_TOOLS_IMAGE}:${ASF_TOOLS_TAG} as asf-tools

FROM ubuntu:22.04

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

RUN apt update \
    && apt upgrade -y \
    && apt install -y --no-install-recommends \
         # GAMMA requirements per sections 2-6, 9 of the Linux installation guide
         libfftw3-3 libfftw3-dev libfftw3-single3 \
         gnuplot gnuplot-data gimp \
         gdal-bin libgdal-dev \
         libhdf5-dev libhdf5-103 \
         libblas-dev libblas3 liblapack-dev liblapack3 liblapack-doc \
         python-is-python3 python3-numpy python3-matplotlib python3-scipy python3-shapely python3-packaging \
         # GAMMA scripts require csh/tcsh
         tcsh \
         # Additional installs
         python3-pip wget git vim \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

COPY GAMMA_SOFTWARE-20220630 /usr/local/GAMMA_SOFTWARE-20220630/

COPY . /hyp3-gamma/
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir /hyp3-gamma \
    && rm -rf /hyp3-gamma

ARG CONDA_GID=1000
ARG CONDA_UID=1000

RUN groupadd -g "${CONDA_GID}" --system conda \
    && useradd -l -u "${CONDA_UID}" -g "${CONDA_GID}" --system -d /home/conda -m -s /bin/bash conda

USER ${CONDA_UID}
SHELL ["/bin/bash", "-l", "-c"]
ENV PYTHONDONTWRITEBYTECODE=true

# GAMMA environment variables per section 1 of the Linux installation guide
ENV GAMMA_VERSION=20220630
ENV GAMMA_HOME=/usr/local/GAMMA_SOFTWARE-${GAMMA_VERSION}
ENV MSP_HOME=$GAMMA_HOME/MSP
ENV ISP_HOME=$GAMMA_HOME/ISP
ENV DIFF_HOME=$GAMMA_HOME/DIFF
ENV DISP_HOME=$GAMMA_HOME/DISP
ENV LAT_HOME=$GAMMA_HOME/LAT
ENV PATH=$PATH:$MSP_HOME/bin:$ISP_HOME/bin:$DIFF_HOME/bin:$LAT_HOME/bin:$DISP_HOME/bin
ENV PATH=$PATH:$MSP_HOME/scripts:$ISP_HOME/scripts:$DIFF_HOME/scripts:$LAT_HOME/scripts:$DISP_HOME/scripts
ENV OS=linux64
ENV PYTHONPATH=$GAMMA_HOME:$PYTHONPATH
ENV HDF5_DISABLE_VERSION_CHECK=1

WORKDIR /home/conda/

COPY --from=asf-tools --chown=${CONDA_GID}:${CONDA_UID} /opt/conda /opt/conda
COPY --from=asf-tools --chown=${CONDA_GID}:${CONDA_UID} /home/conda/.profile /home/conda/

ENV PATH=$PATH:/opt/conda/bin

ENTRYPOINT ["/usr/local/bin/hyp3_gamma"]
CMD ["-h"]

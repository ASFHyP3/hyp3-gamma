FROM ubuntu:18.04 AS production

# For opencontainers label definitions, see:
#    https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.title="HyP3 GAMMA"
LABEL org.opencontainers.image.description="HyP3 plugin for processing SAR data with GAMMA"
LABEL org.opencontainers.image.vendor="Alaska Satellite Facility"
LABEL org.opencontainers.image.authors="ASF APD/Tools Team <uaf-asf-apd@alaska.edu>"
LABEL org.opencontainers.image.licenses="BSD-3-Clause"
LABEL org.opencontainers.image.url="https://github.com/ASFHyP3/hyp3-gamma"
LABEL org.opencontainers.image.source="https://github.com/ASFHyP3/hyp3-gamma"
# LABEL org.opencontainers.image.documentation=""

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
    python3-matplotlib python3-pip python3-scipy tcsh unzip vim wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir --upgrade pip setuptools wheel

COPY GAMMA_SOFTWARE-20191203 /usr/local/GAMMA_SOFTWARE-20191203/

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal && \
    export C_INCLUDE_PATH=/usr/include/gdal && \
    python3 -m pip install --no-cache-dir GDAL==2.2.3 statsmodels==0.9 pandas==0.23

ARG S3_PYPI_HOST
ARG SDIST_SPEC

RUN python3 -m pip install --no-cache-dir hyp3_gamma${SDIST_SPEC} \
    --trusted-host "${S3_PYPI_HOST}" \
    --extra-index-url "http://${S3_PYPI_HOST}"

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

ENTRYPOINT ["/usr/local/bin/hyp3_gamma"]
CMD ["-h"]

FROM production AS prototype

ARG DEBIAN_FRONTEND=noninteractive

USER 0

RUN apt-get update && apt-get install -y --no-install-recommends \
    bzip2 ca-certificates fonts-liberation git locales libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc

ENV LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -f -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    . /opt/conda/etc/profile.d/conda.sh && \
    conda config --system --prepend channels conda-forge && \
    conda config --system --set auto_update_conda false && \
    conda config --system --set show_channel_urls true && \
    conda config --system --set channel_priority strict && \
    conda update --all --quiet --yes && \
    chown -R conda:conda /opt && \
    conda clean -afy && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> /home/conda/.profile && \
    echo "conda activate base" >> /home/conda/.profile

COPY --chown=conda:conda /etc/start-jupyter.sh /usr/local/bin/
COPY --chown=conda:conda /etc/jupyter_notebook_config.py /etc/jupyter/

ARG CONDA_GID=1000
ARG CONDA_UID=1000

USER ${CONDA_UID}

COPY conda-env.yml /home/conda/conda-env.yml

RUN conda env create -f conda-env.yml && \
    rm conda-env.yml && \
    conda clean -afy && \
    conda activate hyp3-gamma && \
    sed -i 's/conda activate base/conda activate hyp3-gamma/g' /home/conda/.profile

RUN conda install --quiet --yes \
    jupyterlab notebook nodejs tini && \
    conda clean --all -f -y && \
    npm cache clean --force && \
    jupyter notebook --generate-config && \
    rm -rf /opt/conda/share/jupyter/lab/staging && \
    rm -rf /home/conda/.cache/yarn

EXPOSE 8888

ENTRYPOINT ["/usr/local/bin/start-jupyter.sh"]
CMD ["lab"]
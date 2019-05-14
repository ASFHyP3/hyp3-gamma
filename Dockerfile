FROM ubuntu:16.04

ARG GAMMA=gamma_20170707.tar.gz

COPY ${GAMMA} /
RUN mkdir -p /usr/local/gamma
RUN tar --strip-components=1 -zxvf ${GAMMA} -C /usr/local/gamma
RUN rm /${GAMMA}

ENV GAMMA_HOME=/usr/local/gamma
ENV MSP_HOME=${GAMMA_HOME}/MSP \
    ISP_HOME=${GAMMA_HOME}/ISP \
    DIFF_HOME=${GAMMA_HOME}/DIFF \
    DISP_HOME=${GAMMA_HOME}/DISP \
    LAT_HOME=${GAMMA_HOME}/LAT \
    IPTA_HOME=${GAMMA_HOME}/IPTA \
    GEO_HOME=${GAMMA_HOME}/GEO \
    GDFONTPATH=/usr/share/fonts/truetype/msttcorefonts \
    GAMMA_RASTER=BMP

ENV PATH=${PATH}:${DISP_HOME}/bin:${MSP_HOME}/bin:${ISP_HOME}/bin:${DIFF_HOME}/bin:${LAT_HOME}/bin:${IPTA_HOME}/bin:${GEO_HOME}/bin
ENV PATH=${PATH}:${MSP_HOME}/scripts:${ISP_HOME}/scripts/:${DIFF_HOME}/scripts:${LAT_HOME}/scripts:${IPTA_HOME}/scripts
ENV PATH=${PATH}:/usr/lib

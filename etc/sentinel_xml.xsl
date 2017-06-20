<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:gml="http://www.opengis.net/gml"
  xmlns:xfdu="urn:ccsds:schema:xfdu:1"
  xmlns:safe="http://www.esa.int/safe/sentinel-1.0"
  xmlns:s1="http://www.esa.int/safe/sentinel-1.0/sentinel-1"
  xmlns:s1sar="http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar"
  xmlns:s1sarl1="http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-1"
  xmlns:s1sarl2="http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-2"
  xmlns:exsl="http://exslt.org/common" exclude-result-prefixes="xsl gml xfdu safe s1 s1sar s1sarl1 exsl">
  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  
  <!-- path, server, timestamp and package file size need to be parsed into via xsltproc string parameters -->
  
  <!-- granule name parsing -->
  <xsl:variable name="smallcase" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
  <xsl:variable name="directory" select="substring($path, string-length($path)-71)"/>
  <xsl:variable name="platform"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:familyName"/><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:number"/></xsl:variable>
  <xsl:variable name="granule"><xsl:copy-of select="substring($directory,1,67)"/></xsl:variable>
  <xsl:variable name="mission_id"><xsl:copy-of select="substring($directory,1,3)"/></xsl:variable>
  <xsl:variable name="beam_mode"><xsl:copy-of select="substring($directory,5,2)"/></xsl:variable>
  <xsl:variable name="product_type"><xsl:copy-of select="substring($directory,8,3)"/></xsl:variable>
  <xsl:variable name="resolution_class"><xsl:copy-of select="substring($directory,11,1)"/></xsl:variable>
  <xsl:variable name="processing_level"><xsl:copy-of select="substring($directory,13,1)"/></xsl:variable>
  <xsl:variable name="product_class"><xsl:copy-of select="substring($directory,14,1)"/></xsl:variable>
  <xsl:variable name="polarization"><xsl:copy-of select="substring($directory,15,2)"/></xsl:variable>
  <xsl:variable name="absolute_orbit"><xsl:copy-of select="substring($directory,50,6)"/></xsl:variable>
  <xsl:variable name="mission_datatake_id"><xsl:copy-of select="substring($directory,57,6)"/></xsl:variable>
  <xsl:variable name="product_id"><xsl:copy-of select="substring($directory,64,4)"/></xsl:variable>

  <!-- polarization flags -->
  <xsl:variable name="hh_pol">
    <xsl:if test="$polarization='SH'">1</xsl:if>
    <xsl:if test="$polarization='DH'">1</xsl:if>
    <xsl:if test="$polarization='HH'">1</xsl:if>
  </xsl:variable>
  <xsl:variable name="hv_pol">
    <xsl:if test="$polarization='DH'">1</xsl:if>
    <xsl:if test="$polarization='HV'">1</xsl:if>
  </xsl:variable>
  <xsl:variable name="vh_pol">
    <xsl:if test="$polarization='DV'">1</xsl:if>
    <xsl:if test="$polarization='VH'">1</xsl:if>
  </xsl:variable>
  <xsl:variable name="vv_pol">
    <xsl:if test="$polarization='SV'">1</xsl:if>
    <xsl:if test="$polarization='DV'">1</xsl:if>
    <xsl:if test="$polarization='VV'">1</xsl:if>
  </xsl:variable>
  <xsl:variable name="swath_count"><xsl:value-of select="count(/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:extension/s1sarl1:instrumentMode/s1sarl1:swath)"/></xsl:variable>

  <!-- timestamps -->
  <xsl:variable name="ascending_node_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/safe:orbitReference/safe:extension/s1:orbitProperties/s1:ascendingNodeTime"/></xsl:variable>
  <xsl:variable name="ascending_node_utc_time"><xsl:copy-of select="$ascending_node_time"/><xsl:if test="not(contains($ascending_node_time,'Z'))">Z</xsl:if></xsl:variable>
  <xsl:variable name="processing_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing/@stop"/></xsl:variable>
  <xsl:variable name="processing_utc_time"><xsl:copy-of select="$processing_time"/><xsl:if test="not(contains($processing_time,'Z'))">Z</xsl:if></xsl:variable>
  <xsl:variable name="start_acquisition_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/safe:acquisitionPeriod/safe:startTime"/></xsl:variable>
  <xsl:variable name="start_acquisition_utc_time"><xsl:copy-of select="$start_acquisition_time"/><xsl:if test="not(contains($start_acquisition_time,'Z'))">Z</xsl:if></xsl:variable>
  <xsl:variable name="end_acquisition_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/safe:acquisitionPeriod/safe:stopTime"/></xsl:variable>
  <xsl:variable name="end_acquistion_utc_time"><xsl:copy-of select="$end_acquisition_time"/><xsl:if test="not(contains($end_acquisition_time,'Z'))">Z</xsl:if></xsl:variable>
  <xsl:variable name="year"><xsl:copy-of select="substring($end_acquisition_time,1,4)"/></xsl:variable>  

  <!-- data source -->
  <xsl:variable name="data_source_path">
    <xsl:if test="$processing_level=0"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing/safe:resource/safe:processing/safe:resource[@role='Level-0 Product']/@name"/></xsl:if>
    <xsl:if test="$processing_level=1"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing/safe:resource/safe:processing/safe:resource[@role='Level-0 Product']/@name"/></xsl:if>
    <xsl:if test="$processing_level=2"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing/safe:resource[contains(@role,'Level-1 Intermediate')]/@name"/></xsl:if>
  </xsl:variable>
  <xsl:variable name="data_source">
    <xsl:if test="contains($data_source_path,'//')"><xsl:value-of select="substring-after($data_source_path,'//')"/></xsl:if>
    <xsl:if test="not(contains($data_source_path,'//'))"><xsl:copy-of select="$data_source_path"/></xsl:if>
  </xsl:variable>
  
  <xsl:variable name="format">
    <xsl:if test="$processing_level=0">binary DAT file</xsl:if>
    <xsl:if test="$processing_level=1">GeoTIFF</xsl:if>
    <xsl:if test="$processing_level=2">netCDF</xsl:if>
  </xsl:variable>
  <xsl:variable name="start_time_anx"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/safe:acquisitionPeriod/safe:extension/s1:timeANX/s1:startTimeANX"/></xsl:variable>
  <xsl:variable name="stop_time_anx"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/safe:acquisitionPeriod/safe:extension/s1:timeANX/s1:stopTimeANX"/></xsl:variable>
  
  <xsl:template match="/">
    <!-- start of the actual output XML file -->
    <sentinel>
      <directory><xsl:copy-of select="$directory"/></directory>
      <product><xsl:copy-of select="$granule"/></product>
      <granule><xsl:copy-of select="$granule"/></granule>
      <metadata_creation><xsl:copy-of select="$timestamp"/>Z</metadata_creation>
      <data>
        <!-- level 0 data -->
        <xsl:if test="$processing_level=0">
          <xsl:if test="$polarization='DH'">
            <xsl:element name="{concat($beam_mode,'_HH')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData1']/byteStream/fileLocation/@href"/></xsl:element>
            <xsl:element name="{concat($beam_mode,'_HV')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData2']/byteStream/fileLocation/@href"/></xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='DV'">
            <xsl:element name="{concat($beam_mode,'_VH')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData1']/byteStream/fileLocation/@href"/></xsl:element>
            <xsl:element name="{concat($beam_mode,'_VV')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData2']/byteStream/fileLocation/@href"/></xsl:element>
          </xsl:if>
          <xsl:if test="($polarization='SH') or ($polarization='HH')">
            <xsl:element name="{concat($beam_mode,'_HH')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData']/byteStream/fileLocation/@href"/></xsl:element>
          </xsl:if>
          <xsl:if test="($polarization='SV') or ($polarization='VV')">
            <xsl:element name="{concat($beam_mode,'_VV')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData']/byteStream/fileLocation/@href"/></xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='HV'">
            <xsl:element name="{concat($beam_mode,'_HV')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData']/byteStream/fileLocation/@href"/></xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='VH'">
            <xsl:element name="{concat($beam_mode,'_VH')}"><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='measurementData']/byteStream/fileLocation/@href"/></xsl:element>
          </xsl:if>
        </xsl:if>

        <!-- level 1 data -->
        <xsl:if test="$processing_level=1">
          <xsl:for-each
            select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:extension/s1sarl1:instrumentMode/s1sarl1:swath">
            <xsl:variable name="swath" select="."/>
            <xsl:if test="$polarization='DH'">
              <xsl:element name="{concat($swath,'_HH')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
              <xsl:element name="{concat($swath,'_HV')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
            </xsl:if>
            <xsl:if test="$polarization='DV'">
              <xsl:element name="{concat($swath,'_VH')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
              <xsl:element name="{concat($swath,'_VV')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
            </xsl:if>
            <xsl:if test="($polarization='SH') or ($polarization='HH')">
              <xsl:element name="{concat($swath,'_HH')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
            </xsl:if>
            <xsl:if test="($polarization='SV') or ($polarization='VV')">
              <xsl:element name="{concat($swath,'_VV')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
            </xsl:if>
            <xsl:if test="$polarization='HV'">
              <xsl:element name="{concat($swath,'_HV')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
            </xsl:if>
            <xsl:if test="$polarization='VH'">
              <xsl:element name="{concat($swath,'_VH')}">
                <xsl:variable name="data">
                  <xsl:if test="$swath_count>1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="position()"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
                  <xsl:if test="$swath_count=1"><xsl:value-of
                      select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of
                      select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
                </xsl:variable>
                <xsl:value-of
                  select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data)]/byteStream/fileLocation/@href"
                />
              </xsl:element>
            </xsl:if>
          </xsl:for-each>          
        </xsl:if>
        
        <!-- level 2 data -->
        <xsl:if test="$processing_level=2">
          <xsl:for-each select="/xfdu:XFDU/dataObjectSection/dataObject[@repID='s1Level1MeasurementSchema']/byteStream/fileLocation">
            <xsl:variable name="data_id"><xsl:value-of select="position()"/></xsl:variable>
            <xsl:for-each select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:extension/s1sarl2:instrumentMode/s1sarl2:swath">
              <xsl:variable name="swath" select="."/>
              <xsl:variable name="data">
                <xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/>
                <xsl:value-of select="translate($swath,$uppercase,$smallcase)"/>
                <xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>
              </xsl:variable>
              <xsl:variable name="number">
                <xsl:value-of select="translate($mission_datatake_id,$uppercase,$smallcase)"/>
                <xsl:value-of select="format-number($data_id, '000')"/>
              </xsl:variable>
              <xsl:variable name="dataset">
                <xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$data) and contains(@ID,$number)]/byteStream/fileLocation/@href"/>                
              </xsl:variable>
              <xsl:if test="string-length($dataset) > 0">
                <xsl:element name="{$swath}"><xsl:attribute name="data_id"><xsl:value-of select="$data_id"/></xsl:attribute><xsl:value-of select="$dataset"/></xsl:element>
              </xsl:if>
            </xsl:for-each>
          </xsl:for-each>
        </xsl:if>
      </data>
      
      <!-- metadata section -->
      <metadata>
        <image>
          <file type="string" definition="file name of the image"><xsl:copy-of select="$granule"/>.iso.xml</file>
          <platform type="string" definition="name of the platform (SENTINEL-1A or SENTINEL-1B)" label="Platform"><xsl:copy-of select="$platform"/></platform>
          <sensor type="string" definition="name of the sensor"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:familyName"/></sensor>
          <polarization type="string" definition="single, dual or partial dual polarization of HH, HV, VH, VV" label="Polarization"><xsl:copy-of select="$polarization"/></polarization>
          <product_class type="string" definition="S (SAR standard), A (Annotation product)"><xsl:copy-of select="$product_class"/></product_class>
          <processing_level type="int" definition="level of processing (0, 1, or 2)" label="Processing level"><xsl:copy-of select="$processing_level"/></processing_level>
          <product_class_description type="string" definition="textual description of product class">
            <xsl:if test="$processing_level=0"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:productClassDescription"/></xsl:if>
            <xsl:if test="$processing_level=1"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sarl1:standAloneProductInformation/s1sarl1:productClassDescription"/></xsl:if>
            <xsl:if test="$processing_level=2"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sarl2:standAloneProductInformation/s1sarl2:productClassDescription"/></xsl:if>
          </product_class_description>
          <xsl:if test="$processing_level=1">
          <product_composition type="string" definition="product composition (Individual, Slice or Assembled)"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sarl1:standAloneProductInformation/s1sarl1:productComposition"/></product_composition>
          <product_timeliness_category type="string" definition="required timeliness of the processing"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sarl1:standAloneProductInformation/s1sarl1:productTimelinessCategory"/></product_timeliness_category>
        </xsl:if>
        <xsl:if test="$processing_level=0">
          <product_consolidation type="string" definition="product consolidation status (SLICE, PARTIAL, FULL)"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:productConsolidation"/></product_consolidation>
        </xsl:if>
          <product_type type="string" definition="product type (RAW, SLC, GRD, OCN)" label="Product type"><xsl:copy-of select="$product_type"/></product_type>
          <beam_mode type="string" definition="beam mode of the sensor" label="Product type"><xsl:copy-of select="$beam_mode"/></beam_mode>
          <cycle type="int" definition="mission cycle the orbit is in" label="Cycle"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/safe:orbitReference/safe:cycleNumber"/></cycle>
          <absolute_orbit type="int" definition="absolute orbit of the image" label="Absolute orbit"><xsl:copy-of select="number($absolute_orbit)"/></absolute_orbit>
          <relative_orbit type="int" definition="relative orbit of the image" label="Relative orbit"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/safe:orbitReference/safe:relativeOrbitNumber"/></relative_orbit>
          <mission_datatake_id type="string" definition="mission datatake identifier"><xsl:copy-of select="$mission_datatake_id"/></mission_datatake_id>
          <product_unique_id type="string" definition="hexadecimal string generated by computing CRC-16 on the manifest file"><xsl:copy-of select="$product_id"/></product_unique_id>
          <flight_direction type="string" definition="flight direction of the sensor" label="Flight direction"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/safe:orbitReference/safe:extension/s1:orbitProperties/s1:pass"/></flight_direction>
          <data_format type="string" definition="data format of image data" label="Data format"><xsl:copy-of select="$format"/></data_format>
          
          <xsl:if test="$processing_level=1">
            <!-- Assign width, height, x spacing and y spacing for all available swaths -->
            <xsl:for-each select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:extension/s1sarl1:instrumentMode/s1sarl1:swath">
              <xsl:variable name="swath" select="."/>
              <xsl:if test="($polarization='DV') or ($polarization='SV') or ($polarization='VV')">
                <xsl:if test="$swath_count>1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:variable>
                  <xsl:element name="{concat($swath,'_',$polarization)}">
                    <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                    <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                    <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                    <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                    <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                  </xsl:element>
                </xsl:if>
                <xsl:if test="$swath_count=1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:variable>
                  <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                  <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                  <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                  <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                  <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                </xsl:if>
              </xsl:if>
              <xsl:if test="($polarization='DH') or ($polarization='SH') or ($polarization='HH')">
                <xsl:if test="$swath_count>1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:variable>
                  <xsl:element name="{concat($swath,'_',$polarization)}">
                    <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                    <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                    <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                    <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                    <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                  </xsl:element>                  
                </xsl:if>
                <xsl:if test="$swath_count=1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:variable>
                  <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                  <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                  <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                  <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                  <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                </xsl:if>
              </xsl:if>
              <xsl:if test="$polarization='HV'">
                <xsl:if test="$swath_count>1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:variable>
                  <xsl:element name="{concat($swath,'_',$polarization)}">
                    <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                    <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                    <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                    <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                    <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                  </xsl:element>
                </xsl:if>
                <xsl:if test="$swath_count=1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:variable>
                  <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                  <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                  <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                  <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                  <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                </xsl:if>
              </xsl:if>
              <xsl:if test="$polarization='VH'">
                <xsl:if test="$swath_count>1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:variable>
                  <xsl:element name="{concat($swath,'_',$polarization)}">
                    <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                    <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                    <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                    <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                    <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                  </xsl:element>
                </xsl:if>
                <xsl:if test="$swath_count=1">
                  <xsl:variable name="xml">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:variable>
                  <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
                  <width type="int" definition="width of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/></width>
                  <height type="int" definition="height of the image" units="pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/></height>
                  <x_spacing type="double" definition="spacing in x direction" units="m"><xsl:value-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/rangePixelSpacing,'#.000')"/></x_spacing>
                  <y_spacing type="double" definition="spacing in y direction" units="m"><xsl:copy-of select="format-number(document($meta)/product/imageAnnotation/imageInformation/azimuthPixelSpacing,'#.000')"/></y_spacing>
                </xsl:if>
              </xsl:if>
            </xsl:for-each>
            
            <!-- Assign radar frequencey, output pixels, pixel value and projection -->
            <xsl:if test="($polarization='DV') or ($polarization='SV') or ($polarization='VV')">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <radar_frequency type="double" definition="width of the image" units="Hz"><xsl:value-of select="format-number(document($meta)/product/generalAnnotation/productInformation/radarFrequency,'#.000')"/></radar_frequency>
              <output_pixels type="string" definition="data type of output pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/outputPixels"/></output_pixels>
              <pixel_value type="string" definition="interpretation of pixel value (Raw, Complex or Detected)"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/pixelValue"/></pixel_value>
              <projection type="string" definition="projection of the image"><xsl:value-of select="document($meta)/product/generalAnnotation/productInformation/projection"/></projection>
            </xsl:if>
            <xsl:if test="($polarization='DH') or ($polarization='SH') or ($polarization='HH')">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <radar_frequency type="double" definition="width of the image" units="Hz"><xsl:value-of select="format-number(document($meta)/product/generalAnnotation/productInformation/radarFrequency,'#.000')"/></radar_frequency>
              <output_pixels type="string" definition="data type of output pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/outputPixels"/></output_pixels>
              <pixel_value type="string" definition="interpretation of pixel value (Raw, Complex or Detected)"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/pixelValue"/></pixel_value>
              <projection type="string" definition="projection of the image"><xsl:value-of select="document($meta)/product/generalAnnotation/productInformation/projection"/></projection>
            </xsl:if>
            <xsl:if test="$polarization='HV'">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <radar_frequency type="double" definition="width of the image" units="Hz"><xsl:value-of select="format-number(document($meta)/product/generalAnnotation/productInformation/radarFrequency,'#.000')"/></radar_frequency>
              <output_pixels type="string" definition="data type of output pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/outputPixels"/></output_pixels>
              <pixel_value type="string" definition="interpretation of pixel value (Raw, Complex or Detected)"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/pixelValue"/></pixel_value>
              <projection type="string" definition="projection of the image"><xsl:value-of select="document($meta)/product/generalAnnotation/productInformation/projection"/></projection>
            </xsl:if>
            <xsl:if test="$polarization='VH'">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <radar_frequency type="double" definition="width of the image" units="Hz"><xsl:value-of select="format-number(document($meta)/product/generalAnnotation/productInformation/radarFrequency,'#.000')"/></radar_frequency>
              <output_pixels type="string" definition="data type of output pixels"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/outputPixels"/></output_pixels>
              <pixel_value type="string" definition="interpretation of pixel value (Raw, Complex or Detected)"><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/pixelValue"/></pixel_value>
              <projection type="string" definition="projection of the image"><xsl:value-of select="document($meta)/product/generalAnnotation/productInformation/projection"/></projection>
            </xsl:if>
          </xsl:if>
          <xsl:if test="$processing_level=0">
            <pixel_value type="string" definition="interpretation of pixel value (Raw, Complex or Detected)">Raw</pixel_value>
          </xsl:if>
          <ascending_node_time type="string" definition="time of the ascending node crossing"><xsl:copy-of select="$ascending_node_utc_time"/></ascending_node_time>
          <start_time_anx type="double" definition="start time relative to ascending node crossing"><xsl:copy-of select="number($start_time_anx)"/></start_time_anx>
          <stop_time_anx type="double" definition="stop time relative to ascending node crossing"><xsl:copy-of select="number($stop_time_anx)"/></stop_time_anx>
        <xsl:if test="not($product_type='OCN')">
          <xsl:variable name="coords"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/xmlData/safe:frameSet/safe:frame/safe:footPrint/gml:coordinates"/></xsl:variable>
          <xsl:variable name="first"><xsl:copy-of select="substring-before($coords,' ')"/></xsl:variable>
          <xsl:variable name="first_lat" select="substring-before($first,',')"/>
          <xsl:if test="$first_lat &gt; 66.5622">
            <epsg type="int" definition="EPSG code for map projection" label="EPSG code">3413</epsg>
          </xsl:if>
          <xsl:if test="($first_lat &lt; 66.5622) and ($first_lat &gt; -66.5622)">
            <epsg type="int" definition="EPSG code for map projection" label="EPSG code">4326</epsg>
          </xsl:if>
          <xsl:if test="$first_lat &lt; -66.5622">
            <epsg type="int" definition="EPSG code for map projection" label="EPSG code">3031</epsg>
          </xsl:if>          
        </xsl:if>
        <xsl:if test="$product_type='RAW'">
          <url type="string" definition="location of data in the archive" label="URL"><xsl:copy-of select="$server"/>/RAW/SA/<xsl:copy-of select="$granule"/>.zip</url>
        </xsl:if>
        <xsl:if test="$product_type='SLC'">
          <url type="string" definition="location of data in the archive" label="URL"><xsl:copy-of select="$server"/>/SLC/SA/<xsl:copy-of select="$granule"/>.zip</url>
        </xsl:if>
        <xsl:if test="$product_type='GRD'">
          <url type="string" definition="location of data in the archive" label="URL"><xsl:copy-of select="$server"/>/GRD/SA/<xsl:copy-of select="$granule"/>.zip</url>
        </xsl:if>
        <xsl:if test="$product_type='OCN'">
          <url type="string" definition="location of data in the archive" label="URL"><xsl:copy-of select="$server"/>/OCN/SA/<xsl:copy-of select="$granule"/>.zip</url>
        </xsl:if>
          <file_size type="double" definition="file size of product zip file [MB]" label="File size" units="MB"><xsl:copy-of select="$file_size"/></file_size>
        </image>
      </metadata>
      
    <xsl:if test="$processing_level=1">
      <!-- browse image section -->
      <browse>
        <amplitude><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='quicklook']/byteStream/fileLocation/@href"/></amplitude>
        <kml_overlay><xsl:value-of select="/xfdu:XFDU/dataObjectSection/dataObject[@ID='mapoverlay']/byteStream/fileLocation/@href"/></kml_overlay>
      </browse>
    </xsl:if>

    <xsl:for-each select="/xfdu:XFDU/metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/xmlData/safe:frameSet/safe:frame">
      <xsl:variable name="data_id"><xsl:value-of select="position()"/></xsl:variable>
      <xsl:variable name="data_count"><xsl:value-of select="count(/xfdu:XFDU/metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/xmlData/safe:frameSet/safe:frame)"/></xsl:variable>
      
      <!-- parsing of coordinate string - kind of lengthy -->
      <xsl:variable name="coordinates"><xsl:value-of select="safe:footPrint/gml:coordinates"/></xsl:variable>
      <xsl:variable name="coords1"><xsl:copy-of select="substring-before($coordinates,' ')"/></xsl:variable>
      <xsl:variable name="remain1"><xsl:copy-of select="substring-after($coordinates,' ')"/></xsl:variable>
      <xsl:variable name="coords2"><xsl:copy-of select="substring-before($remain1,' ')"/></xsl:variable>
      <xsl:variable name="remain2"><xsl:copy-of select="substring-after($remain1,' ')"/></xsl:variable>
      <xsl:variable name="coords3"><xsl:copy-of select="substring-before($remain2,' ')"/></xsl:variable>
      <xsl:variable name="remain3"><xsl:copy-of select="substring-after($remain2,' ')"/></xsl:variable>
      <xsl:variable name="coords4">
        <xsl:if test="contains($remain3,' ')"><xsl:value-of select="substring-before($remain3,' ')"/></xsl:if>
        <xsl:if test="not(contains($remain3,' '))"><xsl:copy-of select="substring-after($remain2,' ')"/></xsl:if>
      </xsl:variable>
      <xsl:variable name="lat1" select="substring-before($coords1,',')"/>
      <xsl:variable name="lat2" select="substring-before($coords2,',')"/>
      <xsl:variable name="lat3" select="substring-before($coords3,',')"/>
      <xsl:variable name="lat4" select="substring-before($coords4,',')"/>
      <xsl:variable name="lon1" select="substring-after($coords1,',')"/>
      <xsl:variable name="lon2" select="substring-after($coords2,',')"/>
      <xsl:variable name="lon3" select="substring-after($coords3,',')"/>
      <xsl:variable name="lon4" select="substring-after($coords4,',')"/>
      <xsl:variable name="lat">
        <lat1><xsl:copy-of select="$lat1"/></lat1>
        <lat2><xsl:copy-of select="$lat2"/></lat2>
        <lat3><xsl:copy-of select="$lat3"/></lat3>
        <lat4><xsl:copy-of select="$lat4"/></lat4>
      </xsl:variable>
      <xsl:variable name="lon">
        <lon1><xsl:copy-of select="$lon1"/></lon1>
        <lon2><xsl:copy-of select="$lon2"/></lon2>
        <lon3><xsl:copy-of select="$lon3"/></lon3>
        <lon4><xsl:copy-of select="$lon4"/></lon4>    
      </xsl:variable>
      <xsl:variable name="west_bound_longitude">
        <xsl:for-each select="exsl:node-set($lon)/*">
          <xsl:sort select="." data-type="number" order="ascending"/>
          <xsl:if test="position()=1"><xsl:value-of select="."/></xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <xsl:variable name="east_bound_longitude">
        <xsl:for-each select="exsl:node-set($lon)/*">
          <xsl:sort select="." data-type="number" order="descending"/>
          <xsl:if test="position()=1"><xsl:value-of select="."/></xsl:if>
        </xsl:for-each>    
      </xsl:variable>
      <xsl:variable name="north_bound_latitude">
        <xsl:for-each select="exsl:node-set($lat)/*">
          <xsl:sort select="." data-type="number" order="descending"/>
          <xsl:if test="position()=1"><xsl:value-of select="."/></xsl:if>
        </xsl:for-each>    
      </xsl:variable>
      <xsl:variable name="south_bound_latitude">
        <xsl:for-each select="exsl:node-set($lat)/*">
          <xsl:sort select="." data-type="number" order="ascending"/>
          <xsl:if test="position()=1"><xsl:value-of select="."/></xsl:if>
        </xsl:for-each>
      </xsl:variable>
      
      <!-- boundary coordinates -->
      <boundary>
        <xsl:if test="$data_count > 1"><xsl:attribute name="data_id"><xsl:value-of select="$data_id"/></xsl:attribute></xsl:if>
        <reference><xsl:value-of select="safe:footPrint/@srsName"/></reference>
        <coordinates><xsl:copy-of select="$coords1"/><xsl:text> </xsl:text><xsl:copy-of select="$coords2"/><xsl:text> </xsl:text><xsl:copy-of select="$coords3"/><xsl:text> </xsl:text><xsl:copy-of select="$coords4"/><xsl:text> </xsl:text><xsl:copy-of select="$coords1"/></coordinates>
        <polygon>
          <xsl:variable name="xml">
            <xsl:if test="($polarization='DV') or ($polarization='SV') or ($polarization='VV')">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/>1<xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
            </xsl:if>
            <xsl:if test="($polarization='DH') or ($polarization='SH') or ($polarization='HH')">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/>1<xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
            </xsl:if>
            <xsl:if test="$polarization='HV'">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/>1<xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
            </xsl:if>
            <xsl:if test="$polarization='VH'">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/>1<xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
            </xsl:if>
          </xsl:variable>
          <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
          <xsl:variable name="height" select="document($meta)/product/imageAnnotation/imageInformation/numberOfSamples"/>
          <xsl:variable name="width" select="document($meta)/product/imageAnnotation/imageInformation/numberOfLines"/>
          <point_count>5</point_count>
          <point id="1">
            <xsl:if test="($product_type='GRD') or ($product_type='SLC')">
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="line" select="line"/>
                <xsl:variable name="pixel" select="pixel"/>
                <xsl:variable name="latitude" select="latitude"/>
                <xsl:variable name="longitude" select="longitude"/>
                <xsl:variable name="diff_lat" select="$latitude - $lat1"/>
                <xsl:variable name="diff_lon" select="$longitude - $lon1"/>
                <xsl:if test="($diff_lat &gt; -0.0001) and ($diff_lat &lt; 0.0001) and ($diff_lon &gt; -0.0001) and ($diff_lon &lt; 0.0001)">
                  <line><xsl:value-of select="$line"/></line>
                  <sample><xsl:value-of select="$pixel"/></sample>
                </xsl:if>
              </xsl:for-each>
            </xsl:if>
            <lat><xsl:copy-of select="$lat1"/></lat>
            <lon><xsl:copy-of select="$lon1"/></lon>
          </point>
          <point id="2">
            <xsl:if test="($product_type='GRD') or ($product_type='SLC')">
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="line" select="line"/>
                <xsl:variable name="pixel" select="pixel"/>
                <xsl:variable name="latitude" select="latitude"/>
                <xsl:variable name="longitude" select="longitude"/>
                <xsl:variable name="diff_lat" select="$latitude - $lat2"/>
                <xsl:variable name="diff_lon" select="$longitude - $lon2"/>
                <xsl:if test="($diff_lat &gt; -0.0001) and ($diff_lat &lt; 0.0001) and ($diff_lon &gt; -0.0001) and ($diff_lon &lt; 0.0001)">
                  <line><xsl:value-of select="$line"/></line>
                  <sample><xsl:value-of select="$pixel"/></sample>
                </xsl:if>
              </xsl:for-each>
            </xsl:if>
            <lat><xsl:copy-of select="$lat2"/></lat>
            <lon><xsl:copy-of select="$lon2"/></lon>
          </point>
          <point id="3">
            <xsl:if test="($product_type='GRD') or ($product_type='SLC')">
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="line" select="line"/>
                <xsl:variable name="pixel" select="pixel"/>
                <xsl:variable name="latitude" select="latitude"/>
                <xsl:variable name="longitude" select="longitude"/>
                <xsl:variable name="diff_lat" select="$latitude - $lat3"/>
                <xsl:variable name="diff_lon" select="$longitude - $lon3"/>
                <xsl:if test="($diff_lat &gt; -0.0001) and ($diff_lat &lt; 0.0001) and ($diff_lon &gt; -0.0001) and ($diff_lon &lt; 0.0001)">
                  <line><xsl:value-of select="$line"/></line>
                  <sample><xsl:value-of select="$pixel"/></sample>
                </xsl:if>
              </xsl:for-each>
            </xsl:if>
            <lat><xsl:copy-of select="$lat3"/></lat>
            <lon><xsl:copy-of select="$lon3"/></lon>
          </point>
          <point id="4">
            <xsl:if test="($product_type='GRD') or ($product_type='SLC')">
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="line" select="line"/>
                <xsl:variable name="pixel" select="pixel"/>
                <xsl:variable name="latitude" select="latitude"/>
                <xsl:variable name="longitude" select="longitude"/>
                <xsl:variable name="diff_lat" select="$latitude - $lat4"/>
                <xsl:variable name="diff_lon" select="$longitude - $lon4"/>
                <xsl:if test="($diff_lat &gt; -0.0001) and ($diff_lat &lt; 0.0001) and ($diff_lon &gt; -0.0001) and ($diff_lon &lt; 0.0001)">
                  <line><xsl:value-of select="$line"/></line>
                  <sample><xsl:value-of select="$pixel"/></sample>
                </xsl:if>
              </xsl:for-each>
            </xsl:if>
            <lat><xsl:copy-of select="$lat4"/></lat>
            <lon><xsl:copy-of select="$lon4"/></lon>
          </point>
          <point id="5">
            <xsl:if test="($product_type='GRD') or ($product_type='SLC')">
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="line" select="line"/>
                <xsl:variable name="pixel" select="pixel"/>
                <xsl:variable name="latitude" select="latitude"/>
                <xsl:variable name="longitude" select="longitude"/>
                <xsl:variable name="diff_lat" select="$latitude - $lat1"/>
                <xsl:variable name="diff_lon" select="$longitude - $lon1"/>
                <xsl:if test="($diff_lat &gt; -0.0001) and ($diff_lat &lt; 0.0001) and ($diff_lon &gt; -0.0001) and ($diff_lon &lt; 0.0001)">
                  <line><xsl:value-of select="$line"/></line>
                  <sample><xsl:value-of select="$pixel"/></sample>
                </xsl:if>
              </xsl:for-each>
            </xsl:if>
            <lat><xsl:copy-of select="$lat1"/></lat>
            <lon><xsl:copy-of select="$lon1"/></lon>
          </point>
        </polygon>
      </boundary>
      
      <!-- geospatial and temporal extent -->
      <extent>
        <xsl:if test="$data_count > 1"><xsl:attribute name="data_id"><xsl:value-of select="$data_id"/></xsl:attribute></xsl:if>
        <westBoundLongitude><xsl:copy-of select="$west_bound_longitude"/></westBoundLongitude>
        <eastBoundLongitude><xsl:copy-of select="$east_bound_longitude"/></eastBoundLongitude>
        <northBoundLatitude><xsl:copy-of select="$north_bound_latitude"/></northBoundLatitude>
        <southBoundLatitude><xsl:copy-of select="$south_bound_latitude"/></southBoundLatitude>
        <start_datetime><xsl:copy-of select="$start_acquisition_utc_time"/></start_datetime>
        <end_datetime><xsl:copy-of select="$end_acquistion_utc_time"/></end_datetime>
      </extent>

    </xsl:for-each>
      
    <xsl:if test="$processing_level=1">

      <!-- statistics -->
      <statistics>
        <xsl:for-each select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:extension/s1sarl1:instrumentMode/s1sarl1:swath">
          <xsl:variable name="swath" select="."/>
          <xsl:if test="$polarization='DV'">
            <xsl:element name="{concat($swath,'_VH')}">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>
            <xsl:element name="{concat($swath,'_VV')}">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='DH'">
            <xsl:element name="{concat($swath,'_HH')}">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>            
            <xsl:element name="{concat($swath,'_HV')}">
              <xsl:variable name="xml">
                <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
                <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
              </xsl:variable>
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>
          </xsl:if>
          <xsl:if test="($polarization='SV') or ($polarization='VV')">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
            </xsl:variable>
            <xsl:element name="{concat($swath,'_VV')}">
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>
          </xsl:if>
          <xsl:if test="($polarization='SH') or ($polarization='HH')">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
            </xsl:variable>
            <xsl:element name="{concat($swath,'_HH')}">
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='HV'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
            </xsl:variable>
            <xsl:element name="{concat($swath,'_HV')}">
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='VH'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
            </xsl:variable>
            <xsl:element name="{concat($swath,'_VH')}">
              <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
              <mean>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataMean/im"/></im>
              </mean>
              <standard_deviation>
                <re><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/re"/></re>
                <im><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/imageStatistics/outputDataStdDev/im"/></im>
              </standard_deviation>
            </xsl:element>
          </xsl:if>
        </xsl:for-each>
      </statistics>
    </xsl:if>
      
    <xsl:if test="$product_type='RAW'">
      <!-- processing: RAW -->
      <processing>
        <processing_step ID='RAW'>
          <name>RAW product generation</name>
          <xsl:variable name="processing_step">
            <xsl:if test="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing/@name='Generation of Sentinel-1 SAR Slice L0 product'">Generation of Sentinel-1 SAR Slice L0 product</xsl:if>
            <xsl:if test="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing/@name='Generation of Sentinel-1 L0 SAR Product'">Generation of Sentinel-1 L0 SAR Product</xsl:if>
          </xsl:variable>
          <xsl:variable name="processing_raw_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name=$processing_step]/@stop"/></xsl:variable>
          <datetime><xsl:copy-of select="$processing_raw_time"/><xsl:if test="not(contains($processing_raw_time,'Z'))">Z</xsl:if></datetime>
        </processing_step>
      </processing>
    </xsl:if>
    <xsl:if test="$product_type='SLC'">
      <!-- processing: SLC -->
      <processing>
        <software><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='SLC Post Processing']/safe:facility/safe:software/@name"/></software>
        <software_version><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='SLC Post Processing']/safe:facility/safe:software/@version"/></software_version>
        <processor>
          <organization><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='SLC Post Processing']/safe:facility/@organisation"/></organization>
          <site><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='SLC Post Processing']/safe:facility/@site"/></site>
          <country><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='SLC Post Processing']/safe:facility/@country"/></country>
        </processor>
        <data_source><xsl:copy-of select="$data_source"/></data_source>
        <processing_step ID='SLC'>
          <name>SLC Post Processing</name>
          <xsl:variable name="processing_slc_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='SLC Post Processing']/safe:resource/safe:processing/@stop"/></xsl:variable>
          <datetime><xsl:copy-of select="$processing_utc_time"/></datetime>
        </processing_step>
      </processing>
    </xsl:if>
    <xsl:if test="$product_type='GRD'">
      <!-- processing: GRD -->
      <processing>
        <software><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='GRD Post Processing']/safe:facility/safe:software/@name"/></software>
        <software_version><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='GRD Post Processing']/safe:facility/safe:software/@version"/></software_version>
        <processor>
          <organization><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='GRD Post Processing']/safe:facility/@organisation"/></organization>
          <site><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='GRD Post Processing']/safe:facility/@site"/></site>
          <country><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='GRD Post Processing']/safe:facility/@country"/></country>
        </processor>
        <data_source><xsl:copy-of select="$data_source"/></data_source>
        <processing_step ID='SLC'>
          <name>SLC Processing</name>
          <xsl:variable name="processing_slc_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='GRD Post Processing']/safe:resource/safe:processing/@stop"/></xsl:variable>
          <datetime><xsl:copy-of select="$processing_slc_time"/><xsl:if test="not(contains($processing_slc_time,'Z'))">Z</xsl:if></datetime>
        </processing_step>
        <processing_step ID='GRD'>
          <name>GRD Post Processing</name>
          <datetime><xsl:copy-of select="$processing_utc_time"/></datetime>
        </processing_step>
      </processing>
    </xsl:if>
    <xsl:if test="$product_type='OCN'">
      <!-- processing: OCN -->
      <processing>
        <software><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='OCN Processing']/safe:facility/safe:software/@name"/></software>
        <software_version><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='OCN Processing']/safe:facility/safe:software/@version"/></software_version>
        <processor>
          <organization><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='OCN Processing']/safe:facility/@organisation"/></organization>
          <site><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='OCN Processing']/safe:facility/@site"/></site>
          <country><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='OCN Processing']/safe:facility/@country"/></country>
        </processor>
        <data_source><xsl:copy-of select="$data_source"/></data_source>
        <processing_step ID='SLC'>
          <name>SLC Processing</name>
          <xsl:variable name="processing_slc_time"><xsl:value-of select="/xfdu:XFDU/metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/safe:processing[@name='OCN Processing']/safe:resource/safe:processing/@stop"/></xsl:variable>
          <datetime><xsl:copy-of select="$processing_slc_time"/><xsl:if test="not(contains($processing_slc_time,'Z'))">Z</xsl:if></datetime>
        </processing_step>
        <processing_step ID='OCN'>
          <name>OCN Processing</name>
          <datetime><xsl:copy-of select="$processing_utc_time"/></datetime>
        </processing_step>
      </processing>      
    </xsl:if>
      
      <!-- root section -->
      <root>
        <institution>Alaska Satellite Facility</institution>
        <title><xsl:copy-of select="$platform"/> product: <xsl:copy-of select="$directory"/></title>
        <source><xsl:copy-of select="$platform"/> data with <xsl:copy-of select="$polarization"/> polarization</source>
      <xsl:if test="$processing_level=1">
        <original_file><xsl:copy-of select="$data_source"/></original_file>
      </xsl:if>
        <comment>Copyright: European Space Agency (<xsl:copy-of select="$year"/>)</comment>
        <reference>Documentation available at: www.asf.alaska.edu</reference>
        <history><xsl:copy-of select="$processing_utc_time"/>: <xsl:copy-of select="$format"/> file created.</history>
      </root>

      <xsl:if test="$processing_level=1">
        <geometry>
                
        <!-- orbit information -->
        <xsl:for-each select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:extension/s1sarl1:instrumentMode/s1sarl1:swath">
          <xsl:variable name="swath_number"><xsl:value-of select="position()"/></xsl:variable>
          <xsl:if test="$polarization='DV'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:if test="$swath_number=1">
              <orbit>
                <frame><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/orbit[1]/frame"/></frame>
                <vector_count><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/@count"/></vector_count>
                <xsl:for-each select="document($meta)/product/generalAnnotation/orbitList/orbit">
                  <xsl:variable name="pos"><xsl:value-of select="position()"/></xsl:variable>
                  <vector id="{$pos}">
                    <time><xsl:value-of select="time"/>Z</time>
                    <position_x units="m"><xsl:value-of select="format-number(position/x,'#.0000000000')"/></position_x>
                    <position_y units="m"><xsl:value-of select="format-number(position/y,'#.0000000000')"/></position_y>
                    <position_z units="m"><xsl:value-of select="format-number(position/z,'#.0000000000')"/></position_z>
                    <velocity_x units="m/s"><xsl:value-of select="format-number(velocity/x,'#.0000000000')"/></velocity_x>
                    <velocity_y units="m/s"><xsl:value-of select="format-number(velocity/y,'#.0000000000')"/></velocity_y>
                    <velocity_z units="m/s"><xsl:value-of select="format-number(velocity/z,'#.0000000000')"/></velocity_z>
                  </vector>
                </xsl:for-each>
              </orbit>
            </xsl:if>
            <slant_range_time><xsl:value-of select="document($meta)/product/imageAnnotation/imageInformation/slantRangeTime"/></slant_range_time>
          </xsl:if>
          <xsl:if test="$polarization='DH'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:if test="$swath_number=1">
              <orbit>
                <frame><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/orbit[1]/frame"/></frame>
                <vector_count><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/@count"/></vector_count>
                <xsl:for-each select="document($meta)/product/generalAnnotation/orbitList/orbit">
                  <xsl:variable name="pos"><xsl:value-of select="position()"/></xsl:variable>
                  <vector id="{$pos}">
                    <time><xsl:value-of select="time"/>Z</time>
                    <position_x units="m"><xsl:value-of select="format-number(position/x,'#.0000000000')"/></position_x>
                    <position_y units="m"><xsl:value-of select="format-number(position/y,'#.0000000000')"/></position_y>
                    <position_z units="m"><xsl:value-of select="format-number(position/z,'#.0000000000')"/></position_z>
                    <velocity_x units="m/s"><xsl:value-of select="format-number(velocity/x,'#.0000000000')"/></velocity_x>
                    <velocity_y units="m/s"><xsl:value-of select="format-number(velocity/y,'#.0000000000')"/></velocity_y>
                    <velocity_z units="m/s"><xsl:value-of select="format-number(velocity/z,'#.0000000000')"/></velocity_z>
                  </vector>
                </xsl:for-each>
              </orbit>
            </xsl:if>
          </xsl:if>
          <xsl:if test="($polarization='SV') or ($polarization='VV')">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:if test="$swath_number=1">
              <orbit>
                <frame><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/orbit[1]/frame"/></frame>
                <vector_count><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/@count"/></vector_count>
                <xsl:for-each select="document($meta)/product/generalAnnotation/orbitList/orbit">
                  <xsl:variable name="pos"><xsl:value-of select="position()"/></xsl:variable>
                  <vector id="{$pos}">
                    <time><xsl:value-of select="time"/>Z</time>
                    <position_x units="m"><xsl:value-of select="format-number(position/x,'#.0000000000')"/></position_x>
                    <position_y units="m"><xsl:value-of select="format-number(position/y,'#.0000000000')"/></position_y>
                    <position_z units="m"><xsl:value-of select="format-number(position/z,'#.0000000000')"/></position_z>
                    <velocity_x units="m/s"><xsl:value-of select="format-number(velocity/x,'#.0000000000')"/></velocity_x>
                    <velocity_y units="m/s"><xsl:value-of select="format-number(velocity/y,'#.0000000000')"/></velocity_y>
                    <velocity_z units="m/s"><xsl:value-of select="format-number(velocity/z,'#.0000000000')"/></velocity_z>
                  </vector>
                </xsl:for-each>
              </orbit>
            </xsl:if>
          </xsl:if>
          <xsl:if test="($polarization='SH') or ($polarization='HH')">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:if test="$swath_number=1">
              <orbit>
                <frame><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/orbit[1]/frame"/></frame>
                <vector_count><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/@count"/></vector_count>
                <xsl:for-each select="document($meta)/product/generalAnnotation/orbitList/orbit">
                  <xsl:variable name="pos"><xsl:value-of select="position()"/></xsl:variable>
                  <vector id="{$pos}">
                    <time><xsl:value-of select="time"/>Z</time>
                    <position_x units="m"><xsl:value-of select="format-number(position/x,'#.0000000000')"/></position_x>
                    <position_y units="m"><xsl:value-of select="format-number(position/y,'#.0000000000')"/></position_y>
                    <position_z units="m"><xsl:value-of select="format-number(position/z,'#.0000000000')"/></position_z>
                    <velocity_x units="m/s"><xsl:value-of select="format-number(velocity/x,'#.0000000000')"/></velocity_x>
                    <velocity_y units="m/s"><xsl:value-of select="format-number(velocity/y,'#.0000000000')"/></velocity_y>
                    <velocity_z units="m/s"><xsl:value-of select="format-number(velocity/z,'#.0000000000')"/></velocity_z>
                  </vector>
                </xsl:for-each>
              </orbit>
            </xsl:if>
          </xsl:if>
          <xsl:if test="$polarization='HV'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:if test="$swath_number=1">
              <orbit>
                <frame><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/orbit[1]/frame"/></frame>
                <vector_count><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/@count"/></vector_count>
                <xsl:for-each select="document($meta)/product/generalAnnotation/orbitList/orbit">
                  <xsl:variable name="pos"><xsl:value-of select="position()"/></xsl:variable>
                  <vector id="{$pos}">
                    <time><xsl:value-of select="time"/>Z</time>
                    <position_x units="m"><xsl:value-of select="format-number(position/x,'#.0000000000')"/></position_x>
                    <position_y units="m"><xsl:value-of select="format-number(position/y,'#.0000000000')"/></position_y>
                    <position_z units="m"><xsl:value-of select="format-number(position/z,'#.0000000000')"/></position_z>
                    <velocity_x units="m/s"><xsl:value-of select="format-number(velocity/x,'#.0000000000')"/></velocity_x>
                    <velocity_y units="m/s"><xsl:value-of select="format-number(velocity/y,'#.0000000000')"/></velocity_y>
                    <velocity_z units="m/s"><xsl:value-of select="format-number(velocity/z,'#.0000000000')"/></velocity_z>
                  </vector>
                </xsl:for-each>
              </orbit>
            </xsl:if>
          </xsl:if>
          <xsl:if test="$polarization='VH'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:if test="$swath_number=1">
              <orbit>
                <frame><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/orbit[1]/frame"/></frame>
                <vector_count><xsl:value-of select="document($meta)/product/generalAnnotation/orbitList/@count"/></vector_count>
                <xsl:for-each select="document($meta)/product/generalAnnotation/orbitList/orbit">
                  <xsl:variable name="pos"><xsl:value-of select="position()"/></xsl:variable>
                  <vector id="{$pos}">
                    <time><xsl:value-of select="time"/>Z</time>
                    <position_x units="m"><xsl:value-of select="format-number(position/x,'#.0000000000')"/></position_x>
                    <position_y units="m"><xsl:value-of select="format-number(position/y,'#.0000000000')"/></position_y>
                    <position_z units="m"><xsl:value-of select="format-number(position/z,'#.0000000000')"/></position_z>
                    <velocity_x units="m/s"><xsl:value-of select="format-number(velocity/x,'#.0000000000')"/></velocity_x>
                    <velocity_y units="m/s"><xsl:value-of select="format-number(velocity/y,'#.0000000000')"/></velocity_y>
                    <velocity_z units="m/s"><xsl:value-of select="format-number(velocity/z,'#.0000000000')"/></velocity_z>
                  </vector>
                </xsl:for-each>
              </orbit>
            </xsl:if>
          </xsl:if>
        </xsl:for-each>
          
          <!-- geolocation grid points -->
        <xsl:for-each select="/xfdu:XFDU/metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/safe:platform/safe:instrument/safe:extension/s1sarl1:instrumentMode/s1sarl1:swath">
          <xsl:variable name="swath_number"><xsl:value-of select="position()"/></xsl:variable>
          <xsl:variable name="swath" select="."/>
          <xsl:if test="$polarization='DV'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:element name="{$swath}">
              <grid_point_count><xsl:value-of select="document($meta)/product/geolocationGrid/geolocationGridPointList/@count"/></grid_point_count>
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="gcp"><xsl:value-of select="position()"/></xsl:variable>
                <geolocation_grid_point id="{$gcp}">
                  <azimuth_time><xsl:value-of select="azimuthTime"/>Z</azimuth_time>
                  <slant_range_time><xsl:value-of select="format-number(slantRangeTime,'0.000000000000')"/></slant_range_time>
                  <line><xsl:value-of select="line"/></line>
                  <pixel><xsl:value-of select="pixel"/></pixel>
                  <latitude><xsl:value-of select="format-number(latitude,'#.000000')"/></latitude>
                  <longitude><xsl:value-of select="format-number(longitude,'#.000000')"/></longitude>
                  <incidence_angle><xsl:value-of select="format-number(incidenceAngle,'#.000000')"/></incidence_angle>
                </geolocation_grid_point>
              </xsl:for-each>
            </xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='DH'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:element name="{$swath}">
              <grid_point_count><xsl:value-of select="document($meta)/product/geolocationGrid/geolocationGridPointList/@count"/></grid_point_count>
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="gcp"><xsl:value-of select="position()"/></xsl:variable>
                <geolocation_grid_point id="{$gcp}">
                  <azimuth_time><xsl:value-of select="azimuthTime"/>Z</azimuth_time>
                  <slant_range_time><xsl:value-of select="format-number(slantRangeTime,'0.000000000000')"/></slant_range_time>
                  <line><xsl:value-of select="line"/></line>
                  <pixel><xsl:value-of select="pixel"/></pixel>
                  <latitude><xsl:value-of select="format-number(latitude,'#.000000')"/></latitude>
                  <longitude><xsl:value-of select="format-number(longitude,'#.000000')"/></longitude>
                  <incidence_angle><xsl:value-of select="format-number(incidenceAngle,'#.000000')"/></incidence_angle>
                </geolocation_grid_point>
              </xsl:for-each>
            </xsl:element>
          </xsl:if>
          <xsl:if test="($polarization='SV') or ($polarization='VV')">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vv</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:element name="{$swath}">
              <grid_point_count><xsl:value-of select="document($meta)/product/geolocationGrid/geolocationGridPointList/@count"/></grid_point_count>
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="gcp"><xsl:value-of select="position()"/></xsl:variable>
                <geolocation_grid_point id="{$gcp}">
                  <azimuth_time><xsl:value-of select="azimuthTime"/>Z</azimuth_time>
                  <slant_range_time><xsl:value-of select="format-number(slantRangeTime,'0.000000000000')"/></slant_range_time>
                  <line><xsl:value-of select="line"/></line>
                  <pixel><xsl:value-of select="pixel"/></pixel>
                  <latitude><xsl:value-of select="format-number(latitude,'#.000000')"/></latitude>
                  <longitude><xsl:value-of select="format-number(longitude,'#.000000')"/></longitude>
                  <incidence_angle><xsl:value-of select="format-number(incidenceAngle,'#.000000')"/></incidence_angle>
                </geolocation_grid_point>
              </xsl:for-each>
            </xsl:element>
          </xsl:if>
          <xsl:if test="($polarization='SH') or ($polarization='HH')">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hh</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:element name="{$swath}">
              <grid_point_count><xsl:value-of select="document($meta)/product/geolocationGrid/geolocationGridPointList/@count"/></grid_point_count>
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="gcp"><xsl:value-of select="position()"/></xsl:variable>
                <geolocation_grid_point id="{$gcp}">
                  <azimuth_time><xsl:value-of select="azimuthTime"/>Z</azimuth_time>
                  <slant_range_time><xsl:value-of select="format-number(slantRangeTime,'0.000000000000')"/></slant_range_time>
                  <line><xsl:value-of select="line"/></line>
                  <pixel><xsl:value-of select="pixel"/></pixel>
                  <latitude><xsl:value-of select="format-number(latitude,'#.000000')"/></latitude>
                  <longitude><xsl:value-of select="format-number(longitude,'#.000000')"/></longitude>
                  <incidence_angle><xsl:value-of select="format-number(incidenceAngle,'#.000000')"/></incidence_angle>
                </geolocation_grid_point>
              </xsl:for-each>
            </xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='HV'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>hv</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:element name="{$swath}">
              <grid_point_count><xsl:value-of select="document($meta)/product/geolocationGrid/geolocationGridPointList/@count"/></grid_point_count>
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="gcp"><xsl:value-of select="position()"/></xsl:variable>
                <geolocation_grid_point id="{$gcp}">
                  <azimuth_time><xsl:value-of select="azimuthTime"/>Z</azimuth_time>
                  <slant_range_time><xsl:value-of select="format-number(slantRangeTime,'0.000000000000')"/></slant_range_time>
                  <line><xsl:value-of select="line"/></line>
                  <pixel><xsl:value-of select="pixel"/></pixel>
                  <latitude><xsl:value-of select="format-number(latitude,'#.000000')"/></latitude>
                  <longitude><xsl:value-of select="format-number(longitude,'#.000000')"/></longitude>
                  <incidence_angle><xsl:value-of select="format-number(incidenceAngle,'#.000000')"/></incidence_angle>
                </geolocation_grid_point>
              </xsl:for-each>
            </xsl:element>
          </xsl:if>
          <xsl:if test="$polarization='VH'">
            <xsl:variable name="xml">
              <xsl:if test="$swath_count>1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="position()"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
              <xsl:if test="$swath_count=1">product<xsl:value-of select="translate($mission_id,$uppercase,$smallcase)"/><xsl:value-of select="translate($beam_mode,$uppercase,$smallcase)"/><xsl:value-of select="translate($product_type,$uppercase,$smallcase)"/>vh</xsl:if>
            </xsl:variable>
            <xsl:variable name="meta" select="concat($path,'/',substring(/xfdu:XFDU/dataObjectSection/dataObject[starts-with(@ID,$xml)]/byteStream/fileLocation/@href,3))"/>
            <xsl:element name="{$swath}">
              <grid_point_count><xsl:value-of select="document($meta)/product/geolocationGrid/geolocationGridPointList/@count"/></grid_point_count>
              <xsl:for-each select="document($meta)/product/geolocationGrid/geolocationGridPointList/geolocationGridPoint">
                <xsl:variable name="gcp"><xsl:value-of select="position()"/></xsl:variable>
                <geolocation_grid_point id="{$gcp}">
                  <azimuth_time><xsl:value-of select="azimuthTime"/>Z</azimuth_time>
                  <slant_range_time><xsl:value-of select="format-number(slantRangeTime,'0.000000000000')"/></slant_range_time>
                  <line><xsl:value-of select="line"/></line>
                  <pixel><xsl:value-of select="pixel"/></pixel>
                  <latitude><xsl:value-of select="format-number(latitude,'#.000000')"/></latitude>
                  <longitude><xsl:value-of select="format-number(longitude,'#.000000')"/></longitude>
                  <incidence_angle><xsl:value-of select="format-number(incidenceAngle,'#.000000')"/></incidence_angle>
                </geolocation_grid_point>
              </xsl:for-each>
            </xsl:element>
          </xsl:if>
        </xsl:for-each>
          
      </geometry>
    </xsl:if>
      
    </sentinel>
  </xsl:template>
</xsl:stylesheet>

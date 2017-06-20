<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" encoding="utf-8" indent="yes" />
<xsl:template match="/">
<gmd:DS_Series xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
  xmlns:gmd="http://www.isotc211.org/2005/gmd" 
  xmlns:gco="http://www.isotc211.org/2005/gco" 
  xmlns:xs="http://www.w3.org/2001/XMLSchema" 
  xmlns:eos="http://earthdata.nasa.gov/schema/eos" 
  xmlns:echo="http://www.echo.nasa.gov/ingest/schemas/operatations" 
  xmlns:xlink="http://www.w3.org/1999/xlink" 
  xmlns:gml="http://www.opengis.net/gml/3.2" 
  xmlns:gmi="http://www.isotc211.org/2005/gmi" 
  xmlns:gmx="http://www.isotc211.org/2005/gmx">
  <gmd:composedOf>
    <gmd:DS_DataSet>
      <gmd:has>
        <gmi:MI_Metadata>
          <gmd:fileIdentifier>
            <gco:CharacterString><xsl:value-of select="/hdf5/granule" />.iso.xml</gco:CharacterString>
          </gmd:fileIdentifier>
          <gmd:language>
            <gco:CharacterString>eng</gco:CharacterString>
          </gmd:language>
          <gmd:characterSet>
            <gmd:MD_CharacterSetCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
          </gmd:characterSet>
          <gmd:hierarchyLevel>
            <gmd:MD_ScopeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
          </gmd:hierarchyLevel>
          <gmd:contact>
            <gmd:CI_ResponsibleParty>
              <gmd:organisationName>
                <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
              </gmd:organisationName>
              <gmd:contactInfo>
                <gmd:CI_Contact id="ASFcontactInfo">
                  <gmd:phone>
                    <gmd:CI_Telephone>
                      <gmd:voice>
                        <gco:CharacterString>907-474-6166</gco:CharacterString>
                      </gmd:voice>
                      <gmd:facsimile>
                        <gco:CharacterString>907-474-2665</gco:CharacterString>
                      </gmd:facsimile>
                    </gmd:CI_Telephone>
                  </gmd:phone>
                  <gmd:address>
                    <gmd:CI_Address>
                      <gmd:deliveryPoint>
                        <gco:CharacterString>903 Koyukuk Dr.</gco:CharacterString>
                      </gmd:deliveryPoint>
                      <gmd:city>
                        <gco:CharacterString>Fairbanks</gco:CharacterString>
                      </gmd:city>
                      <gmd:administrativeArea>
                        <gco:CharacterString>AK</gco:CharacterString>
                      </gmd:administrativeArea>
                      <gmd:postalCode>
                        <gco:CharacterString>99775-7320</gco:CharacterString>
                      </gmd:postalCode>
                      <gmd:country>
                        <gco:CharacterString>USA</gco:CharacterString>
                      </gmd:country>
                      <gmd:electronicMailAddress>
                        <gco:CharacterString>uso@asf.alaska.edu</gco:CharacterString>
                      </gmd:electronicMailAddress>
                    </gmd:CI_Address>
                  </gmd:address>
                </gmd:CI_Contact>
              </gmd:contactInfo>
              <gmd:role>
                <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="pointOfContact">pointOfContact</gmd:CI_RoleCode>
              </gmd:role>
            </gmd:CI_ResponsibleParty>
          </gmd:contact>
          <gmd:dateStamp>
            <gco:DateTime>
              <xsl:value-of select="/hdf5/metadata_creation" />
            </gco:DateTime>
          </gmd:dateStamp>
          <gmd:metadataStandardName>
            <gco:CharacterString>ISO 19115-2 Geographic information — Metadata — Part 2: Extensions for imagery and gridded data</gco:CharacterString>
          </gmd:metadataStandardName>
          <gmd:metadataStandardVersion>
            <gco:CharacterString>ISO 19115-2:2009-02-15</gco:CharacterString>
          </gmd:metadataStandardVersion>
          <gmd:spatialRepresentationInfo>
            <gmd:MD_GridSpatialRepresentation>
              <gmd:numberOfDimensions>
                <gco:Integer>2</gco:Integer>
              </gmd:numberOfDimensions>
              <gmd:axisDimensionProperties>
                <gmd:MD_Dimension>
                  <gmd:dimensionName>
                    <gmd:MD_DimensionNameTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_DimensionNameTypeCode" codeListValue="row">row</gmd:MD_DimensionNameTypeCode>
                  </gmd:dimensionName>
                  <gmd:dimensionSize>
                    <gco:Integer><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/height" /></gco:Integer>
                  </gmd:dimensionSize>
                  <gmd:resolution>
                    <gco:Length uom="meter"><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/y_spacing" /></gco:Length>
                  </gmd:resolution>
                </gmd:MD_Dimension>
              </gmd:axisDimensionProperties>
              <gmd:axisDimensionProperties>
                <gmd:MD_Dimension>
                  <gmd:dimensionName>
                    <gmd:MD_DimensionNameTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_DimensionNameTypeCode" codeListValue="column">column</gmd:MD_DimensionNameTypeCode>
                  </gmd:dimensionName>
                  <gmd:dimensionSize>
                    <gco:Integer><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/width" /></gco:Integer>
                  </gmd:dimensionSize>
                  <gmd:resolution>
                    <gco:Length uom="meter"><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/x_spacing" /></gco:Length>
                  </gmd:resolution>
                </gmd:MD_Dimension>
              </gmd:axisDimensionProperties>
              <gmd:cellGeometry>
                <gmd:MD_CellGeometryCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CellGeometryCode" codeListValue="area">area</gmd:MD_CellGeometryCode>
              </gmd:cellGeometry>
              <gmd:transformationParameterAvailability>
                <gco:Boolean>false</gco:Boolean>
              </gmd:transformationParameterAvailability>
              <eos:otherPropertyType>
                <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
              </eos:otherPropertyType>
              <eos:otherProperty> 
                <gco:Record>
                  <eos:additionalAttributes>
                    <eos:EOS_AdditionalAttributes>
                      <eos:additionalAttribute>
                        <eos:EOS_AdditionalAttribute>
                          <eos:reference>
                            <eos:EOS_AdditionalAttributeDescription>
                              <eos:type>
                                <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="spatialInformation">spatialInformation</eos:EOS_AdditionalAttributeTypeCode>
                              </eos:type>
                              <eos:name>
                                <gco:CharacterString>map projection</gco:CharacterString>
                              </eos:name>
                              <eos:description>
                                <gco:CharacterString>map projection definition (in well known text format) for the terrain corrected image</gco:CharacterString>
                              </eos:description>
                              <eos:dataType>
                                <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="STRING">STRING</eos:EOS_AdditionalAttributeDataTypeCode>
                              </eos:dataType>
                            </eos:EOS_AdditionalAttributeDescription>
                          </eos:reference>
                          <eos:value>
                            <gco:CharacterString><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/projection_string" /></gco:CharacterString>
                          </eos:value>
                        </eos:EOS_AdditionalAttribute>
                      </eos:additionalAttribute>
                    </eos:EOS_AdditionalAttributes>
                  </eos:additionalAttributes>
                </gco:Record>
              </eos:otherProperty>
            </gmd:MD_GridSpatialRepresentation>
          </gmd:spatialRepresentationInfo>
          <gmd:identificationInfo>
            <gmd:MD_DataIdentification>
              <gmd:citation>
                <gmd:CI_Citation>
                  <gmd:title>
                    <gmx:FileName><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/file" /></gmx:FileName>
                  </gmd:title>
                  <gmd:alternateTitle>
                    <gco:CharacterString>terrain corrected image</gco:CharacterString>
                  </gmd:alternateTitle>
                  <gmd:date>
                    <gmd:CI_Date>
                      <gmd:date>
                        <gco:DateTime><xsl:value-of select="/hdf5/metadata_creation" /></gco:DateTime>
                      </gmd:date>
                      <gmd:dateType>
                        <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_DateTypeCode" codeListValue="creation">creation</gmd:CI_DateTypeCode>
                      </gmd:dateType>
                    </gmd:CI_Date>
                  </gmd:date>
                  <gmd:citedResponsibleParty>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:citedResponsibleParty>
                  <gmd:presentationForm>
                    <gmd:CI_PresentationFormCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_PresentationFormCode" codeListValue="documentDigital">documentDigital</gmd:CI_PresentationFormCode>
                  </gmd:presentationForm>
                  <gmd:series>
                    <gmd:CI_Series>
                      <gmd:name>
                      <xsl:if test="/hdf5/metadata/input_image/platform='ALOS'">
                        <gco:CharacterString>The granule for the generation of this terrain corrected product has been acquired as part of the ALOS mission. The ALOS satellite was launched on January 24, 2006. ALOS had a 46-day repeat cycle and operated until May 12, 2011.</gco:CharacterString>
                      </xsl:if>
                      <xsl:if test="/hdf5/metadata/input_image/platform='ERS-1'">
                        <gco:CharacterString>The granule for the generation of this terrain corrected product has been acquired as part of the ERS-1 mission. The ERS-1 satellite was launched on July 17, 1991. ERS-1 had various repeat cycles and operated until March 10, 2000.</gco:CharacterString>
                      </xsl:if>
                      <xsl:if test="/hdf5/metadata/input_image/platform='ERS-2'">
                        <gco:CharacterString>The granule for the generation of this terrain corrected product has been acquired as part of the ERS-2 mission. The ERS-2 satellite was launched on April 21, 1995. ERS-2 had a 35-day repeat cycle and operated until September 5, 2011.</gco:CharacterString>
                      </xsl:if>
                      <xsl:if test="/hdf5/metadata/input_image/platform='Sentinel-1A'">
                        <gco:CharacterString>The granule for the generation of this terrain corrected product has been acquired as part of the Copernicus Sentinel-1A mission. The Sentinel-1A satellite was launched on April 3, 2014. Sentinel-1A has a 12-day repeat cycle.</gco:CharacterString>
                      </xsl:if>
                      </gmd:name>
                    </gmd:CI_Series>
                  </gmd:series>
                </gmd:CI_Citation>
              </gmd:citation>
              <gmd:abstract>
                <gco:CharacterString>The terrain corrected product is derived from a single look complex SAR image. It is provided in Universal Transverse Mercator coordinates and is corrected for terrain by using a DEM.</gco:CharacterString>
              </gmd:abstract>
              <gmd:status>
                <gmd:MD_ProgressCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ProgressCode" codeListValue="completed">completed</gmd:MD_ProgressCode>
              </gmd:status>
              <gmd:resourceMaintenance>
                <gmd:MD_MaintenanceInformation>
                  <gmd:maintenanceAndUpdateFrequency>
                    <gmd:MD_MaintenanceFrequencyCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MaintenanceFrequencyCode" codeListValue="asNeeded">asNeeded</gmd:MD_MaintenanceFrequencyCode>
                  </gmd:maintenanceAndUpdateFrequency>
                </gmd:MD_MaintenanceInformation>
              </gmd:resourceMaintenance>
              <gmd:graphicOverview>
                <gmd:MD_BrowseGraphic>
                  <gmd:fileName>
                    <gco:CharacterString><xsl:value-of select="/hdf5/browse/amplitude" /></gco:CharacterString>
                  </gmd:fileName>
                  <gmd:fileDescription>
                    <gco:CharacterString>browse image of the amplitude (including world and auxiliary file)</gco:CharacterString>
                  </gmd:fileDescription>
                  <gmd:fileType>
                    <gco:CharacterString>JPEG</gco:CharacterString>
                  </gmd:fileType>
                </gmd:MD_BrowseGraphic>
              </gmd:graphicOverview>
              <gmd:graphicOverview>
                <gmd:MD_BrowseGraphic>
                  <gmd:fileName>
                    <gco:CharacterString><xsl:value-of select="/hdf5/browse/kml_overlay" /></gco:CharacterString>
                  </gmd:fileName>
                  <gmd:fileDescription>
                    <gco:CharacterString>KML overlay image (PNG embedded into KML)</gco:CharacterString>
                  </gmd:fileDescription>
                  <gmd:fileType>
                    <gco:CharacterString>KMZ</gco:CharacterString>
                  </gmd:fileType>
                </gmd:MD_BrowseGraphic>
              </gmd:graphicOverview>
              <gmd:resourceConstraints>
                <gmd:MD_LegalConstraints>
                  <gmd:accessConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:accessConstraints>
                  <gmd:useConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:useConstraints>
                  <gmd:otherConstraints>
                    <gco:CharacterString>
Please identify that the data you have used was processed by the Alaska Satellite Facility. Additionally, the research agreements specify separate conditions by the Foreign Space Agencies on the use of their data.
                      
Data received from the Alaska Satellite Facility (ASF) can be used only under the following terms and conditions:
1. The data are for use for bona fide research purposes only. No commercial use is allowed of the data or any products derived there from.
2. The data will not be reproduced or distributed to any other parties, except that they may be shared among named members of a research team (co-investigators) and with other researchers who have signed a similar research agreement. The user is responsible for compliance with this condition for the data obtained from ASF. Furthermore, the user is responsible for compliance to these agreement terms by members of the research team with whom these data are shared.
3. The user will submit for publication in the open scientific literature results of research accomplished with the requested data, including derived data sets, and the algorithms and models used. Application demonstrations are not required to supply algorithms or models.
4. The user agrees to provide, if requested, a copy of such results including derived data sets, algorithms, models, and documentation, to the ASF for archive and distribution. Application demonstrations are not required to supply algorithms or models.
5. The user agrees to pay the marginal cost to ASF of filling my specific requests including reproducing and delivering the data.
6. The user also understands that a product which involved ASF data in its production can only be freely distributed by me if it is in such a form that the original backscatter values cannot be derived from it.
                    </gco:CharacterString>                
                  </gmd:otherConstraints>
                </gmd:MD_LegalConstraints>
              </gmd:resourceConstraints>
              <gmd:spatialRepresentationType>
                <gmd:MD_SpatialRepresentationTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_SpatialRepresentationTypeCode" codeListValue="grid">grid</gmd:MD_SpatialRepresentationTypeCode>
              </gmd:spatialRepresentationType>
              <gmd:language>
                <gco:CharacterString>eng</gco:CharacterString>
              </gmd:language>
              <gmd:characterSet>
                <gmd:MD_CharacterSetCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
              </gmd:characterSet>
              <gmd:topicCategory>
                <gmd:MD_TopicCategoryCode>geoscientificInformation</gmd:MD_TopicCategoryCode>
              </gmd:topicCategory>
              <gmd:environmentDescription>
                <gco:CharacterString>Data product generated in GeoTIFF format with ISO 19115 conformant metadata.</gco:CharacterString>
              </gmd:environmentDescription>
              <gmd:extent>
                <gmd:EX_Extent>
                  <gmd:description>
                    <gco:CharacterString>geographic and temporal extent of the terrain corrected image</gco:CharacterString>
                  </gmd:description>
                  <gmd:geographicElement>
                    <gmd:EX_GeographicBoundingBox id="imageBoundingBox">
                      <gmd:extentTypeCode>
                        <gco:Boolean>true</gco:Boolean>
                      </gmd:extentTypeCode>
                      <gmd:westBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/westBoundLongitude" /></gco:Decimal>
                      </gmd:westBoundLongitude>
                      <gmd:eastBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/eastBoundLongitude" /></gco:Decimal>
                      </gmd:eastBoundLongitude>
                      <gmd:southBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/southBoundLatitude" /></gco:Decimal>
                      </gmd:southBoundLatitude>
                      <gmd:northBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/northBoundLatitude" /></gco:Decimal>
                      </gmd:northBoundLatitude>
                    </gmd:EX_GeographicBoundingBox>
                  </gmd:geographicElement>
                  <gmd:temporalElement>
                    <gmd:EX_TemporalExtent id="imageTemporalExtent">
                      <gmd:extent>
                        <gml:TimePeriod gml:id="dataAcquisition">
                          <gml:description>begin and end time of data acquisition of input image</gml:description>
                          <gml:beginPosition><xsl:value-of select="/hdf5/metadata/input_image/start_datetime" /></gml:beginPosition>
                          <gml:endPosition><xsl:value-of select="/hdf5/metadata/input_image/end_datetime" /></gml:endPosition>
                        </gml:TimePeriod>
                      </gmd:extent>
                    </gmd:EX_TemporalExtent>
                  </gmd:temporalElement>
                </gmd:EX_Extent>
              </gmd:extent>
            </gmd:MD_DataIdentification>
          </gmd:identificationInfo>
          <gmd:identificationInfo>
            <gmd:MD_DataIdentification>
              <gmd:citation>
                <gmd:CI_Citation>
                  <gmd:title>
                    <gmx:FileName><xsl:value-of select="/hdf5/metadata/layover_shadow_mask/file" /></gmx:FileName>
                  </gmd:title>
                  <gmd:alternateTitle>
                    <gco:CharacterString>layover shadow mask</gco:CharacterString>
                  </gmd:alternateTitle>
                  <gmd:date>
                    <gmd:CI_Date>
                      <gmd:date>
                        <gco:DateTime><xsl:value-of select="/hdf5/metadata_creation" /></gco:DateTime>
                      </gmd:date>
                      <gmd:dateType>
                        <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_DateTypeCode"
                          codeListValue="creation">creation</gmd:CI_DateTypeCode>
                      </gmd:dateType>
                    </gmd:CI_Date>
                  </gmd:date>
                  <gmd:citedResponsibleParty>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:citedResponsibleParty>
                  <gmd:presentationForm>
                    <gmd:CI_PresentationFormCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_PresentationFormCode" codeListValue="documentDigital">documentDigital</gmd:CI_PresentationFormCode>
                  </gmd:presentationForm>
                </gmd:CI_Citation>
              </gmd:citation>
              <gmd:abstract>
                <gco:CharacterString>The layover shadow mask indicates which pixels in the terrain corrected image have been affected by layover and shadow.</gco:CharacterString>
              </gmd:abstract>
              <gmd:status>
                <gmd:MD_ProgressCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ProgressCode" codeListValue="completed">completed</gmd:MD_ProgressCode>
              </gmd:status>
              <gmd:resourceMaintenance>
                <gmd:MD_MaintenanceInformation>
                  <gmd:maintenanceAndUpdateFrequency>
                    <gmd:MD_MaintenanceFrequencyCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MaintenanceFrequencyCode" codeListValue="asNeeded">asNeeded</gmd:MD_MaintenanceFrequencyCode>
                  </gmd:maintenanceAndUpdateFrequency>
                </gmd:MD_MaintenanceInformation>
              </gmd:resourceMaintenance>
              <gmd:resourceConstraints>
                <gmd:MD_LegalConstraints>
                  <gmd:accessConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:accessConstraints>
                  <gmd:useConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:useConstraints>
                  <gmd:otherConstraints>
                    <gco:CharacterString>
                      Please identify that the data you have used was processed by the Alaska Satellite Facility. Additionally, the research agreements specify separate conditions by the Foreign Space Agencies on the use of their data.
                      
                      Data received from the Alaska Satellite Facility (ASF) can be used only under the following terms and conditions:
                      1. The data are for use for bona fide research purposes only. No commercial use is allowed of the data or any products derived there from.
                      2. The data will not be reproduced or distributed to any other parties, except that they may be shared among named members of a research team (co-investigators) and with other researchers who have signed a similar research agreement. The user is responsible for compliance with this condition for the data obtained from ASF. Furthermore, the user is responsible for compliance to these agreement terms by members of the research team with whom these data are shared.
                      3. The user will submit for publication in the open scientific literature results of research accomplished with the requested data, including derived data sets, and the algorithms and models used. Application demonstrations are not required to supply algorithms or models.
                      4. The user agrees to provide, if requested, a copy of such results including derived data sets, algorithms, models, and documentation, to the ASF for archive and distribution. Application demonstrations are not required to supply algorithms or models.
                      5. The user agrees to pay the marginal cost to ASF of filling my specific requests including reproducing and delivering the data.
                      6. The user also understands that a product which involved ASF data in its production can only be freely distributed by me if it is in such a form that the original backscatter values cannot be derived from it.
                    </gco:CharacterString>                
                  </gmd:otherConstraints>
                </gmd:MD_LegalConstraints>
              </gmd:resourceConstraints>
              <gmd:spatialRepresentationType>
                <gmd:MD_SpatialRepresentationTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_SpatialRepresentationTypeCode" codeListValue="grid">grid</gmd:MD_SpatialRepresentationTypeCode>
              </gmd:spatialRepresentationType>
              <gmd:language>
                <gco:CharacterString>eng</gco:CharacterString>
              </gmd:language>
              <gmd:characterSet>
                <gmd:MD_CharacterSetCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
              </gmd:characterSet>
              <gmd:topicCategory>
                <gmd:MD_TopicCategoryCode>geoscientificInformation</gmd:MD_TopicCategoryCode>
              </gmd:topicCategory>
              <gmd:environmentDescription>
                <gco:CharacterString>Data product generated in GeoTIFF format.</gco:CharacterString>
              </gmd:environmentDescription>
              <gmd:extent>
                <gmd:EX_Extent>
                  <gmd:description>
                    <gco:CharacterString>geographic extent of the layover shadow mask</gco:CharacterString>
                  </gmd:description>
                  <gmd:geographicElement>
                    <gmd:EX_GeographicBoundingBox id="maskBoundingBox">
                      <gmd:extentTypeCode>
                        <gco:Boolean>true</gco:Boolean>
                      </gmd:extentTypeCode>
                      <gmd:westBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/westBoundLongitude" /></gco:Decimal>
                      </gmd:westBoundLongitude>
                      <gmd:eastBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/eastBoundLongitude" /></gco:Decimal>
                      </gmd:eastBoundLongitude>
                      <gmd:southBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/southBoundLatitude" /></gco:Decimal>
                      </gmd:southBoundLatitude>
                      <gmd:northBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/northBoundLatitude" /></gco:Decimal>
                      </gmd:northBoundLatitude>
                    </gmd:EX_GeographicBoundingBox>
                  </gmd:geographicElement>
                </gmd:EX_Extent>
              </gmd:extent>
            </gmd:MD_DataIdentification>
          </gmd:identificationInfo>
          <gmd:identificationInfo>
            <gmd:MD_DataIdentification>
              <gmd:citation>
                <gmd:CI_Citation>
                  <gmd:title>
                    <gmx:FileName><xsl:value-of select="/hdf5/metadata/incidence_angle_map/file" /></gmx:FileName>
                  </gmd:title>
                  <gmd:alternateTitle>
                    <gco:CharacterString>incidence angle map</gco:CharacterString>
                  </gmd:alternateTitle>
                  <gmd:date>
                    <gmd:CI_Date>
                      <gmd:date>
                        <gco:DateTime><xsl:value-of select="/hdf5/metadata_creation" /></gco:DateTime>
                      </gmd:date>
                      <gmd:dateType>
                        <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_DateTypeCode"
                          codeListValue="creation">creation</gmd:CI_DateTypeCode>
                      </gmd:dateType>
                    </gmd:CI_Date>
                  </gmd:date>
                  <gmd:citedResponsibleParty>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:citedResponsibleParty>
                  <gmd:presentationForm>
                    <gmd:CI_PresentationFormCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_PresentationFormCode" codeListValue="documentDigital">documentDigital</gmd:CI_PresentationFormCode>
                  </gmd:presentationForm>
                </gmd:CI_Citation>
              </gmd:citation>
              <gmd:abstract>
                <gco:CharacterString>The incidence angle map represents the local incidene angle on a pixel by pixel basis.</gco:CharacterString>
              </gmd:abstract>
              <gmd:status>
                <gmd:MD_ProgressCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ProgressCode" codeListValue="completed">completed</gmd:MD_ProgressCode>
              </gmd:status>
              <gmd:resourceMaintenance>
                <gmd:MD_MaintenanceInformation>
                  <gmd:maintenanceAndUpdateFrequency>
                    <gmd:MD_MaintenanceFrequencyCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MaintenanceFrequencyCode" codeListValue="asNeeded">asNeeded</gmd:MD_MaintenanceFrequencyCode>
                  </gmd:maintenanceAndUpdateFrequency>
                </gmd:MD_MaintenanceInformation>
              </gmd:resourceMaintenance>
              <gmd:resourceConstraints>
                <gmd:MD_LegalConstraints>
                  <gmd:accessConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:accessConstraints>
                  <gmd:useConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:useConstraints>
                  <gmd:otherConstraints>
                    <gco:CharacterString>
                      Please identify that the data you have used was processed by the Alaska Satellite Facility. Additionally, the research agreements specify separate conditions by the Foreign Space Agencies on the use of their data.
                      
                      Data received from the Alaska Satellite Facility (ASF) can be used only under the following terms and conditions:
                      1. The data are for use for bona fide research purposes only. No commercial use is allowed of the data or any products derived there from.
                      2. The data will not be reproduced or distributed to any other parties, except that they may be shared among named members of a research team (co-investigators) and with other researchers who have signed a similar research agreement. The user is responsible for compliance with this condition for the data obtained from ASF. Furthermore, the user is responsible for compliance to these agreement terms by members of the research team with whom these data are shared.
                      3. The user will submit for publication in the open scientific literature results of research accomplished with the requested data, including derived data sets, and the algorithms and models used. Application demonstrations are not required to supply algorithms or models.
                      4. The user agrees to provide, if requested, a copy of such results including derived data sets, algorithms, models, and documentation, to the ASF for archive and distribution. Application demonstrations are not required to supply algorithms or models.
                      5. The user agrees to pay the marginal cost to ASF of filling my specific requests including reproducing and delivering the data.
                      6. The user also understands that a product which involved ASF data in its production can only be freely distributed by me if it is in such a form that the original backscatter values cannot be derived from it.
                    </gco:CharacterString>                
                  </gmd:otherConstraints>
                </gmd:MD_LegalConstraints>
              </gmd:resourceConstraints>
              <gmd:spatialRepresentationType>
                <gmd:MD_SpatialRepresentationTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_SpatialRepresentationTypeCode" codeListValue="grid">grid</gmd:MD_SpatialRepresentationTypeCode>
              </gmd:spatialRepresentationType>
              <gmd:language>
                <gco:CharacterString>eng</gco:CharacterString>
              </gmd:language>
              <gmd:characterSet>
                <gmd:MD_CharacterSetCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
              </gmd:characterSet>
              <gmd:topicCategory>
                <gmd:MD_TopicCategoryCode>geoscientificInformation</gmd:MD_TopicCategoryCode>
              </gmd:topicCategory>
              <gmd:environmentDescription>
                <gco:CharacterString>Data product generated in GeoTIFF format.</gco:CharacterString>
              </gmd:environmentDescription>
              <gmd:extent>
                <gmd:EX_Extent>
                  <gmd:description>
                    <gco:CharacterString>geographic extent of the incidence angle map</gco:CharacterString>
                  </gmd:description>
                  <gmd:geographicElement>
                    <gmd:EX_GeographicBoundingBox id="mapBoundingBox">
                      <gmd:extentTypeCode>
                        <gco:Boolean>true</gco:Boolean>
                      </gmd:extentTypeCode>
                      <gmd:westBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/westBoundLongitude" /></gco:Decimal>
                      </gmd:westBoundLongitude>
                      <gmd:eastBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/eastBoundLongitude" /></gco:Decimal>
                      </gmd:eastBoundLongitude>
                      <gmd:southBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/southBoundLatitude" /></gco:Decimal>
                      </gmd:southBoundLatitude>
                      <gmd:northBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/terrain_corrected_image/northBoundLatitude" /></gco:Decimal>
                      </gmd:northBoundLatitude>
                    </gmd:EX_GeographicBoundingBox>
                  </gmd:geographicElement>
                </gmd:EX_Extent>
              </gmd:extent>
            </gmd:MD_DataIdentification>
          </gmd:identificationInfo>
          <gmd:contentInfo>
            <gmd:MD_CoverageDescription>
              <gmd:attributeDescription>
                <gco:RecordType>terrain corrected product</gco:RecordType>
              </gmd:attributeDescription>
              <gmd:contentType>
                <gmd:MD_CoverageContentTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CoverageContentTypeCode" codeListValue="image">image</gmd:MD_CoverageContentTypeCode>
              </gmd:contentType>
              <gmd:dimension>
              <xsl:if test="/hdf5/statistics/terrain_corrected_HH">
                <gmi:MI_Band>
                  <gmd:descriptor>
                    <gco:CharacterString>HH band</gco:CharacterString>
                  </gmd:descriptor>
                  <gmd:maxValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HH/maximum_value" /></gco:Real>
                  </gmd:maxValue>
                  <gmd:minValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HH/minimum_value" /></gco:Real>
                  </gmd:minValue>
                  <gmd:meanValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HH/mean_value" /></gco:Real>
                  </gmd:meanValue>
                  <gmd:standardDeviation>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HH/standard_deviation" /></gco:Real>
                  </gmd:standardDeviation>
                  <gmi:transmittedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">horizontal</gmi:MI_PolarisationOrientationCode>
                  </gmi:transmittedPolarisation>
                  <gmi:detectedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">horizontal</gmi:MI_PolarisationOrientationCode>
                  </gmi:detectedPolarisation>
                  <eos:otherPropertyType>
                    <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
                  </eos:otherPropertyType>
                  <eos:otherProperty>
                    <gco:Record>
                      <eos:additionalAttributes>
                        <eos:EOS_AdditionalAttributes>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>percent valid values</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>percent of pixels in the image with valid values</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/terrain_corrected_HH/percent_valid_values" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                        </eos:EOS_AdditionalAttributes>
                      </eos:additionalAttributes>
                    </gco:Record>
                  </eos:otherProperty>
                </gmi:MI_Band>
              </xsl:if>
              <xsl:if test="/hdf5/statistics/terrain_corrected_HV">
                <gmi:MI_Band>
                  <gmd:descriptor>
                    <gco:CharacterString>HV band</gco:CharacterString>
                  </gmd:descriptor>
                  <gmd:maxValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HV/maximum_value" /></gco:Real></gmd:maxValue>
                  <gmd:minValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HV/minimum_value" /></gco:Real></gmd:minValue>
                  <gmd:meanValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HV/mean_value" /></gco:Real></gmd:meanValue>
                  <gmd:standardDeviation>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_HV/standard_deviation" /></gco:Real>
                  </gmd:standardDeviation>
                  <gmi:transmittedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">horizontal</gmi:MI_PolarisationOrientationCode>
                  </gmi:transmittedPolarisation>
                  <gmi:detectedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">vertical</gmi:MI_PolarisationOrientationCode>
                  </gmi:detectedPolarisation>
                  <eos:otherPropertyType>
                    <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
                  </eos:otherPropertyType>
                  <eos:otherProperty>
                    <gco:Record>
                      <eos:additionalAttributes>
                        <eos:EOS_AdditionalAttributes>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>percent valid values</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>percent of pixels in the image with valid values</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/terrain_corrected_HV/percent_valid_values" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                        </eos:EOS_AdditionalAttributes>
                      </eos:additionalAttributes>
                    </gco:Record>
                  </eos:otherProperty>
                </gmi:MI_Band>
              </xsl:if>
              <xsl:if test="/hdf5/statistics/terrain_corrected_VH">
                <gmi:MI_Band>
                  <gmd:descriptor>
                    <gco:CharacterString>VH band</gco:CharacterString>
                  </gmd:descriptor>
                  <gmd:maxValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VH/maximum_value" /></gco:Real>
                  </gmd:maxValue>
                  <gmd:minValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VH/minimum_value" /></gco:Real>
                  </gmd:minValue>
                  <gmd:meanValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VH/mean_value" /></gco:Real>
                  </gmd:meanValue>
                  <gmd:standardDeviation>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VH/standard_deviation" /></gco:Real>
                  </gmd:standardDeviation>
                  <gmi:transmittedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">vertical</gmi:MI_PolarisationOrientationCode>
                  </gmi:transmittedPolarisation>
                  <gmi:detectedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">horizontal</gmi:MI_PolarisationOrientationCode>
                  </gmi:detectedPolarisation>
                  <eos:otherPropertyType>
                    <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
                  </eos:otherPropertyType>
                  <eos:otherProperty>
                    <gco:Record>
                      <eos:additionalAttributes>
                        <eos:EOS_AdditionalAttributes>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>percent valid values</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>percent of pixels in the image with valid values</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/terrain_corrected_VH/percent_valid_values" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                        </eos:EOS_AdditionalAttributes>
                      </eos:additionalAttributes>
                    </gco:Record>
                  </eos:otherProperty>
                </gmi:MI_Band>
              </xsl:if>
              <xsl:if test="/hdf5/statistics/terrain_corrected_VV">
                <gmi:MI_Band>
                  <gmd:descriptor>
                    <gco:CharacterString>VV band</gco:CharacterString>
                  </gmd:descriptor>
                  <gmd:maxValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VV/maximum_value" /></gco:Real>
                  </gmd:maxValue>
                  <gmd:minValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VV/minimum_value" /></gco:Real>
                  </gmd:minValue>
                  <gmd:meanValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VV/mean_value" /></gco:Real>
                  </gmd:meanValue>
                  <gmd:standardDeviation>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/terrain_corrected_VV/standard_deviation" /></gco:Real>
                  </gmd:standardDeviation>
                  <gmi:transmittedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">vertical</gmi:MI_PolarisationOrientationCode>
                  </gmi:transmittedPolarisation>
                  <gmi:detectedPolarisation>
                    <gmi:MI_PolarisationOrientationCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MI_PolarizationOrientationCode" codeListValue="horizontal">vertical</gmi:MI_PolarisationOrientationCode>
                  </gmi:detectedPolarisation>
                  <eos:otherPropertyType>
                    <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
                  </eos:otherPropertyType>
                  <eos:otherProperty>
                    <gco:Record>
                      <eos:additionalAttributes>
                        <eos:EOS_AdditionalAttributes>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>percent valid values</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>percent of pixels in the image with valid values</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/terrain_corrected_VV/percent_valid_values" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                        </eos:EOS_AdditionalAttributes>
                      </eos:additionalAttributes>
                    </gco:Record>
                  </eos:otherProperty>
                </gmi:MI_Band>
              </xsl:if>
              </gmd:dimension>
            </gmd:MD_CoverageDescription>
          </gmd:contentInfo>
          <gmd:contentInfo>
            <gmd:MD_CoverageDescription>
              <gmd:attributeDescription>
                <gco:RecordType>layover shadow mask</gco:RecordType>
              </gmd:attributeDescription>
              <gmd:contentType>
                <gmd:MD_CoverageContentTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CoverageContentTypeCode" codeListValue="image">image</gmd:MD_CoverageContentTypeCode>
              </gmd:contentType>
              <gmd:dimension>
                <gmi:MI_Band>
                  <eos:otherPropertyType>
                    <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
                  </eos:otherPropertyType>
                  <eos:otherProperty>
                    <gco:Record>
                      <eos:additionalAttributes>
                        <eos:EOS_AdditionalAttributes>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>no layover shadow</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pixels with neither layover nor shadow</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/layover_shadow_mask/percent_no_layover_shadow" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>true layover</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pixels were slope angle is greater than look angle</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/layover_shadow_mask/percent_true_layover" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>layover</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pixels in areas affected by layover</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/layover_shadow_mask/percent_layover" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>true shadow</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pixels where opposite of slope angle is greater than look angle</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/layover_shadow_mask/percent_true_shadow" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>shadow</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pixels in areas affected by shadow</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/layover_shadow_mask/percent_shadow" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                        </eos:EOS_AdditionalAttributes>
                      </eos:additionalAttributes>
                    </gco:Record>
                  </eos:otherProperty>
                </gmi:MI_Band>
              </gmd:dimension>
            </gmd:MD_CoverageDescription>
          </gmd:contentInfo>
          <gmd:contentInfo>
            <gmd:MD_CoverageDescription>
              <gmd:attributeDescription>
                <gco:RecordType>incidence angle map</gco:RecordType>
              </gmd:attributeDescription>
              <gmd:contentType>
                <gmd:MD_CoverageContentTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CoverageContentTypeCode" codeListValue="image">image</gmd:MD_CoverageContentTypeCode>
              </gmd:contentType>
              <gmd:dimension>
                <gmi:MI_Band>
                  <gmd:maxValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/incidence_angle_map/maximum_value" /></gco:Real>
                  </gmd:maxValue>
                  <gmd:minValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/incidence_angle_map/minimum_value" /></gco:Real>
                  </gmd:minValue>
                  <gmd:meanValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/incidence_angle_map/mean_value" /></gco:Real>
                  </gmd:meanValue>
                  <gmd:standardDeviation>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/incidence_angle_map/standard_deviation" /></gco:Real>
                  </gmd:standardDeviation>
                  <eos:otherPropertyType>
                    <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
                  </eos:otherPropertyType>
                  <eos:otherProperty>
                    <gco:Record>
                      <eos:additionalAttributes>
                        <eos:EOS_AdditionalAttributes>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="contentInformation">contentInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>percent valid values</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>percent of pixels in the image with valid values</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>percent</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/statistics/incidence_angle_map/percent_valid_values" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                        </eos:EOS_AdditionalAttributes>
                      </eos:additionalAttributes>
                    </gco:Record>
                  </eos:otherProperty>
                </gmi:MI_Band>
              </gmd:dimension>
            </gmd:MD_CoverageDescription>
          </gmd:contentInfo>
          <gmd:distributionInfo>
            <gmd:MD_Distribution>
              <gmd:distributionFormat>
                <gmd:MD_Format>
                  <gmd:name>
                    <gco:CharacterString>GeoTIFF</gco:CharacterString>
                  </gmd:name>
                  <gmd:version>
                    <gco:CharacterString>1.2.2</gco:CharacterString>
                  </gmd:version>
                </gmd:MD_Format>
              </gmd:distributionFormat>
              <gmd:distributor>
                <gmd:MD_Distributor>
                  <gmd:distributorContact>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:contactInfo xlink:href="#ASFcontactInfo" />
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="distributor">distributor</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:distributorContact>
                  <gmd:distributionOrderProcess>
                    <gmd:MD_StandardOrderProcess>
                      <gmd:fees>
                        <gco:CharacterString>free</gco:CharacterString>
                      </gmd:fees>
                    </gmd:MD_StandardOrderProcess>
                  </gmd:distributionOrderProcess>
                </gmd:MD_Distributor>
              </gmd:distributor>
            </gmd:MD_Distribution>
          </gmd:distributionInfo>
          <gmd:dataQualityInfo>
            <gmd:DQ_DataQuality>
              <gmd:scope>
                <gmd:DQ_Scope>
                  <gmd:level>
                    <gmd:MD_ScopeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
                  </gmd:level>
                </gmd:DQ_Scope>
              </gmd:scope>
              <gmd:report>
                <gmd:DQ_QuantitativeAttributeAccuracy>
                  <gmd:nameOfMeasure>
                    <gco:CharacterString>number of patches used to coregister</gco:CharacterString>
                  </gmd:nameOfMeasure>
                  <gmd:evaluationMethodType>
                    <gmd:DQ_EvaluationMethodTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#DQ_EvaluationMethodTypeCode" codeListValue="directInternal">directInternal</gmd:DQ_EvaluationMethodTypeCode>
                  </gmd:evaluationMethodType>
                  <gmd:result>
                    <gmd:DQ_QuantitativeResult>
                      <gmd:valueUnit gco:nilReason="inapplicable"/>
                      <gmd:value>
                        <gco:Record xsi:type="gco:Integer_PropertyType">
                          <gco:Integer><xsl:value-of select="/hdf5/metadata/terrain_correction/patches_attempted" /></gco:Integer>
                        </gco:Record>
                      </gmd:value>
                    </gmd:DQ_QuantitativeResult>
                  </gmd:result>
                </gmd:DQ_QuantitativeAttributeAccuracy>
              </gmd:report>
              <gmd:report>
                <gmd:DQ_QuantitativeAttributeAccuracy>
                  <gmd:nameOfMeasure>
                    <gco:CharacterString>number of patches successfully coregister</gco:CharacterString>
                  </gmd:nameOfMeasure>
                  <gmd:evaluationMethodType>
                    <gmd:DQ_EvaluationMethodTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#DQ_EvaluationMethodTypeCode" codeListValue="directInternal">directInternal</gmd:DQ_EvaluationMethodTypeCode>
                  </gmd:evaluationMethodType>
                  <gmd:result>
                    <gmd:DQ_QuantitativeResult>
                      <gmd:valueUnit gco:nilReason="inapplicable"/>
                      <gmd:value>
                        <gco:Record xsi:type="gco:Integer_PropertyType">
                          <gco:Integer><xsl:value-of select="/hdf5/metadata/terrain_correction/patches_accepted" /></gco:Integer>
                        </gco:Record>
                      </gmd:value>
                    </gmd:DQ_QuantitativeResult>
                  </gmd:result>
                </gmd:DQ_QuantitativeAttributeAccuracy>
              </gmd:report>
              <gmd:report>
                <gmd:DQ_QuantitativeAttributeAccuracy>
                  <gmd:nameOfMeasure>
                    <gco:CharacterString>coregistration success flag</gco:CharacterString>
                  </gmd:nameOfMeasure>
                  <gmd:evaluationMethodType>
                    <gmd:DQ_EvaluationMethodTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#DQ_EvaluationMethodTypeCode" codeListValue="directInternal">directInternal</gmd:DQ_EvaluationMethodTypeCode>
                  </gmd:evaluationMethodType>
                  <gmd:result>
                    <gmd:DQ_QuantitativeResult>
                      <gmd:valueUnit gco:nilReason="inapplicable"/>
                      <gmd:value>
                        <gco:Record xsi:type="gco:CharacterString_PropertyType">
                          <gco:CharacterString><xsl:value-of select="/hdf5/metadata/terrain_correction/coregistration_success" /></gco:CharacterString>
                        </gco:Record>
                      </gmd:value>
                    </gmd:DQ_QuantitativeResult>
                  </gmd:result>
                </gmd:DQ_QuantitativeAttributeAccuracy>
              </gmd:report>
              <gmd:report>
                <gmd:DQ_QuantitativeAttributeAccuracy>
                  <gmd:nameOfMeasure>
                    <gco:CharacterString>coregistration range offset</gco:CharacterString>
                  </gmd:nameOfMeasure>
                  <gmd:evaluationMethodType>
                    <gmd:DQ_EvaluationMethodTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#DQ_EvaluationMethodTypeCode" codeListValue="directInternal">directInternal</gmd:DQ_EvaluationMethodTypeCode>
                  </gmd:evaluationMethodType>
                  <gmd:result>
                    <gmd:DQ_QuantitativeResult>
                      <gmd:valueUnit xlink:href="http://www.opengis.net/def/uom/OGC/1.0/GridSpacing" />
                      <gmd:value>
                        <gco:Record xsi:type="gco:Real_PropertyType">
                          <gco:Real><xsl:value-of select="/hdf5/metadata/terrain_correction/offset_x" /></gco:Real>
                        </gco:Record>
                      </gmd:value>
                    </gmd:DQ_QuantitativeResult>
                  </gmd:result>
                </gmd:DQ_QuantitativeAttributeAccuracy>
              </gmd:report>
              <gmd:report>
                <gmd:DQ_QuantitativeAttributeAccuracy>
                  <gmd:nameOfMeasure>
                    <gco:CharacterString>coregistration azimuth offset</gco:CharacterString>
                  </gmd:nameOfMeasure>
                  <gmd:evaluationMethodType>
                    <gmd:DQ_EvaluationMethodTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#DQ_EvaluationMethodTypeCode" codeListValue="directInternal">directInternal</gmd:DQ_EvaluationMethodTypeCode>
                  </gmd:evaluationMethodType>
                  <gmd:result>
                    <gmd:DQ_QuantitativeResult>
                      <gmd:valueUnit xlink:href="http://www.opengis.net/def/uom/OGC/1.0/GridSpacing" />
                      <gmd:value>
                        <gco:Record xsi:type="gco:Real_PropertyType">
                          <gco:Real><xsl:value-of select="/hdf5/metadata/terrain_correction/offset_y" /></gco:Real>
                        </gco:Record>
                      </gmd:value>
                    </gmd:DQ_QuantitativeResult>
                  </gmd:result>
                </gmd:DQ_QuantitativeAttributeAccuracy>
              </gmd:report>
              <gmd:report>
                <gmd:DQ_QuantitativeAttributeAccuracy>
                  <gmd:nameOfMeasure>
                    <gco:CharacterString>final model fit standard deviation in range direction</gco:CharacterString>
                  </gmd:nameOfMeasure>
                  <gmd:evaluationMethodType>
                    <gmd:DQ_EvaluationMethodTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#DQ_EvaluationMethodTypeCode" codeListValue="directInternal">directInternal</gmd:DQ_EvaluationMethodTypeCode>
                  </gmd:evaluationMethodType>
                  <gmd:result>
                    <gmd:DQ_QuantitativeResult>
                      <gmd:valueUnit xlink:href="http://www.opengis.net/def/uom/OGC/1.0/GridSpacing" />
                      <gmd:value>
                        <gco:Record xsi:type="gco:Real_PropertyType">
                          <gco:Real><xsl:value-of select="/hdf5/metadata/terrain_correction/residual_range_offset_stddev" /></gco:Real>
                        </gco:Record>
                      </gmd:value>
                    </gmd:DQ_QuantitativeResult>
                  </gmd:result>
                </gmd:DQ_QuantitativeAttributeAccuracy>
              </gmd:report>
              <gmd:report>
                <gmd:DQ_QuantitativeAttributeAccuracy>
                  <gmd:nameOfMeasure>
                    <gco:CharacterString>final model fit standard deviation in azimuth direction</gco:CharacterString>
                  </gmd:nameOfMeasure>
                  <gmd:evaluationMethodType>
                    <gmd:DQ_EvaluationMethodTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#DQ_EvaluationMethodTypeCode" codeListValue="directInternal">directInternal</gmd:DQ_EvaluationMethodTypeCode>
                  </gmd:evaluationMethodType>
                  <gmd:result>
                    <gmd:DQ_QuantitativeResult>
                      <gmd:valueUnit xlink:href="http://www.opengis.net/def/uom/OGC/1.0/GridSpacing" />
                      <gmd:value>
                        <gco:Record xsi:type="gco:Real_PropertyType">
                          <gco:Real><xsl:value-of select="/hdf5/metadata/terrain_correction/residual_azimuth_offset_stddev" /></gco:Real>
                        </gco:Record>
                      </gmd:value>
                    </gmd:DQ_QuantitativeResult>
                  </gmd:result>
                </gmd:DQ_QuantitativeAttributeAccuracy>
              </gmd:report>
              <gmd:lineage>
                <gmd:LI_Lineage>
                  <gmd:statement>
                  <xsl:if test="/hdf5/metadata/input_image/platform='ALOS'">
                    <gco:CharacterString>Processing of a standard CEOS frame from single look complex data to a terrain corrected geocoded product</gco:CharacterString>
                  </xsl:if>
                  <xsl:if test="/hdf5/metadata/input_image/platform='ERS-1' or
                                /hdf5/metadata/input_image/platform='ERS-2'">
                    <gco:CharacterString>Processing of a standard CEOS frame from raw data to a terrain corrected geocoded product</gco:CharacterString>              
                  </xsl:if>
                  <xsl:if test="/hdf5/metadata/input_image/platform='Sentinel-1A' or
                                /hdf5/metadata/input_image/platform='Sentinel-1B'">
                    <gco:CharacterString>Processing of a SAFE format data from single look complex data to a terrain corrected geocoded product</gco:CharacterString>
                  </xsl:if>
                  </gmd:statement>
                  <gmd:processStep>
                    <gmi:LE_ProcessStep>
                      <gmd:description>
                      <xsl:if test="/hdf5/metadata/input_image/platform='ALOS'">
                        <gco:CharacterString>Conversion of single look complex data from CEOS format into GAMMA internal format</gco:CharacterString>                        
                      </xsl:if>
                      <xsl:if test="/hdf5/metadata/input_image/platform='ERS-1' or
                                    /hdf5/metadata/input_image/platform='ERS-2'">
                        <gco:CharacterString>Conversion of raw data from CEOS format into GAMMA internal format</gco:CharacterString>                        
                      </xsl:if>
                      <xsl:if test="/hdf5/metadata/input_image/platform='Sentinel-1A' or
                                    /hdf5/metadata/input_image/platform='Sentinel-1B'">
                        <gco:CharacterString>Conversion of raw data from SAFE format into GAMMA internal format</gco:CharacterString>                        
                      </xsl:if>
                      </gmd:description>
                      <gmd:dateTime>
                        <gco:DateTime><xsl:value-of select="/hdf5/processing/data_ingest" /></gco:DateTime>
                      </gmd:dateTime>
                      <gmd:processor>
                        <gmd:CI_ResponsibleParty>
                          <gmd:organisationName>
                            <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                          </gmd:organisationName>
                          <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                          <gmd:role>
                            <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="processor">processor</gmd:CI_RoleCode>
                          </gmd:role>
                        </gmd:CI_ResponsibleParty>
                      </gmd:processor>
                      <gmd:source>
                        <gmd:LI_Source>
                          <gmd:description>
                          <xsl:if test="/hdf5/metadata/input_image/platform='ALOS'">
                            <gco:CharacterString>Single look complex image - <xsl:value-of select="/hdf5/metadata/input_image/file" /></gco:CharacterString>                                                      </xsl:if>
                          <xsl:if test="/hdf5/metadata/input_image/platform='ERS-1' or
                                        /hdf5/metadata/input_image/platform='ERS-2'">
                            <gco:CharacterString>Raw image - <xsl:value-of select="/hdf5/metadata/input_image/file" /></gco:CharacterString>                                                                      </xsl:if>
                          <xsl:if test="/hdf5/metadata/input_image/platform='Sentinel-1A' or
                                        /hdf5/metadata/input_image/platform='Sentinel-1B'">
                            <gco:CharacterString>Single look complex image - <xsl:value-of select="/hdf5/metadata/input_image/file" /></gco:CharacterString>                                                      </xsl:if>
                          </gmd:description>
                        </gmd:LI_Source>
                      </gmd:source>
                      <gmi:processingInformation>
                        <gmi:LE_Processing>
                          <gmi:identifier>
                            <gmd:MD_Identifier>
                              <gmd:code>
                                <gco:CharacterString>GAMMA data ingest</gco:CharacterString>
                              </gmd:code>
                            </gmd:MD_Identifier>
                          </gmi:identifier>
                          <gmi:softwareReference>
                            <gmd:CI_Citation>
                              <gmd:title>
                              <xsl:if test="/hdf5/metadata/input_image/platform='ALOS'">
                                <gco:CharacterString>ASF_GEO_proc_ALOS_utm</gco:CharacterString>                                
                              </xsl:if>
                              <xsl:if test="/hdf5/metadata/input_image/platform='ERS-1' or
                                            /hdf5/metadata/input_image/platform='ERS-2'">
                                <gco:CharacterString>ASF_GEO_proc_legacy_utm</gco:CharacterString>
                              </xsl:if>
                              </gmd:title>
                              <gmd:date gco:nilReason="inapplicable"/>
                              <gmd:edition>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/software" /></gco:CharacterString>
                              </gmd:edition>
                              <gmd:citedResponsibleParty>
                                <gmd:CI_ResponsibleParty>
                                  <gmd:organisationName>
                                    <gco:CharacterString>GAMMA Remote Sensing and Consulting AG</gco:CharacterString>
                                  </gmd:organisationName>
                                  <gmd:role>
                                    <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                                  </gmd:role>
                                </gmd:CI_ResponsibleParty>
                              </gmd:citedResponsibleParty>
                            </gmd:CI_Citation>
                          </gmi:softwareReference>
                          <gmi:procedureDescription>
                            <gco:CharacterString>processing with gap_rtc script (version <xsl:value-of select="/hdf5/metadata/terrain_correction/gap_rtc_version" />)</gco:CharacterString>
                          </gmi:procedureDescription>
                        </gmi:LE_Processing>
                      </gmi:processingInformation>
                      <gmi:output>
                        <gmi:LE_Source>
                          <gmd:description>
                            <gco:CharacterString>Single look complex image in GAMMA internal format</gco:CharacterString>
                          </gmd:description>
                        </gmi:LE_Source>
                      </gmi:output>
                    </gmi:LE_ProcessStep>
                  </gmd:processStep>
                <xsl:if test="/hdf5/processing/simulate_sar">
                  <gmd:processStep>
                    <gmi:LE_ProcessStep>
                      <gmd:description>
                        <gco:CharacterString>Generate initial geocoding lookup table and simulate SAR image from DEM</gco:CharacterString>
                      </gmd:description>
                      <gmd:dateTime>
                        <gco:DateTime><xsl:value-of select="/hdf5/processing/simulate_sar" /></gco:DateTime>
                      </gmd:dateTime>
                      <gmd:processor>
                        <gmd:CI_ResponsibleParty>
                          <gmd:organisationName>
                            <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                          </gmd:organisationName>
                          <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                          <gmd:role>
                            <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="processor">processor</gmd:CI_RoleCode>
                          </gmd:role>
                        </gmd:CI_ResponsibleParty>
                      </gmd:processor>
                      <gmd:source>
                        <gmd:LI_Source>
                          <gmd:description>
                            <gco:CharacterString>Single look complex ingested into GAMMA internal format</gco:CharacterString>
                          </gmd:description>
                        </gmd:LI_Source>
                      </gmd:source>
                      <gmi:processingInformation>
                        <gmi:LE_Processing>
                          <gmi:identifier>
                            <gmd:MD_Identifier>
                              <gmd:code>
                                <gco:CharacterString>GAMMA terrain correction</gco:CharacterString>
                              </gmd:code>
                            </gmd:MD_Identifier>
                          </gmi:identifier>
                          <gmi:softwareReference>
                            <gmd:CI_Citation>
                              <gmd:title>
                                <gco:CharacterString>mk_geo_radcal, mode: 0</gco:CharacterString>
                              </gmd:title>
                              <gmd:date gco:nilReason="inapplicable"/>
                              <gmd:edition>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/software" /></gco:CharacterString>
                              </gmd:edition>
                              <gmd:citedResponsibleParty>
                                <gmd:CI_ResponsibleParty>
                                  <gmd:organisationName>
                                    <gco:CharacterString>GAMMA Remote Sensing and Consulting AG</gco:CharacterString>
                                  </gmd:organisationName>
                                  <gmd:role>
                                    <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                                  </gmd:role>
                                </gmd:CI_ResponsibleParty>
                              </gmd:citedResponsibleParty>
                            </gmd:CI_Citation>
                          </gmi:softwareReference>
                          <gmi:procedureDescription>
                            <gco:CharacterString>processing with gap_rtc script (version <xsl:value-of select="/hdf5/metadata/terrain_correction/gap_rtc_version" />)</gco:CharacterString>
                          </gmi:procedureDescription>
                        </gmi:LE_Processing>
                      </gmi:processingInformation>
                      <gmi:output>
                        <gmi:LE_Source>
                          <gmd:description>
                            <gco:CharacterString>simulated SAR image</gco:CharacterString>
                          </gmd:description>
                        </gmi:LE_Source>
                      </gmi:output>
                    </gmi:LE_ProcessStep>
                  </gmd:processStep>
                </xsl:if>
                <xsl:if test="/hdf5/processing/initial_offset">
                  <gmd:processStep>
                    <gmi:LE_ProcessStep>
                      <gmd:description>
                        <gco:CharacterString>Estimate initial offset between the actual and simulated SAR images and refine the lookup table</gco:CharacterString>
                      </gmd:description>
                      <gmd:dateTime>
                        <gco:DateTime><xsl:value-of select="/hdf5/processing/initial_offset" /></gco:DateTime>
                      </gmd:dateTime>
                      <gmd:processor>
                        <gmd:CI_ResponsibleParty>
                          <gmd:organisationName>
                            <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                          </gmd:organisationName>
                          <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                          <gmd:role>
                            <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="processor">processor</gmd:CI_RoleCode>
                          </gmd:role>
                        </gmd:CI_ResponsibleParty>
                      </gmd:processor>
                      <gmd:source>
                        <gmd:LI_Source>
                          <gmd:description>
                            <gco:CharacterString>Actual and simulated SAR images</gco:CharacterString>
                          </gmd:description>
                        </gmd:LI_Source>
                      </gmd:source>
                      <gmi:processingInformation>
                        <gmi:LE_Processing>
                          <gmi:identifier>
                            <gmd:MD_Identifier>
                              <gmd:code>
                                <gco:CharacterString>GAMMA terrain correction</gco:CharacterString>
                              </gmd:code>
                            </gmd:MD_Identifier>
                          </gmi:identifier>
                          <gmi:softwareReference>
                            <gmd:CI_Citation>
                              <gmd:title>
                                <gco:CharacterString>mk_geo_radcal, mode: 1</gco:CharacterString>
                              </gmd:title>
                              <gmd:date gco:nilReason="inapplicable"/>
                              <gmd:edition>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/software" /></gco:CharacterString>
                              </gmd:edition>
                              <gmd:citedResponsibleParty>
                                <gmd:CI_ResponsibleParty>
                                  <gmd:organisationName>
                                    <gco:CharacterString>GAMMA Remote Sensing and Consulting AG</gco:CharacterString>
                                  </gmd:organisationName>
                                  <gmd:role>
                                    <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                                  </gmd:role>
                                </gmd:CI_ResponsibleParty>
                              </gmd:citedResponsibleParty>
                            </gmd:CI_Citation>
                          </gmi:softwareReference>
                          <gmi:procedureDescription>
                            <gco:CharacterString>processing with gap_rtc script (version <xsl:value-of select="/hdf5/metadata/terrain_correction/gap_rtc_version" />)</gco:CharacterString>
                          </gmi:procedureDescription>
                        </gmi:LE_Processing>
                      </gmi:processingInformation>
                      <gmi:output>
                        <gmi:LE_Source>
                          <gmd:description>
                            <gco:CharacterString>Initial offset between actual and simulated SAR images</gco:CharacterString>
                          </gmd:description>
                        </gmi:LE_Source>
                      </gmi:output>
                    </gmi:LE_ProcessStep>
                  </gmd:processStep>
                </xsl:if>
                <xsl:if test="/hdf5/processing/refined_offset">
                  <gmd:processStep>
                    <gmi:LE_ProcessStep>
                      <gmd:description>
                        <gco:CharacterString>Estimate offsets between the SAR and simulated image and calculate the polynomial offset model</gco:CharacterString>
                      </gmd:description>
                      <gmd:dateTime>
                        <gco:DateTime><xsl:value-of select="/hdf5/processing/refined_offset" /></gco:DateTime>
                      </gmd:dateTime>
                      <gmd:processor>
                        <gmd:CI_ResponsibleParty>
                          <gmd:organisationName>
                            <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                          </gmd:organisationName>
                          <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                          <gmd:role>
                            <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="processor">processor</gmd:CI_RoleCode>
                          </gmd:role>
                        </gmd:CI_ResponsibleParty>
                      </gmd:processor>
                      <gmd:source>
                        <gmd:LI_Source>
                          <gmd:description>
                            <gco:CharacterString>Actual and simulated SAR images</gco:CharacterString>
                          </gmd:description>
                        </gmd:LI_Source>
                      </gmd:source>
                      <gmi:processingInformation>
                        <gmi:LE_Processing>
                          <gmi:identifier>
                            <gmd:MD_Identifier>
                              <gmd:code>
                                <gco:CharacterString>GAMMA terrain correction</gco:CharacterString>
                              </gmd:code>
                            </gmd:MD_Identifier>
                          </gmi:identifier>
                          <gmi:softwareReference>
                            <gmd:CI_Citation>
                              <gmd:title>
                                <gco:CharacterString>mk_geo_radcal, mode: 2</gco:CharacterString>
                              </gmd:title>
                              <gmd:date gco:nilReason="inapplicable"/>
                              <gmd:edition>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/software" /></gco:CharacterString>
                              </gmd:edition>
                              <gmd:citedResponsibleParty>
                                <gmd:CI_ResponsibleParty>
                                  <gmd:organisationName>
                                    <gco:CharacterString>GAMMA Remote Sensing and Consulting AG</gco:CharacterString>
                                  </gmd:organisationName>
                                  <gmd:role>
                                    <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                                  </gmd:role>
                                </gmd:CI_ResponsibleParty>
                              </gmd:citedResponsibleParty>
                            </gmd:CI_Citation>
                          </gmi:softwareReference>
                          <gmi:procedureDescription>
                            <gco:CharacterString>processing with gap_rtc script (version <xsl:value-of select="/hdf5/metadata/terrain_correction/gap_rtc_version" />)</gco:CharacterString>
                          </gmi:procedureDescription>
                        </gmi:LE_Processing>
                      </gmi:processingInformation>
                      <gmi:output>
                        <gmi:LE_Source>
                          <gmd:description>
                            <gco:CharacterString>Refined offset between actual and simulated images</gco:CharacterString>
                          </gmd:description>
                        </gmi:LE_Source>
                      </gmi:output>
                    </gmi:LE_ProcessStep>
                  </gmd:processStep>
                </xsl:if>
                <xsl:if test="/hdf5/processing/terrain_correction">
                  <gmd:processStep>
                    <gmi:LE_ProcessStep>
                      <gmd:description>
                        <gco:CharacterString>Update lookup table, generate terrain geocoded image, perform pixel area correction and generate GEOTIFF output. Calculate DEM in SAR range-doppler coordinates.</gco:CharacterString>
                      </gmd:description>
                      <gmd:dateTime>
                        <gco:DateTime><xsl:value-of select="/hdf5/processing/terrain_correction" /></gco:DateTime>
                      </gmd:dateTime>
                      <gmd:processor>
                        <gmd:CI_ResponsibleParty>
                          <gmd:organisationName>
                            <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
                          </gmd:organisationName>
                          <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
                          <gmd:role>
                            <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="processor">processor</gmd:CI_RoleCode>
                          </gmd:role>
                        </gmd:CI_ResponsibleParty>
                      </gmd:processor>
                      <gmd:source>
                        <gmd:LI_Source>
                          <gmd:description>
                            <gco:CharacterString>SAR image and resampled digital elevation model</gco:CharacterString>
                          </gmd:description>
                        </gmd:LI_Source>
                      </gmd:source>
                      <gmi:processingInformation>
                        <gmi:LE_Processing>
                          <gmi:identifier>
                            <gmd:MD_Identifier>
                              <gmd:code>
                                <gco:CharacterString>GAMMA terrain correction</gco:CharacterString>
                              </gmd:code>
                            </gmd:MD_Identifier>
                          </gmi:identifier>
                          <gmi:softwareReference>
                            <gmd:CI_Citation>
                              <gmd:title>
                                <gco:CharacterString>mk_geo_radcal, mode: 3</gco:CharacterString>
                              </gmd:title>
                              <gmd:date gco:nilReason="inapplicable"/>
                              <gmd:edition>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/terrain_corrected_image/software" /></gco:CharacterString>
                              </gmd:edition>
                              <gmd:citedResponsibleParty>
                                <gmd:CI_ResponsibleParty>
                                  <gmd:organisationName>
                                    <gco:CharacterString>GAMMA Remote Sensing and Consulting AG</gco:CharacterString>
                                  </gmd:organisationName>
                                  <gmd:role>
                                    <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:CI_RoleCode" codeListValue="originator">originator</gmd:CI_RoleCode>
                                  </gmd:role>
                                </gmd:CI_ResponsibleParty>
                              </gmd:citedResponsibleParty>
                            </gmd:CI_Citation>
                          </gmi:softwareReference>
                          <gmi:procedureDescription>
                            <gco:CharacterString>processing with gap_rtc script (version <xsl:value-of select="/hdf5/metadata/terrain_correction/gap_rtc_version" />)</gco:CharacterString>
                          </gmi:procedureDescription>
                        </gmi:LE_Processing>
                      </gmi:processingInformation>
                      <gmi:output>
                        <gmi:LE_Source>
                          <gmd:description>
                            <gco:CharacterString>Terrain corrected image - <xsl:value-of select="/hdf5/metadata/terrain_corrected_image/file" /></gco:CharacterString>
                          </gmd:description>
                        </gmi:LE_Source>
                      </gmi:output>
                    </gmi:LE_ProcessStep>
                  </gmd:processStep>
                </xsl:if>
                  <gmd:source>
                    <gmd:LI_Source>
                      <gmd:description>
                        <gco:CharacterString>Single look complex - <xsl:value-of select="/hdf5/metadata/input_image/file" /></gco:CharacterString>
                      </gmd:description>
                    </gmd:LI_Source>
                  </gmd:source>
                </gmd:LI_Lineage>
              </gmd:lineage>
            </gmd:DQ_DataQuality>
          </gmd:dataQualityInfo>
          <gmd:metadataMaintenance>
            <gmd:MD_MaintenanceInformation>
              <gmd:maintenanceAndUpdateFrequency>
                <gmd:MD_MaintenanceFrequencyCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MaintenanceFrequencyCode" codeListValue="asNeeded">asNeeded</gmd:MD_MaintenanceFrequencyCode>
              </gmd:maintenanceAndUpdateFrequency>
            </gmd:MD_MaintenanceInformation>
          </gmd:metadataMaintenance>
          <gmi:acquisitionInformation>
            <gmi:MI_AcquisitionInformation>
              <gmi:instrument>
                <gmi:MI_Instrument id="sarInstrument">
                  <gmi:identifier>
                    <gmd:MD_Identifier>
                      <gmd:code>
                        <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/sensor" /></gco:CharacterString>
                      </gmd:code>
                    </gmd:MD_Identifier>
                  </gmi:identifier>
                  <gmi:type>
                  <xsl:if test="/hdf5/metadata/input_image/sensor='PALSAR'">
                    <gco:CharacterString>Phased Array L-band Synthetic Aperture Radar</gco:CharacterString>
                  </xsl:if>
                  <xsl:if test="/hdf5/metadata/input_image/sensor='SAR'">
                    <gco:CharacterString>Synthetic Aperture Radar</gco:CharacterString>
                  </xsl:if>
                  </gmi:type>
                  <gmi:mountedOn xlink:href="#sarPlatform" />
                </gmi:MI_Instrument>
              </gmi:instrument>
              <gmi:platform>
                <eos:EOS_Platform id="sarPlatform">
                  <gmi:identifier>
                    <gmd:MD_Identifier>
                      <gmd:code>
                        <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/platform" /></gco:CharacterString>
                      </gmd:code>
                    </gmd:MD_Identifier>
                  </gmi:identifier>
                  <gmi:description>
                  <xsl:if test="/hdf5/metadata/input_image/platform='ALOS'">
                    <gco:CharacterString>The Advanced Land Observing Satellite (ALOS) had been developed to contribute to the fields of mapping, precise regional land coverage observation, disaster monitoring, and resource surveying.</gco:CharacterString>
                  </xsl:if>
                  <xsl:if test="/hdf5/metadata/input_image/platform='ERS-1'">
                    <gco:CharacterString>The European Remote Sensing satellite ERS-1 carried a comprehensive payload including an imaging synthetic aperture radar, a radar altimeter and other powerful instruments to measure ocean surface temperature and winds at sea.</gco:CharacterString>
                  </xsl:if>
                  <xsl:if test="/hdf5/metadata/input_image/platform='ERS-2'">
                    <gco:CharacterString>The European Remote Sensing satellite ERS-2 carried a comprehensive payload including an imaging synthetic aperture radar, a radar altimeter and other powerful instruments to measure ocean surface temperature and winds at sea. An additional sensor was used for atmospheric ozone research</gco:CharacterString>
                  </xsl:if>
                  <xsl:if test="/hdf5/metadata/input_image/platform='Sentinel-1A' or
                                /hdf5/metadata/input_image/platform='Sentinel-1B'">
                    <gco:CharacterString>Sentinel-1 is a two satellite constellation with the prime objectives of Land and Ocean monitoring.</gco:CharacterString>
                  </xsl:if>
                  </gmi:description>
                  <gmi:instrument xlink:href="#sarInstrument" />
                  <eos:otherPropertyType>
                    <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
                  </eos:otherPropertyType>
                  <eos:otherProperty>
                    <gco:Record>
                      <eos:additionalAttributes>
                        <eos:EOS_AdditionalAttributes>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>input image(s)</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>file name(s) of input image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="STRING">STRING</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/file" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>wavelength</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>wavelength of the sensor</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/wavelength" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>beam mode</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>beam mode of the sensor</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="STRING">STRING</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/beam_mode" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>orbit</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>absolute orbit of the image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="INT">INT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/absolute_orbit" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <xsl:if test="/hdf5/metadata/input_image/frame">
                            <eos:additionalAttribute>
                              <eos:EOS_AdditionalAttribute>
                                <eos:reference>
                                  <eos:EOS_AdditionalAttributeDescription>
                                    <eos:type>
                                      <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                    </eos:type>
                                    <eos:name>
                                      <gco:CharacterString>frame</gco:CharacterString>
                                    </eos:name>
                                    <eos:description>
                                      <gco:CharacterString>frame number of the image</gco:CharacterString>
                                    </eos:description>
                                    <eos:dataType>
                                      <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="INT">INT</eos:EOS_AdditionalAttributeDataTypeCode>
                                    </eos:dataType>
                                  </eos:EOS_AdditionalAttributeDescription>
                                </eos:reference>
                                <eos:value>
                                  <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/frame" /></gco:CharacterString>
                                </eos:value>
                              </eos:EOS_AdditionalAttribute>
                            </eos:additionalAttribute>                            
                          </xsl:if>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>flight direction</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>flight direction of the sensor</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="STRING">STRING</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/flight_direction" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>data format</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>data format of the input data</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="STRING">STRING</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/data_format" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>PRF</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pulse repetition frequency</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>Hz</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/prf" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>start time</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>UTC time at the start of the image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="DATETIME">DATETIME</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/start_datetime" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>center time</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>UTC time at the center of the image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="DATETIME">DATETIME</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/center_datetime" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>end time</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>UTC time at the end of the image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="DATETIME">DATETIME</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/end_datetime" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>Doppler poly 0</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Doppler polynomial (constant term)</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>Hz</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/doppler_poly_0" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>Doppler poly 1</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Doppler polynomial (linear term)</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>Hz/m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/doppler_poly_1" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>Doppler poly 2</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Doppler polynomial (quadratic term)</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>Hz/m^2</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/doppler_poly_2" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>Doppler poly dot 0</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Doppler velocity polynomial (constant term)</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>Hz/s</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/doppler_poly_dot_0" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>Doppler poly dot 1</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Doppler velocity polynomial (linear term)</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>Hz/s/m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/doppler_poly_dot_1" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>Doppler poly dot 2</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Doppler velocity polynomial (quadratic term)</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>Hz/s/m^2</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/doppler_poly_dot_2" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>range looks</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>number of range looks</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="INT">INT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/range_looks" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>azimuth looks</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>number of azimuth looks</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="INT">INT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/azimuth_looks" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>slant spacing</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pixel size in slant range</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/slant_spacing" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>azimuth spacing</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>pixel size in azimuth direction</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/azimuth_spacing" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>slant to first</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Slant range distance to near-range edge of the image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/slant_to_first" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>slant to center</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Slant range distance to center of the image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/slant_to_center" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                          <eos:additionalAttribute>
                            <eos:EOS_AdditionalAttribute>
                              <eos:reference>
                                <eos:EOS_AdditionalAttributeDescription>
                                  <eos:type>
                                    <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#EOS_AdditionalAttributeTypeCode" codeListValue="acquisitionInformation">acquisitionInformation</eos:EOS_AdditionalAttributeTypeCode>
                                  </eos:type>
                                  <eos:name>
                                    <gco:CharacterString>slant to last</gco:CharacterString>
                                  </eos:name>
                                  <eos:description>
                                    <gco:CharacterString>Slant range distance to far-range edge of the image</gco:CharacterString>
                                  </eos:description>
                                  <eos:dataType>
                                    <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="FLOAT">FLOAT</eos:EOS_AdditionalAttributeDataTypeCode>
                                  </eos:dataType>
                                  <eos:parameterUnitsOfMeasure>
                                    <gco:CharacterString>m</gco:CharacterString>
                                  </eos:parameterUnitsOfMeasure>
                                </eos:EOS_AdditionalAttributeDescription>
                              </eos:reference>
                              <eos:value>
                                <gco:CharacterString><xsl:value-of select="/hdf5/metadata/input_image/slant_to_last" /></gco:CharacterString>
                              </eos:value>
                            </eos:EOS_AdditionalAttribute>
                          </eos:additionalAttribute>
                        </eos:EOS_AdditionalAttributes>
                      </eos:additionalAttributes>
                    </gco:Record>
                  </eos:otherProperty>
                </eos:EOS_Platform>
              </gmi:platform>
            </gmi:MI_AcquisitionInformation>
          </gmi:acquisitionInformation>
        </gmi:MI_Metadata>
      </gmd:has>
      <gmd:has>
        <gmi:MI_Metadata>
          <gmd:hierarchyLevel>
            <gmd:MD_ScopeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>
          </gmd:hierarchyLevel>
          <gmd:contact>
            <gmd:CI_ResponsibleParty>
              <gmd:organisationName>
                <gco:CharacterString>Alaska Satellite Facility</gco:CharacterString>
              </gmd:organisationName>
              <gmd:contactInfo xlink:href="#ASFcontactInfo"/>
              <gmd:role>
                <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="pointOfContact">pointOfContact</gmd:CI_RoleCode>
              </gmd:role>
            </gmd:CI_ResponsibleParty>
          </gmd:contact>
          <gmd:dateStamp>
            <gco:DateTime>
              <xsl:value-of select="/hdf5/metadata_creation" />
            </gco:DateTime>
          </gmd:dateStamp>
          <gmd:metadataStandardName>
            <gco:CharacterString>ISO 19115-2 Geographic information — Metadata — Part 2: Extensions for imagery and gridded data</gco:CharacterString>
          </gmd:metadataStandardName>
          <gmd:metadataStandardVersion>
            <gco:CharacterString>ISO 19115-2:2009-02-15</gco:CharacterString>
          </gmd:metadataStandardVersion>
          <gmd:spatialRepresentationInfo>
            <gmd:MD_GridSpatialRepresentation>
              <gmd:numberOfDimensions>
                <gco:Integer>2</gco:Integer>
              </gmd:numberOfDimensions>
              <gmd:axisDimensionProperties>
                <gmd:MD_Dimension>
                  <gmd:dimensionName>
                    <gmd:MD_DimensionNameTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:MD_DimensionNameTypeCode" codeListValue="row">row</gmd:MD_DimensionNameTypeCode>
                  </gmd:dimensionName>
                  <gmd:dimensionSize>
                    <gco:Integer><xsl:value-of select="/hdf5/metadata/digital_elevation_model/height" /></gco:Integer>
                  </gmd:dimensionSize>
                  <gmd:resolution>
                    <gco:Distance uom="meter"><xsl:value-of select="/hdf5/metadata/digital_elevation_model/y_spacing" /></gco:Distance>
                  </gmd:resolution>
                </gmd:MD_Dimension>
              </gmd:axisDimensionProperties>
              <gmd:axisDimensionProperties>
                <gmd:MD_Dimension>
                  <gmd:dimensionName>
                    <gmd:MD_DimensionNameTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:MD_DimensionNameTypeCode" codeListValue="column">column</gmd:MD_DimensionNameTypeCode>
                  </gmd:dimensionName>
                  <gmd:dimensionSize>
                    <gco:Integer><xsl:value-of select="/hdf5/metadata/digital_elevation_model/width" /></gco:Integer>
                  </gmd:dimensionSize>
                  <gmd:resolution>
                    <gco:Distance uom="meter"><xsl:value-of select="/hdf5/metadata/digital_elevation_model/x_spacing" /></gco:Distance>
                  </gmd:resolution>
                </gmd:MD_Dimension>
              </gmd:axisDimensionProperties>
              <gmd:cellGeometry>
                <gmd:MD_CellGeometryCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#gmd:MD_CellGeometryCode" codeListValue="area">area</gmd:MD_CellGeometryCode>
              </gmd:cellGeometry>
              <gmd:transformationParameterAvailability>
                <gco:Boolean>false</gco:Boolean>
              </gmd:transformationParameterAvailability>
              <eos:otherPropertyType>
                <gco:RecordType xlink:href="http://earthdata.nasa.gov/schemas/eos/eos.xsd#xpointer(//element[@name='EOS_AdditionalAttributes'])">EOS Additional Attributes</gco:RecordType>
              </eos:otherPropertyType>
              <eos:otherProperty> 
                <gco:Record>
                  <eos:additionalAttributes>
                    <eos:EOS_AdditionalAttributes>
                      <eos:additionalAttribute>
                        <eos:EOS_AdditionalAttribute>
                          <eos:reference>
                            <eos:EOS_AdditionalAttributeDescription>
                              <eos:type>
                                <eos:EOS_AdditionalAttributeTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/Codelist.xml#eos:EOS_AdditionalAttributeTypeCode" codeListValue="spatialInformation">spatialInformation</eos:EOS_AdditionalAttributeTypeCode>
                              </eos:type>
                              <eos:name>
                                <gco:CharacterString>map projection</gco:CharacterString>
                              </eos:name>
                              <eos:description>
                                <gco:CharacterString>map projection definition (in well known text format) for the digital elevation model</gco:CharacterString>
                              </eos:description>
                              <eos:dataType>
                                <eos:EOS_AdditionalAttributeDataTypeCode codeList="http://earthdata.nasa.gov/metadata/resources/" codeListValue="STRING">STRING</eos:EOS_AdditionalAttributeDataTypeCode>
                              </eos:dataType>
                            </eos:EOS_AdditionalAttributeDescription>
                          </eos:reference>
                          <eos:value>
                            <gco:CharacterString><xsl:value-of select="/hdf5/metadata/digital_elevation_model/projection_string" /></gco:CharacterString>
                          </eos:value>
                        </eos:EOS_AdditionalAttribute>
                      </eos:additionalAttribute>
                    </eos:EOS_AdditionalAttributes>
                  </eos:additionalAttributes>
                </gco:Record>
              </eos:otherProperty>
            </gmd:MD_GridSpatialRepresentation>
          </gmd:spatialRepresentationInfo>
          <gmd:identificationInfo>
            <gmd:MD_DataIdentification>
              <gmd:citation>
                <gmd:CI_Citation>
                  <gmd:title>
                    <gmx:FileName><xsl:value-of select="/hdf5/metadata/digital_elevation_model/file" /></gmx:FileName>
                  </gmd:title>
                <xsl:if test="/hdf5/metadata/digital_elevation_model/source='NED1'">
                  <gmd:alternateTitle>
                    <gco:CharacterString>DEM used for terrain correction: NED1 - National Elevation Dataset at 1 arc second (about 30 m) resolution.</gco:CharacterString>
                  </gmd:alternateTitle>
                </xsl:if>
                <xsl:if test="/hdf5/metadata/digital_elevation_model/source='NED2'">
                  <gmd:alternateTitle>
                    <gco:CharacterString>DEM used for terrain correction: NED2 - National Elevation Dataset at 2 arc second (about 60 m) resolution.</gco:CharacterString>
                  </gmd:alternateTitle>
                </xsl:if>
                <xsl:if test="/hdf5/metadata/digital_elevation_model/source='NED13'">
                  <gmd:alternateTitle>
                    <gco:CharacterString>DEM used for terrain correction: NED13 - National Elevation Dataset at 1/3 arc second (about 10 m) resolution.</gco:CharacterString>
                  </gmd:alternateTitle>
                </xsl:if>
                <xsl:if test="/hdf5/metadata/digital_elevation_model/source='SRTMGL3'">
                  <gmd:alternateTitle>
                    <gco:CharacterString>DEM used for terrain correction: SRTMGL3 - Shuttle Radar Topography mission at 90 m resolution.</gco:CharacterString>
                  </gmd:alternateTitle>
                </xsl:if>
                <xsl:if test="/hdf5/metadata/digital_elevation_model/source='SRTMGL1'">
                  <gmd:alternateTitle>
                    <gco:CharacterString>DEM used for terrain correction: SRTMGL1 - Shuttle Radar Topography mission at 30 m resolution. Additional corrections by the Alaska Satellite Facility (June 2015, version 1.1).</gco:CharacterString>
                  </gmd:alternateTitle>
                </xsl:if>
                <xsl:if test="/hdf5/metadata/digital_elevation_model/source='SRTMUS1'">
                  <gmd:alternateTitle>
                    <gco:CharacterString>DEM used for terrain correction: SRTMUS1 - Shuttle Radar Topography mission at 30 m resolution.</gco:CharacterString>
                  </gmd:alternateTitle>
                </xsl:if>
                <xsl:if test="/hdf5/metadata/digital_elevation_model/source='SRTMAU1'">
                  <gmd:alternateTitle>
                    <gco:CharacterString>DEM used for terrain correction: SRTMAU1 - Shuttle Radar Topography mission at 30 m resolution.</gco:CharacterString>
                  </gmd:alternateTitle>
                </xsl:if>
                  <gmd:date>
                    <gmd:CI_Date>
                      <gmd:date>
                        <gco:DateTime><xsl:value-of select="/hdf5/metadata_creation" /></gco:DateTime>
                      </gmd:date>
                      <gmd:dateType>
                        <gmd:CI_DateTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode"
                                                         codeListValue="creation">creation</gmd:CI_DateTypeCode>
                      </gmd:dateType>
                    </gmd:CI_Date>
                  </gmd:date>
                  <gmd:citedResponsibleParty>
                    <gmd:CI_ResponsibleParty>
                      <gmd:organisationName>
                        <gco:CharacterString>U.S. Geological Survey (USGS) - USGS Earth Resources Observation &amp; Science (EROS) Center</gco:CharacterString>
                      </gmd:organisationName>
                      <gmd:contactInfo>
                        <gmd:CI_Contact>
                          <gmd:address>
                            <gmd:CI_Address>
                              <gmd:deliveryPoint>
                                <gco:CharacterString>47914 252nd Street</gco:CharacterString>
                              </gmd:deliveryPoint>
                              <gmd:city>
                                <gco:CharacterString>Sioux Falls</gco:CharacterString>
                              </gmd:city>
                              <gmd:administrativeArea>
                                <gco:CharacterString>South Dakota</gco:CharacterString>
                              </gmd:administrativeArea>
                              <gmd:postalCode>
                                <gco:CharacterString>57198-0001</gco:CharacterString>
                              </gmd:postalCode>
                              <gmd:country>
                                <gco:CharacterString>United States</gco:CharacterString>
                              </gmd:country>
                            </gmd:CI_Address>
                          </gmd:address>
                        </gmd:CI_Contact>
                      </gmd:contactInfo>
                      <gmd:role>
                        <gmd:CI_RoleCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode" codeListValue="gmd:distributor">gmd:distributor</gmd:CI_RoleCode>
                      </gmd:role>
                    </gmd:CI_ResponsibleParty>
                  </gmd:citedResponsibleParty>
                  <gmd:presentationForm>
                    <gmd:CI_PresentationFormCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_PresentationFormCode" codeListValue="documentDigital">documentDigital</gmd:CI_PresentationFormCode>
                  </gmd:presentationForm>
                </gmd:CI_Citation>
              </gmd:citation>
              <gmd:abstract>
              <xsl:if test="/hdf5/metadata/digital_elevation_model/source='NED1' or
                            /hdf5/metadata/digital_elevation_model/source='NED2' or
                            /hdf5/metadata/digital_elevation_model/source='NED13'">
                <gco:CharacterString>The National Elevation Dataset (NED) is the primary elevation data product produced and distributed by the USGS. The NED provides the best available public domain raster elevation data of the conterminous United States, Alaska, Hawaii, and territorial islands in a seamless format.  The NED is derived from diverse source data, processed to a common coordinate system and unit of vertical measure.  All NED data are distributed in geographic coordinates in units of decimal degrees, and in conformance with the North American Datum of 1983 (NAD 83).  All elevation values are provided in units of meters, and are eos:referenced to the North American Vertical Datum of 1988 (NAVD 88) over the conterminous United States.  The vertical eos:reference will vary in other areas.  NED data are available nationally at resolutions of 1 arc-second (approx. 30 meters) and 1/3 arc-second (approx. 10 meters), and in limited areas at 1/9 arc-second (approx. 3 meters).  At present, the bulk of Alaska is only available at a 2 arc-second (approx. 60 meters) resolution, owing to a lack of higher resolution source data, though some areas are available at resolutions of 1 and 1/3 arc-second with plans for significant upgrades of the state over the next five years.  The NED is updated on a nominal two month cycle to integrate newly available, improved elevation source data.</gco:CharacterString>
              </xsl:if>
              <xsl:if test="/hdf5/metadata/digital_elevation_model/source='SRTM3GL' or
                            /hdf5/metadata/digital_elevation_model/source='SRTMUS1'">
                <gco:CharacterString>The Shuttle Radar Topography Mission (SRTM) obtained elevation data on a near-global scale to generate the most complete high-resolution digital topographic database of Earth. SRTM consisted of a specially modified radar system that flew onboard the Space Shuttle Endeavour during an 11-day mission in February of 2000. SRTM elevation data were processed from raw C-band radar signals spaced at intervals of 1 arc-second (approximately 30 meters) at NASA’s Jet Propulsion Laboratory (JPL). This version was then edited or finished by the NGA to delineate and flatten water bodies, better define coastlines, remove spikes and wells, and fill small voids. Data for regions outside the United States were sampled at 3 arc-seconds (approximately 90 meters) using a cubic convolution resampling technique for open distribution.</gco:CharacterString>
              </xsl:if>
              </gmd:abstract>
              <gmd:status>
                <gmd:MD_ProgressCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_ProgressCode" codeListValue="completed">completed</gmd:MD_ProgressCode>
              </gmd:status>
              <gmd:resourceMaintenance>
                <gmd:MD_MaintenanceInformation>
                  <gmd:maintenanceAndUpdateFrequency>
                    <gmd:MD_MaintenanceFrequencyCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_MaintenanceFrequencyCode" codeListValue="asNeeded">asNeeded</gmd:MD_MaintenanceFrequencyCode>
                  </gmd:maintenanceAndUpdateFrequency>
                </gmd:MD_MaintenanceInformation>
              </gmd:resourceMaintenance>
              <gmd:resourceConstraints>
                <gmd:MD_LegalConstraints>
                  <gmd:accessConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:accessConstraints>
                  <gmd:useConstraints>
                    <gmd:MD_RestrictionCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions">otherRestrictions</gmd:MD_RestrictionCode>
                  </gmd:useConstraints>
                  <gmd:otherConstraints>
                    <gco:CharacterString>
None. Any downloading and use of these data signifies a user's agreement to comprehension and compliance of the USGS Standard Disclaimer. Insure all portions of metadata are read and clearly understood before using these data in order to protect both user and USGS interests.
                    
There is no guarantee or warranty concerning the accuracy of the data. Users should be aware that temporal changes may have occurred since these data were collected and that some parts of these data may no longer represent actual surface conditions. Users should not use these data for critical applications without a full awareness of its limitations. Acknowledgement of the originating agencies would be appreciated in products derived from these data. Any user who modifies the data is obligated to describe the eos:types of modifications they perform. User specifically agrees not to misrepresent the data, nor to imply that changes made were approved or endorsed by the USGS. Please refer to http://www.usgs.gov/privacy.html for the USGS disclaimer.                  
                    </gco:CharacterString>
                  </gmd:otherConstraints>
                </gmd:MD_LegalConstraints>
              </gmd:resourceConstraints>
              <gmd:spatialRepresentationType>
                <gmd:MD_SpatialRepresentationTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_SpatialRepresentationTypeCode" codeListValue="grid">grid</gmd:MD_SpatialRepresentationTypeCode>
              </gmd:spatialRepresentationType>
              <gmd:language>
                <gco:CharacterString>eng</gco:CharacterString>
              </gmd:language>
              <gmd:characterSet>
                <gmd:MD_CharacterSetCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf8</gmd:MD_CharacterSetCode>
              </gmd:characterSet>
              <gmd:topicCategory>
                <gmd:MD_TopicCategoryCode>elevation</gmd:MD_TopicCategoryCode>
              </gmd:topicCategory>
              <gmd:environmentDescription>
              <xsl:if test="/hdf5/metadata/digital_elevation_model/source='NED1' or
                            /hdf5/metadata/digital_elevation_model/source='NED2' or
                            /hdf5/metadata/digital_elevation_model/source='NED13'">
                <gco:CharacterString>The digital elevation model was provided in ArcGrid format and converted into GeoTIFF format.</gco:CharacterString>
              </xsl:if>
              <xsl:if test="/hdf5/metadata/digital_elevation_model/source='SRTMGL1' or
                            /hdf5/metadata/digital_elevation_model/source='SRTMGL3' or
                            /hdf5/metadata/digital_elevation_model/source='SRTMUS1'">
                <gco:CharacterString>The digital elevation model was provided in HGT format and converted into GeoTIFF format.</gco:CharacterString>
              </xsl:if>
              </gmd:environmentDescription>
              <gmd:extent>
                <gmd:EX_Extent>
                  <gmd:description>
                    <gco:CharacterString>geographic extent of digital elevation model</gco:CharacterString>
                  </gmd:description>
                  <gmd:geographicElement>
                    <gmd:EX_GeographicBoundingBox id="demBoundingBox">
                      <gmd:extentTypeCode>
                        <gco:Boolean>true</gco:Boolean>
                      </gmd:extentTypeCode>
                      <gmd:westBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/digital_elevation_model/westBoundLongitude" /></gco:Decimal>
                      </gmd:westBoundLongitude>
                      <gmd:eastBoundLongitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/digital_elevation_model/eastBoundLongitude" /></gco:Decimal>
                      </gmd:eastBoundLongitude>
                      <gmd:southBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/digital_elevation_model/southBoundLatitude" /></gco:Decimal>
                      </gmd:southBoundLatitude>
                      <gmd:northBoundLatitude>
                        <gco:Decimal><xsl:value-of select="/hdf5/extent/digital_elevation_model/northBoundLatitude" /></gco:Decimal>
                      </gmd:northBoundLatitude>
                    </gmd:EX_GeographicBoundingBox>
                  </gmd:geographicElement>
                </gmd:EX_Extent>
              </gmd:extent>
              <gmd:supplementalInformation>
                <gco:CharacterString>
The accuracy of the digital elevation model type has been assessed. The results are reported in

Gesch, D.B., Oimoen, M.J. and Evans, G.A., 2014. Accuracy Assessment of the United States Geological Survey National Elevation Dataset, and Comparison with Other Large-Area Elevation Datasets - SRTM and ASTER. U.S. Geological Survey Open-File Report 2014–1008, 10 p. 
                </gco:CharacterString>
              </gmd:supplementalInformation>
            </gmd:MD_DataIdentification>
          </gmd:identificationInfo>
          <gmd:contentInfo>
            <gmd:MD_CoverageDescription>
              <gmd:attributeDescription>
                <gco:RecordType>oversampled digital elevation model used for terrain correction</gco:RecordType>
              </gmd:attributeDescription>
              <gmd:contentType>
                <gmd:MD_CoverageContentTypeCode codeList="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_CoverageContentTypeCode" codeListValue="image">image</gmd:MD_CoverageContentTypeCode>
              </gmd:contentType>
              <gmd:dimension>
                <gmi:MI_Band>
                  <gmd:maxValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/digital_elevation_model/maximum_value" /></gco:Real>
                  </gmd:maxValue>
                  <gmd:minValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/digital_elevation_model/minimum_value" /></gco:Real>
                  </gmd:minValue>
                  <gmd:meanValue>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/digital_elevation_model/mean_value" /></gco:Real>
                  </gmd:meanValue>
                  <gmd:standardDeviation>
                    <gco:Real><xsl:value-of select="/hdf5/statistics/digital_elevation_model/standard_deviation" /></gco:Real>
                  </gmd:standardDeviation>
                </gmi:MI_Band>
              </gmd:dimension>
            </gmd:MD_CoverageDescription>
          </gmd:contentInfo>
          <gmd:distributionInfo>
            <gmd:MD_Distribution>
              <gmd:distributionFormat>
                <gmd:MD_Format>
                  <gmd:name>
                    <gco:CharacterString>GeoTIFF</gco:CharacterString>
                  </gmd:name>
                  <gmd:version>
                    <gco:CharacterString>1.2.2</gco:CharacterString>
                  </gmd:version>
                </gmd:MD_Format>
              </gmd:distributionFormat>
            </gmd:MD_Distribution>
          </gmd:distributionInfo>
        </gmi:MI_Metadata>
      </gmd:has>
    </gmd:DS_DataSet>
  </gmd:composedOf>
  <gmd:seriesMetadata gco:nilReason="inapplicable"/>
</gmd:DS_Series>
</xsl:template>
</xsl:stylesheet>
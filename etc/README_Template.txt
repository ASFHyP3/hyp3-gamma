RTC Data Package

This folder contains radiometric terrain corrected (RTC) products and their associated files, processed [DATE] [TIME] UTC. RTC is performed by the Alaska Satellite Facility (ASF) using GAMMA software. The pixel spacing is [SPACING] m.

The folder and each of its contents all share the same base name, using the following convention: 
S1x_yy_RTzz_aaaaaaaaTbbbbbb_c_def 
x:        Sentinel-1 Mission (A or B)
yy:       Beam Mode
zz:       Terrain Correction Resolution
aaaaaaaa: Start Date of Acquisition (YYYYMMDD)
bbbbbb:   Start Time of Acquisition (HHMMSS)
c:        Processor (Gamma or S1TBX)
d:        gamma-0 (g) or sigma-0 (s) output
e:        amplitude (a) or power (p) output
f:        Not filtered (n) or Filtered (f)

The source granule used to generate the products contained in this folder is:
[GRAN_NAME]

To cite the data:
ASF DAAC [YEARPROCESSED], contains modified Copernicus Sentinel data [YEARACQUIRED], processed by ESA.

Refer to the ASF Sentinel-1 RTC User Guide for additional guidance for the use of this dataset:
https://media.asf.alaska.edu/uploads/sentinel/Sentinel_RTC_Users_Guide.pdf

The side-looking geometry of SAR imagery leads to geometric and radiometric distortions, causing foreshortening, layover, shadowing, and radiometric variations due to terrain slope. Radiometric terrain correction converts unprocessed SAR data into geocoded tiff images with values directly relating to physical properties, alleviating the inherent SAR distortions. The process improves backscatter estimates and provides geolocation information, so images can be used as input for applications such as the monitoring of deforestation, land-cover classification, and delineation of wet snow-covered areas.

The files generated in this process include:

1. Backscatter tif data files for each polarity available
2. Browse images (png and kmz format) in grayscale and color (when dual-pol is available)
3. A copy of the DEM used to correct the data (included in standard products; you can choose to omit this layer when custom ordering imagery)
4. An incidence angle map (included in standard products; you can choose to omit this layer when custom ordering imagery)
5. A layover-shadow mask
6. An xml file in ISO 19115-2 format, describing all of the products
7. An ArcGIS xml metadata file for each raster layer, accessible through the Item Description in ArcGIS
8. Log file

See below for detailed descriptions of each of the products.

-------------
1. Backscatter data files

GeoTIFF files are generated for each polarity available in the source granule. Each filename will include the polarization: VV or HH for primary polarization, and VH or HV for cross-polarization.

These files have been processed to output [POWERTYPE]-0 [FORMAT].

-------------
2. Browse images in grayscale and color

PNG files are generated in two different resolutions for quick visualization of the backscatter data. Each png browse image is accompanied by an aux file containing the projection and geocoding information for the file.

All products will include a grayscale png browse image in both resolutions. It is a rendering of the primary polarization data, scaled to an ASF standard to display nicely in grayscale. The low-resolution image is designated by a simple .png extension, while the tag _large.png indicates the medium-resolution image. 

For dual-pol products, a false color png browse image is generated in both resolutions. It is a rendering of the primary and cross-polarization data, scaled to an ASF standard to display nicely in color. These files are additionally tagged with _rgb, but otherwise have the same tags/extensions as the grayscale browse images.

KMZ files are generated in the higher resolution for use in Google Earth and other compatible applications. All products will include a grayscale kmz image, and dual-pol products will also include a color browse kmz image.

-------------
3. A copy of the DEM used to correct the data

The digital elevation model layer is included with standard products, but is optional when placing a custom order for imagery. This layer is tagged with -dem.tif

The best digital elevation model publicly available for each granule is used in the RTC process, so different granules may be processed using different source DEM layers. The sources include the National Elevation Dataset (NED) or the Shuttle Radar Topography Mission (SRTM), and the resolution of the DEM varies depending on the location of the granule. The DEM is clipped from the source layer to the size needed for full granule coverage, or to the extent of the available DEM source data if full coverage is not available. It is then resampled from the native DEM resolution to [SPACING] m for use in RTC.

The source of the DEM for this particular product is [DEM], which has a native resolution of [RESA] arc seconds (about [RESM] meters).

The NED provides the best available public domain raster elevation data of the conterminous United States, Alaska, Hawaii, and territorial islands in a seamless format. The NED is derived from diverse source data, processed to a common coordinate system and unit of vertical measure. For more information and to access the full NED dataset, refer to https://lta.cr.usgs.gov/NED

The SRTM was flown aboard the space shuttle Endeavour February 11-22, 2000. The National Aeronautics and Space Administration (NASA) and the National Geospatial-Intelligence Agency (NGA) participated in an international project to acquire radar data which were used to create the first near-global set of land elevations. For more information and to access the full SRTM dataset, refer to https://lta.cr.usgs.gov/SRTM

-------------
4. An incidence angle map

The incidence angle map is is included with standard products, but is optional when placing a custom order for imagery. This layer is tagged with -inc_map.tif

This map records the incidence angle for each pixel in the RTC image. The incidence angle is the angle between the incident radar beam and the direction perpendicular to the ground surface, expressed in radians.

-------------
5. A layover-shadow mask

The layover/shadow mask indicates which pixels in the RTC image have been affected by layover and shadow. This layer is tagged with -ls_map.tif 

The pixel values are generated by adding the following values together to indicate which layover and shadow effects are impacting each pixel:
0  Pixel not tested for layover or shadow
1  Pixel tested for layover or shadow
2  Pixel has a look angle less than the slope angle
4  Pixel is in an area affected by layover
8  Pixel has a look angle less than the opposite of the slope angle
16 Pixel is in an area affected by shadow

There are 17 possible different pixel values, indicating the layover, shadow, and slope conditions present added together for any given pixel. 
The values in each cell can range from 0 to 31:
0  Not tested for layover or shadow
1  Not affected by either layover or shadow
3  Look angle < slope angle
5  Affected by layover
7  Affected by layover; look angle < slope angle
9  Look angle < opposite slope angle
11 Look angle < slope and opposite slope angle
13 Affected by layover; look angle < opposite slope angle
15 Affected by layover; look angle < slope and opposite slope angle
17 Affected by shadow
19 Affected by shadow; look angle < slope angle
21 Affected by layover and shadow
23 Affected by layover and shadow; look angle < slope angle
25 Affected by shadow; look angle < opposite slope angle
27 Affected by shadow; look angle < slope and opposite slope angle
29 Affected by shadow and layover; look angle < opposite slope angle
31 Affected by shadow and layover; look angle < slope and opposite slope angle

-------------
6. An xml file in ISO 19115-2 format

There is an iso.xml file that contains the information about the processing of this product.

-------------
7. ArcGIS-compatible xml metadata files

Each raster in this folder has an associated xml file. It is named with the same filename as the raster, but also includes an .xml extension. When any of the rasters are viewed in ArcGIS, the associated xml file is recognized by the software, and the contents will display in the Item Description for that raster. Once the file is viewed in ArcGIS, the software will change the xml file to include metadata inherent to the raster (geographic extent, raster format, etc.) along with the descriptive metadata included in the original xml file.

ArcGIS users should take care not to edit the xml files directly, or to change filenames outside of the ArcGIS environment, as it may render the metadata files unreadable by ArcGIS. 

Users who do not use ArcGIS to interact with the data will still find the information included in the individual xml files very useful, but will need to contend with the xml tags if viewing it as a textfile or in a browser.

-------------
8. Log file

A log file is generated during processing, which includes all of the parameters used for each part of the RTC process. It has a .log extension.

-------------
RTC Processing

The basic steps in the radiometric terrain correction process are as follows:
1.  Data granule is ingested into gamma format - calibration is done during this step. 
2.  If required, data is multi-looked to the desired number of looks (default is 6 for GRD and 3 for SLC). This product used [LOOKS] looks. 
3.  A DEM is extracted from the ASF DEM heap covering the granule to be corrected. 
4.  A mapping function is created, mapping from DEM space into SAR space. 
5.  A simulated SAR image is created. 
6.  The simulated SAR image and the real SAR image are coregistered. 
7.  The mapping function is updated with the coregistration information. 
8.  The SAR image is radiometrically corrected using a pixel integration approach to remove radiometric distortions in foreshortening or layover areas. 
9.  The inversion of the mapping function is used to terrain correct and geocode the radiometrically corrected SAR image. 
10. Post processing creates geotiffs, pngs, kmzs, and metadata.

The Algorithm Theoretical Basis Document (ATBD), which provides the theoretical background of the algorithms and processing flows used for the generation of this product, is available here:
https://media.asf.alaska.edu/uploads/sentinel/RTC_ATBD_Sentinel.pdf

-------------
The Sentinel-1 mission 

The Sentinel-1A satellite was launched April 3, 2014, and the Sentinel-1B satellite was launched April 25, 2016. The satellites each have a 12-day repeat cycle. 

More information about the mission is available at:
https://earth.esa.int/web/guest/missions/esa-operational-eo-missions/sentinel-1

Additional information about Sentinel-1 data, imagery, tools and applications is available at:
https://www.asf.alaska.edu/sentinel/

-------------
For assistance, contact the Alaska Satellite Facility:
uso@asf.alaska.edu
907-474-6166
907-474-2665


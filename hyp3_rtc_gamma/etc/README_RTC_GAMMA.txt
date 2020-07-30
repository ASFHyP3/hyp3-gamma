ASF RTC Data Package (GAMMA)
============================

This folder contains radiometric terrain corrected (RTC) products and their associated files. This data was processed by the ASF DAAC using the HyP3 RTC GAMMA plugin version [HYP3_VER] and GAMMA software release [GAMMA_VER]. They are projected to [PCS], and the pixel spacing is [SPACING] m.

Processing Date/Time: [DATE] [TIME] UTC

The folder and each of its contents all share the same base name, using the following convention:
```
S1x_yy_aaaaaaaaTbbbbbb_ppo_RTCzz_G_defklm_ssss
x:          Sentinel-1 Mission (A or B)
yy:         Beam Mode
aaaaaaaa:   Start Date of Acquisition (YYYYMMDD)
bbbbbb:     Start Time of Acquisition (HHMMSS)
pp:         Polarization
o:          Orbit Type: Precise (P), Restituted (R), or Original Predicted (O)
zz:         Terrain Correction Resolution
d:          Gamma-0 (g) or Sigma-0 (s) Output
e:          Power (p) or Amplitude (a) Output
f:          Unmasked (u) or Water Masked (w)
k:          Not Filtered (n) or Filtered (f)
l:          Entire Area (e) or Clipped Area (c)
m:          Dead Reckoning (d) or DEM Matching (m)
ssss:       Product ID
```

The source granule used to generate the products contained in this folder is:
[GRAN_NAME]

<!-- Consider opening this document in a Markdown editor/viewer for easier reading -->

### Using this data ###

Please refer to the ASF Sentinel-1 RTC User Guide for in-depth guidance on the use of this dataset:
* https://asf.alaska.edu/wp-content/uploads/2019/02/Sentinel_RTC_Users_Guide.pdf

When using this data in a publication or presentation, we ask that you include the following acknowledgement:

    RTC product processed by ASF DAAC HyP3 [YEARPROCESSED] using GAMMA software. Contains modified Copernicus Sentinel data [YEARACQUIRED], processed by ESA.

DOIs are also provided for citation when discussing the HyP3 software or plugins:
* HyP3 processing environment, DOI: [10.5281/zenodo.3962581](https://doi.org/10.5281/zenodo.3962581)
* HyP3 RTC GAMMA plugin, DOI: [10.5281/zenodo.3962936](https://doi.org/10.5281/zenodo.3962936)

For information on GAMMA SAR software, please see: https://gamma-rs.ch/

*************
# Product Contents #

The side-looking geometry of SAR imagery leads to geometric and radiometric distortions, causing foreshortening, layover, shadowing, and radiometric variations due to terrain slope. Radiometric terrain correction converts unprocessed SAR data into geocoded TIFF images with values directly relating to physical properties, alleviating the  inherent SAR distortions. The process improves backscatter estimates and provides geolocation information, so images can be used as input for applications such as the monitoring of deforestation, land-cover classification, and delineation of wet snow-covered areas.

The files generated in this process include:

1. Radiometric Terrain Corrected GeoTIFF data files for each polarization available
2. Browse images (PNG and KMZ format) in grayscale and color (when dual-pol is available)
3. A copy of the DEM used to correct the data (included in standard products; you can choose to omit this layer when custom ordering imagery)
4. An incidence angle map (included in standard products; you can choose to omit this layer when custom ordering imagery)
5. A layover-shadow mask
6. An ArcGIS xml metadata file for each raster layer, displayed in the Item Description (ArcGIS Desktop) or Metadata (ArcGIS Pro)
7. An xml file in ISO 19115-2 format, describing all of the products
8. A shapefile indicating the data and raster extents
9. Log file

See below for detailed descriptions of each of the products.

-------------
## 1. Radiometric Terrain Corrected data files

GeoTIFF files are generated for each polarization available in the source granule. Each filename will include the polarization: VV or HH for primary polarization, and VH or HV for cross-polarization. To learn more about polarimetry, refer to https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/product-overview/polarimetry

These files have been processed to output [POWERTYPE]-0 [FORMAT].

[FILT] speckle filter has been applied to the RTC images. The default is to not apply a speckle filter, but the user can choose to apply a filter when ordering the RTC imagery. When the filtering option is selected, an Enhanced Lee filter is applied during RTC processing to remove speckle while preserving edges. When applied, the filter is set to a dampening factor of 1, with a box size of 7x7 pixels and [FLOOKS] looks.

-------------
## 2. Browse images in grayscale and color

PNG files are generated for quick visualization of the backscatter data. Each png browse image is accompanied by an aux file containing the projection and geocoding information for the file.

All products will include a grayscale png browse image. It is a rendering of the primary polarization data, scaled to an ASF standard to display nicely in grayscale. The image is designated by a simple .png extension.

For dual-pol products, a false-color png browse image is generated. It is a rendering of the primary and cross-polarization data, scaled to an ASF standard to display nicely in color. These files are additionally tagged with _rgb, but otherwise have the same tags/extensions as the grayscale browse images.

KMZ files are generated for use in Google Earth and other compatible applications. All products will include a grayscale kmz image, and dual-pol products will also include a color browse kmz image.

-------------
## 3. DEM used to correct the data

The Digital Elevation Model (DEM) layer is included with standard products, but is optional when placing a custom order for imagery. This layer is tagged with _dem.tif

The best DEM publicly available for each granule is used in the RTC process, so different granules may be processed using different source DEM layers. The resolution of the source DEM varies depending on the location of the granule. The DEM is clipped from the source layer to the size needed for full granule coverage, or to the extent of the available DEM source data if full coverage is not available. It is then resampled from the native DEM resolution to [SPACING] m for use in RTC processing.

The DEM sources include the National Elevation Dataset (NED) and the Shuttle Radar Topography Mission (SRTM).

The source of the DEM for this particular product is [DEM], which has a native resolution of [RESA] arc seconds (about [RESM] meters).

*Refer to the _dem.tif.xml file for additional information about the specific DEM included with this product, including use and citation requirements.*

__Summary of the DEMs used by ASF for RTC Processing__

The *NED* provides the best available public domain raster elevation data of the conterminous United States, Alaska, Hawaii, and territorial islands in a seamless format. The NED is derived from diverse source data, processed to a common coordinate system and unit of vertical measure. For more information, refer to https://pubs.er.usgs.gov/publication/70201572. To download the data, visit https://viewer.nationalmap.gov/basic and expand the Elevation Products (3DEP) section.

The *SRTM* was flown aboard the space shuttle Endeavour February 11-22, 2000. The National Aeronautics and Space Administration (NASA) and the National Geospatial-Intelligence Agency (NGA) participated in an international project to acquire radar data which were used to create the first near-global set of land elevations. For more information and to access the full SRTM dataset, refer to https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1-arc?qt-science_center_objects=0#qt-science_center_objects.

-------------
## 4. Incidence angle map

The incidence angle map is included with standard products, but is optional when placing a custom order for imagery. This layer is tagged with _inc_map.tif

This map records the incidence angle for each pixel in the RTC image. The incidence angle is the angle between the incident radar beam and the direction perpendicular to the ground surface, expressed in radians.

-------------
## 5. Layover-shadow mask

The layover/shadow mask indicates which pixels in the RTC image have been affected by layover and shadow. This layer is tagged with _ls_map.tif

The pixel values are generated by adding the following values together to indicate which layover and shadow effects are impacting each pixel:
0  Pixel not tested for layover or shadow
1  Pixel tested for layover or shadow
2  Pixel has a look angle less than the slope angle
4  Pixel is in an area affected by layover
8  Pixel has a look angle less than the opposite of the slope angle
16 Pixel is in an area affected by shadow

_There are 17 possible different pixel values, indicating the layover, shadow, and slope conditions present added together for any given pixel._

**The values in each cell can range from 0 to 31:**
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
## 6. ArcGIS-compatible xml metadata files

Each raster in this folder has an associated xml file. It is named with the same filename as the raster, but also includes a .xml extension. When any of the rasters are viewed in ArcGIS, the associated xml file is recognized by the software, and the contents will display in the Item Description (ArcGIS Desktop) or Metadata (ArcGIS Pro) for that raster. Once the file is viewed in ArcGIS, the software will update the xml file to include metadata inherent to the raster (geographic extent, raster format, etc.) along with the descriptive metadata included in the original xml file.

ArcGIS users should take care not to edit the xml files directly, or to change filenames outside of the ArcGIS environment, as it may render the metadata files unreadable by ArcGIS.

Users who do not use ArcGIS to interact with the data may still find the information included in the individual xml files very useful, although the xml tag system makes it look cluttered in a text editor or browser window.

-------------
## 7. General metadata xml file in ISO 19115-2 format

The iso.xml file contains general information about the processing of this product and the resulting files, compliant with ISO 19115-2 standards.

-------------
## 8. Shapefile

The shapefile (comprised of the four files tagged with _shape) contains a polygon indicating the extent of actual data (pixels with values other than NoData).

-------------
## 9. Log file

A textfile is generated during processing, which includes the parameters used and step-by-step processing history for the product. It has a .log extension.

*************
### RTC Processing ###

The basic steps in the radiometric terrain correction process are as follows:

1. Data granule is ingested into the format required by GAMMA software - calibration is done during this step.
2. If required, data is multi-looked to the desired number of looks (default for 30-m products is 6 looks for GRD granules and 3 for SLC; 10-m products default to one look). This product used [LOOKS] look(s).
3. A DEM is extracted from the ASF DEM heap covering the granule to be corrected.
4. A mapping function is created, mapping from DEM space into SAR space.
5. By default, DEM coregistration is not used. When the DEM Matching option is selected for a custom order, the following steps will be performed. *By default the process will skip from step 4 to step 6.*
    1. A simulated SAR image is created.
    2. The simulated SAR image and the real SAR image are coregistered.
    3. The mapping function is updated with the coregistration information.
6. The SAR image is radiometrically corrected using a pixel integration approach to remove radiometric distortions in foreshortening or layover areas.
7. The inversion of the mapping function is used to terrain correct and geocode the radiometrically corrected SAR image.
8. Post processing creates GeoTIFF, PNG and KMZ files, along with associated metadata.

*************
### The Sentinel-1 mission ###

The Sentinel-1A satellite was launched April 3, 2014, and the Sentinel-1B satellite was launched April 25, 2016. The satellites each have a 12-day repeat cycle.

More information about the mission is available at:
https://earth.esa.int/web/guest/missions/esa-operational-eo-missions/sentinel-1

Additional information about Sentinel-1 data, imagery, tools and applications is available at:
 https://asf.alaska.edu/data-sets/sar-data-sets/sentinel-1/

*************
For assistance, contact the Alaska Satellite Facility:
uso@asf.alaska.edu
907-474-5041

-------------
Revised 2020-07-29

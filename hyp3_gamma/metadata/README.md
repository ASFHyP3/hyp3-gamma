# HyP3 Metadata Templates
This directory structure contains the metadata templates for HyP3 products.  

Each different processor for each process has its own set of templates, because there are significant differences in the output files and processing method depending on the processor used (i.e. GAMMA vs. S1TBX).  

Each processor has its own directory, and each of those directories has subdirectories for the process types available for that processor. For example, the GAMMA directory has subdirectories for RTC, InSAR, RGB Decomposition, RGB Difference, and Threshold Change Detection.  

The goal is for each process to have a README file, which gives an overview of the product, including a list of all of the files contained in the product zip file with brief summaries for each file. In addition, some processes have individual xml files for each of the raster files contained in the product archive. They have been designed and formatted to display correctly in the ArcGIS metadata environment (Item Description in ArcGIS Desktop, and Metadata tab in ArcGIS Pro).  

## ArcGIS-Compatible Metadata

In order to render properly in ArcGIS, the xml files must be formatted in a very rigid way. When editing the files in PyCharm, the following settings are necessary for the xml to render properly:



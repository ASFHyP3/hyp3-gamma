# HyP3 Metadata Templates
This directory structure contains the metadata templates for HyP3 products.  

Each different processor for each process has its own set of templates, because there are significant differences in the output files and processing method depending on the processor used (i.e. GAMMA vs. S1TBX).  

Each processor has its own directory, and each of those directories has subdirectories for the process types available for that processor. For example, the GAMMA directory has subdirectories for RTC, InSAR, RGB Decomposition, RGB Difference, and Threshold Change Detection.  

The goal is for each process to have a README file, which gives an overview of the product, including a list of all of the files contained in the product zip file with brief summaries for each file. In addition, some processes have individual xml files for each of the raster files contained in the product archive. They have been designed and formatted to display correctly in the ArcGIS metadata environment (Item Description in ArcGIS Desktop, and Metadata tab in ArcGIS Pro).  

## ArcGIS-Compatible Metadata

In order to render properly in ArcGIS, the xml files must be formatted in a very rigid way. When editing the files in PyCharm, the following settings are necessary for the xml to render properly:

1. In Editor > Code Style > XML > Tabs and Indents, set the Indent values to 0  

![](SettingsImages/Editor_CodeStyle_XML_TabsIndents.JPG)

2. In Editor > Code Style > XML > Other:  
    a. Check the boxes for Keep line breaks and Keep line breaks in text  
    b. Set the Keep blank lines to 0  
    c. Set the Wrap attributes to Do not wrap and remove checks from wrapping and spaces settings  
![](SettingsImages/Editor_CodeStyle_XML_Other.JPG)  

For ease of viewing when editing, in the Editor > General settings, scroll down to Soft Wraps, and make the following changes:  
1. Check the soft wrap files option, and add ; *.xml to the list of file types  
2. Check the option to Use original line's indent for wrapped parts, and set the additional shift if you'd like (I prefer an additional 2 spaces).   
![](SettingsImages/Editor_General_SoftWraps.JPG)  








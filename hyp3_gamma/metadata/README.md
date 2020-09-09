# HyP3 Metadata Templates

Package for generating HyP3 products' metadata

Each different processor for each process has its own set of templates, as there are significant differences in the output files and processing method depending on the processor used (i.e. GAMMA vs. S1TBX).  

Each processor has its own directory, and each of those directories has subdirectories for the process types available for that processor. For example, the GAMMA directory has subdirectories for RTC, InSAR, RGB Decomposition, RGB Difference, and Threshold Change Detection.  

The goal is for each process to have a README text file, which gives an overview of the product, including a list of all of the files contained in the product zip file with brief summaries for each file. In addition, some processes have individual xml files for each of the raster files contained in the product archive. They have been designed and formatted to display correctly in the ArcGIS metadata environment (Item Description in ArcGIS Desktop, and Metadata tab in ArcGIS Pro).  

## ArcGIS-Compatible Metadata

When editing the xml templates in PyCharm, care must be taken to keep them in a format that can be properly parsed by ArcGIS. Most importantly, the hard wrap options must be disabled. There are also some adjustments that can be made to the default settings to improve the display of the xml elements while editing the content.   

Use Ctrl+Alt+S to open the settings window, or select Settings from the File menu.

**_Change the hard wrap settings:_**  

In Editor > Code Style > XML > Other:
1. Check the boxes for Keep line breaks and Keep line breaks in text  
2. Set the "Keep blank lines" option to 0  
3. **Set the Wrap attributes to "Do not wrap" and remove checks from wrapping and spaces settings**

![](docs/imgs/Editor_CodeStyle_XML_Other.JPG)

**_Change the soft wrap settings:_**  

For ease of viewing when editing, in the Editor > General settings, scroll down to Soft Wraps, and make the following changes:  
1. Check the soft wrap files option, and add ; *.xml to the list of file types  
2. Check the option to Use original line's indent for wrapped parts, and set the additional shift if desired

![](docs/imgs/Editor_General_SoftWraps.JPG)


**************
**************
Note that if there are any new lines that are added directly in a text editor by using the return key, they will not render properly in ArcGIS if there are tabs/indentation applied to the code in PyCharm (or any other editor). One way to avoid these issues is to use html formatting tags instead. It's a bit tedious, but it will ensure that the code can be parsed just as well in ArcGIS as in PyCharm.  

If you have text breaks that are NOT formatted in the html tags, another option is to change the tabs and indent settings in PyCharm, then reformat the code. To use this method:

1. In Editor > Code Style > XML > Tabs and Indents, set the Indent and Continuation Indent values to 0 and click OK
2. With the XML file open, select Reformat Code from the Code menu to remove the tab-based indentations.

![](docs/imgs/Editor_CodeStyle_XML_TabsIndents.JPG)

If you use this approach frequently, you may want to create different schemes in the Editor > Code Style > XML settings. For example, save an Edit scheme, which keeps the indentation settings (i.e. Indent: 4, Continuation Indent: 8), and a Write scheme, which sets both to 0. Note that the line break settings in the hard wrap section become more important when using the return character approach.










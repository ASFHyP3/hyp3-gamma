# HyP3 Metadata Templates

Package for generating HyP3 products' metadata.

The goal is for each process to have a README text file, which gives an overview
of the product, including a list of all the files contained in the product zip
file with brief summaries for each file. In addition, some processes have
individual xml files for each of the raster files contained in the product
archive. They have been designed and formatted to display correctly in the
ArcGIS metadata environment (Item Description in ArcGIS Desktop, and Metadata
tab in ArcGIS Pro).  See the "ArcGIS-Compatible Metadata" section below for
formatting tips.

## Generating An Example Set

Because we use `jinja2` templates to generate the product metadata files, it's
not possible to preview your changes live, especially in an ArcGIS environment.
You can generate an example set of metadata to preview your changes by running:

```
python -m hyp3_metadata
```
which will generate an example product containing all of its supported metadata
files. You can use a number of options to tune generation options (e.g., the DEM
used) or where the product files are generated; see
```
python -m hyp3_metadata --help
```
for usage details. 

**Note:** This will generate an *entire* product with pseduo data files
(e.g., GeoTIFFs and Browse images), so you don't need to have a HyP3 product on
hand.

## Generating Data For a HyP3 Product

If you have a current HyP3 product and would like re-generate the metadata for
the product, you can do so using `hyp3_metadata.create_metadata_file_set`. For
example, in a python interpreter, you can:

```python
from datetime import datetime
from pathlib import Path

from hyp3_metadata import create_metadata_file_set_rtc

PRODUCT_DIR = Path('./S1A_IW_20150621T120220_DVP_RTC10_G_saufem_F8E2')
SOURCE_GRANULE = 'S1A_IW_SLC__1SSV_20150621T120220_20150621T120232_006471_008934_72D8'

create_metadata_file_set_rtc(
    product_dir=PRODUCT_DIR,
    granule_name=SOURCE_GRANULE,
    dem_name='GLO-30',
    processing_date=datetime.now(),
    looks=1,  # Typically 6 for GRDH or (resolution / 10) for SLC
    plugin_name='hyp3_gamma',
    plugin_version='X.Y.Z',
    processor_name='GAMMA',
    processor_version='YYYYMMDD',
)
```

**Warning!** This will *overwrite* existing product metadata; we recommend creating
a copy of your product before doing this.

## ArcGIS-Compatible Metadata

When editing the xml templates in PyCharm, care must be taken to keep them in a
format that can be properly parsed by ArcGIS. Most importantly, the **hard wrap
options must be disabled**. There are also some adjustments that can be made to
the default settings to improve the display of the xml elements while editing
the content.   

Use Ctrl+Alt+S to open the settings window, or select Settings from the File menu.

**_Change the hard wrap settings:_**  

In Editor > Code Style > XML > Other:
1. Check the boxes for Keep line breaks and Keep line breaks in text  
2. Set the "Keep blank lines" option to 0  
3. **Set the Wrap attributes to "Do not wrap" and remove checks from wrapping
   and spaces settings**

![](docs/imgs/Editor_CodeStyle_XML_Other.JPG)

**_Change the soft wrap settings:_**  

For ease of viewing when editing, in the Editor > General settings, scroll down
to Soft Wraps, and make the following changes:  
1. Check the soft wrap files option, and add ; *.xml to the list of file types  
2. Check the option to Use original line's indent for wrapped parts, and set the
   additional shift if desired

![](docs/imgs/Editor_General_SoftWraps.JPG)


**************
**************
Note that if there are any new lines that are added directly in a text editor by
using the return key, they will not render properly in ArcGIS if there are
tabs/indentation applied to the code in PyCharm (or any other editor). One way to
avoid these issues is to use html formatting tags instead. It's a bit tedious,
but it will ensure that the code can be parsed just as well in ArcGIS as in PyCharm.  

If you have text breaks that are NOT formatted in the html tags, another option
is to change the tabs and indent settings in PyCharm, then reformat the code.
To use this method:

1. In Editor > Code Style > XML > Tabs and Indents, set the Indent and 
   Continuation Indent values to 0 and click OK
2. With the XML file open, select Reformat Code from the Code menu to remove the
   tab-based indentations.

![](docs/imgs/Editor_CodeStyle_XML_TabsIndents.JPG)

If you use this approach frequently, you may want to create different schemes in
the Editor > Code Style > XML settings. For example, save an Edit scheme, which
keeps the indentation settings (i.e. Indent: 4, Continuation Indent: 8), and a 
Write scheme, which sets both to 0. Note that the line break settings in the hard
wrap section become more important when using the return character approach.










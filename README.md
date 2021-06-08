# Excel-to-SBOL

For further depth and information on Excel-to-SBOL, visit the [Excel-to-SBOL wiki on github](https://github.com/SynBioDex/Excel-to-SBOL/wiki)

**Excel-to-SBOL** is an open source python library providing conversion from [Excel Templates](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates) to [SBOL](https://sbolstandard.org/) documents.

# Table of Contents
- [Installation & How to Use](#installation--how-to-use)
-- Installation
-- How to Use
- [Example Conversion](#example-conversion)
- [Architecture](#architecture)
- [Publishing](#publishing)

<!-- # Interface

![VisBOL Example Visualization](./images/example.png) -->

# Installation & How to use

## Installation

Excel-to-SBOL can be installed using `pip install excel2sbol`

## How to use

**1) Choose an Excel Template**

Choose an excel template from the [templates folder](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates).
We suggest choosing the latest version (dates are given at the end of the file names in the form yyyymmdd). Fill out the template as the instructions indicate.

**2) Run the converter**

Use the code below substituting {things in brackets} with the appropriate values.

```
import excel2sbol.converter_function as conf

conf.converter({template_name}, {file_path_in}, {file_path_out})
```

An example use is:

```
import excel2sbol.converter_function as conf

conf.converter("darpa_template_blank_v005_20220222.xlsx", "C:/Users/Test_User/Downloads/Filled_Template.xlsx", "C:/Users/Test_User/Downloads/Output_SBOL.xml")
```
The use of `os.getcwd()` and `os.path.join` is reccommended for the creation of the file paths.

**3) Use the output file**
The SBOL file that is output can then be used by further [SBOL tools](https://sbolstandard.org/applications/) or uploaded to an SBOL repository like [SynBioHub](https://synbiohub.org/).

# Example Conversion

An [example spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/tests/test_files/pichia_toolkit_KWK_v002.xlsx) that contains data was taken and converted to an [SBOL file](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/tests/test_files/pichia_toolkit_KWK_v002.xml) which was subsequently [uploaded to SynBioHub](https://synbioks.org/public/pichia_toolkit_KWK/pichia_toolkit_KWK_collection/1).

**Example Spreadsheet**
![Example Spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/read-me-stuff/images/excel2sbol_spreadsheet.PNG)

**Example SBOL**
![Example SBOL](https://github.com/SynBioDex/Excel-to-SBOL/blob/read-me-stuff/images/excel2sbol_xml.PNG)

**Example SynBioHub Upload**
![Example SynBioHub](https://github.com/SynBioDex/Excel-to-SBOL/blob/read-me-stuff/images/excel2sbol_synbiohub.PNG)

# Architecture

# Publishing

To publish the latest version of the back-end:

1) Navigate to the back-end directory: `cd backend`
2) Open `package.json`
3) Update the version number
4) Run `npm publish`

To publish the latest version of the front-end:

1) Navigate to the front-end directory: `cd frontend`
2) Run `npm run build`
2) Open `package.json`
3) Update the version number
4) Run `npm publish`
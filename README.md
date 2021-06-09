# Excel-to-SBOL

For further depth and information on Excel-to-SBOL, including how to contribute to the project, visit the [Excel-to-SBOL wiki on github](https://github.com/SynBioDex/Excel-to-SBOL/wiki)

**Excel-to-SBOL** is an open source python library providing conversion from [Excel Templates](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates) to [SBOL](https://sbolstandard.org/) documents.

# Table of Contents
- [Installation & How to Use](#installation--how-to-use)
    - [Installation](#installation)
    - [How to Use](#how-to-use)
- [Example Conversion](#example-conversion)
- [Architecture](#architecture)
- [Publishing](#publishing)

<!-- # Interface

![VisBOL Example Visualization](./images/example.png) -->

# Installation & How to use

## Installation

Excel-to-SBOL can be installed using `pip install excel2sbol`

To get the latest version you can use `git clone https://github.com/SynBioDex/Excel-to-SBOL` followed by `cd .\excel2sbol` and `python setup.py install`

## How to use

**1) Choose an Excel Template**

Choose an excel template from the [templates folder](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates).
We suggest choosing the latest version (dates are given at the end of the file names in the form yyyymmdd). Fill out the template as the instructions indicate.

**2) Install the Converter**
There are several ways to install the converter. The easiest is via pip: `pip install excel2sbol` but it can also be done by [cloning the repository](https://github.com/SynBioDex/Excel-to-SBOL/wiki/2.-Cloning-From-GitHub).

**3) Run the Converter**

Use the code below substituting {things in brackets} with the appropriate values.

```
import excel2sbol.converter_function as conf

conf.converter({template_name}, {file_path_in}, {file_path_out})
```

An example use is:

```
import excel2sbol.converter_function as conf

conf.converter("darpa_template_blank_v005_20220222.xlsx",
               "C:/Users/Test_User/Downloads/Filled_Template.xlsx",
               "C:/Users/Test_User/Downloads/Output_SBOL.xml")
```
The use of `os.getcwd()` and `os.path.join` is reccommended for the creation of the file paths.

**4) Use the output file**
The SBOL file that is output can then be used by further [SBOL tools](https://sbolstandard.org/applications/) or uploaded to an SBOL repository like [SynBioHub](https://synbiohub.org/).

# Example Conversion

An [example spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/tests/test_files/pichia_toolkit_KWK_v002.xlsx) that contains data was taken and converted to an [SBOL file](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/tests/test_files/pichia_toolkit_KWK_v002.xml) which was subsequently [uploaded to SynBioHub](https://synbioks.org/public/pichia_toolkit_KWK/pichia_toolkit_KWK_collection/1).

**Example Spreadsheet**
![Example Spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/excel2sbol_spreadsheet.PNG)

**Example SBOL**
![Example SBOL](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/excel2sbol_xml.PNG)

**Example SynBioHub Upload**
![Example SynBioHub](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/excel2sbol_synbiohub.PNG)

# Architecture

The [repository architecture](https://github.com/SynBioDex/Excel-to-SBOL/wiki/5.-Excel2SBOL-Architecture#repository-architecture) is described in the wiki.

This repository contains the [excel2sbol module](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/utils), [resources](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources) to use it (such as [templates](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates)), and the [tests](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/tests) for all of the functions it contains.

Excel-to-SBOL works by splitting the spreadsheet into three parts:
1. Overview information (e.g. Collection Name, Date Created, and Authors)
2. Design Description: The overview of the design collection
3. Part table: The table of parts provided

Each of the three spreadsheet parts is processed individually.

The part table is the most complex as it requires both the column_definitions sheet to process and the other ontology sheets.

The architecture is:
- [helper_functions.py](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/utils/helper_functions.py)
    - Function: **col_to_num**, converts excel column names like AA to zero indexed numbers like 26
    - Function: **check_name**, ensures that a string is alphanumeric and contains no special characters (including spaces) apart from '_'
    - Function: **truthy_strings**, converts several different kinds of True or False input to the boolean True or False
-  [column_functions.py](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/utils/column_functions.py)
    - Class: **sbol_methods**, a class which is used to implement a switch statement to process each of the excel columns. For example if sbh_sourceOrganism is present in the column_definitions sheet then sbol_methods.sbh_sourceOrganism() will automatically be called and used to transform the data as needed.
    - Class: **column**, creates a column object to make handelling data associated with the column easier. This includes the creation of a lookup dictionary if specified in the dictionary it takes as input.
    - Dependency: helper_functions.py
- [initialise_functions.py](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/utils/initialise_functions.py)
    - Function: **read_in_sheet**, reads in the excel spreadsheet and splits it into the above mentioned three parts for further processing.
    - Class: **table**, takes the dictionary produced by read_in_sheet and calls the column class method to create a column object for every column
    - Dependency: column_functions.py
- [converter_function.py](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/utils/converter_function.py)
    - Function: **converter**, relies on all the above functions to go from a spreadsheet, process all the parts individually, and output an SBOL file.
    - Dependency: helper_functions.py, column_functions.py, initialise_functions.py


# Publishing

A new version of the python package is automatically published via [the python-publish GitHub action](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/.github/workflows/python-publish.yml) whenever a new release is created.

Alternatively you can also make changes to the package and then use it locally:
1. Clone the directory: `git clone https://github.com/SynBioDex/Excel-to-SBOL`
2. Change to the excel2sbol folder: `cd .\excel2sbol`
3. Install an editable version of the package: `python -m pip install -e .` (will overwrite the directory in site-packages with a symbolic link to the locations repository). If a virtual environment is being used the python -m can be left off.

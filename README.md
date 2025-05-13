# Excel-to-SBOL

**Excel-to-SBOL** is an open source python library that converts [Excel Templates](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates) to [SBOL](https://sbolstandard.org/) documents.

A similar utility developed for SBOL3 support (developed by Jake Beal) is in [SBOL-utilities](https://github.com/SynBioDex/SBOL-utilities).

For further depth and information on Excel-to-SBOL, including how to contribute to the project, visit the [Excel-to-SBOL wiki on github](https://github.com/SynBioDex/Excel-to-SBOL/wiki)



# Table of Contents
- [Installation & How to Use](#installation--how-to-use)
    - [Installation](#installation)
    - [How to Use](#how-to-use)
- [Example Conversion](#example-conversion)
- [Architecture](#architecture)
- [Publishing](#publishing)

<!-- # Interface

![VisBOL Example Visualization](./images/example.png) -->

# Excel-to-SBOL: Installation & How to use

## Installation

Excel-to-SBOL can be installed using `pip install excel2sbol`

To get the latest version you can use `git clone https://github.com/SynBioDex/Excel-to-SBOL` followed by `cd .\excel2sbol` and `python setup.py install`

## How to use

**1) Choose an Excel Template**
Choose an excel template from the [templates folder](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates).
We suggest choosing the latest version. Fill out the template as the instructions indicate. 

**2) Install the Converter**
There are several ways to install the converter. The easiest is via pip: `pip install excel2sbol` but it can also be done by [cloning the repository](https://github.com/SynBioDex/Excel-to-SBOL/wiki/2.-Cloning-From-GitHub).

**3) Run the Converter**
Use the code below to run the converter. Converter file needs to be within the same directory as the Excel template.
The following script asks the user for the name of the input file, version of SBOL to use, and offers the option to sign in to gain access to private repositories.

If you want to use the tool in offline mode for a custom SynBioHub instance, leave the "Domain" field empty on the spreadsheet "Welcome page".

[Converter File](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/tests/test_files/Excel2SBOLConverter.py)

Tip: the use of `os.getcwd()` and `os.path.join` is recommended for the creation of the file paths. This is safer from a cybersecurity stand point and provide better operating system interoperability.

**4) Use the output file**
The SBOL file that is output can then be used by further [SBOL tools](https://sbolstandard.org/applications/) or uploaded to an SBOL repository like [SynBioHub](https://synbiohub.org/).

# Example Conversion

A data-filled [spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/resources/templates/Sample_template_Excel2SBOL.xlsm) was converted to an [SBOL file](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/excel2sbol/resources/templates/Sample_template_Excel2SBOL.xml).

**Example Spreadsheet**
![Example Spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/sample_template.png)

**Example SBOL**
![Example SBOL](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/sample_xml.png)



# Architecture

The [repository architecture and module architecture](https://github.com/SynBioDex/Excel-to-SBOL/wiki/4.-Excel2SBOL-Module-and-Repository-Architecture) are described in the wiki.

# Publishing

A new version of the python package is automatically published via [the python-publish GitHub action](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/.github/workflows/python-publish.yml) whenever a new release is created.

Alternatively you can also make changes to the package and then use it locally:
1. Clone the directory: `git clone https://github.com/SynBioDex/Excel-to-SBOL`
2. Change to the excel2sbol folder: 
                                   
cd ./Excel_to_SBOL/excel2sbol
                                   
3. Install an editable version of the package: `python -m pip install -e .` (will overwrite the directory in site-packages with a symbolic link to the locations repository). If a virtual environment is being used the python -m can be left off.

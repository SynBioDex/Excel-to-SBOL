# Excel-to-SBOL

**Excel-to-SBOL** is an open source python library that converts [Excel Templates](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/resources/templates) to [SBOL](https://sbolstandard.org/) documents.

A similar utility developed for SBOL3 support (developed by Jake Beal) is in [SBOL-utilities](https://github.com/SynBioDex/SBOL-utilities).

For further depth and information on Excel-to-SBOL, including how to contribute to the project, visit the [Excel-to-SBOL wiki on github](https://github.com/SynBioDex/Excel-to-SBOL/wiki)



# Table of Contents
- [Installation & How to Use](#installation--how-to-use)
    - [Installation](#installation)
    - [Run the GUI](#run-the-gui)
    - [How to Use](#how-to-use)
- [Example Conversion](#example-conversion)
- [Architecture](#architecture)
- [Publishing](#publishing)

<!-- # Interface

![VisBOL Example Visualization](./images/example.png) -->

# Excel-to-SBOL: Installation & How to use

## Installation

Excel-to-SBOL requires Python 3.9 or later. We recommend installing it in a virtual environment so the converter dependencies do not conflict with other Python projects.

### Install the released package

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install excel2sbol
```

### Install from a source checkout

Use this option when you want the latest repository version or want to run the bundled GUI.

```bash
git clone https://github.com/SynBioDex/Excel-to-SBOL.git
cd Excel-to-SBOL
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

To include the Python GUI dependency while installing from source, install the `gui` extra instead:

```bash
python -m pip install -e ".[gui]"
```

## Run the GUI

The repository includes a pywebview-based graphical interface in the `ui/` directory. Install the project from a source checkout with the GUI extra first, then launch the app from the repository root:

```bash
python ui/app.py
```

When the window opens:

1. Choose the Excel-to-SBOL template type you want to use, or select an existing completed template.
2. Confirm or enter the SBOL version, SynBioHub domain, and email metadata.
3. Pick an output folder.
4. Start the conversion or spreadsheet generation from the GUI.

Notes:

- On Linux, pywebview may require system WebKit/GTK packages supplied by your distribution. If the GUI does not open, install the pywebview Linux prerequisites for your desktop environment and rerun `python ui/app.py`.
- The GUI should be run from a cloned repository because the `ui/` assets are not part of the published `excel2sbol` library package.
- If you only need the library/converter in scripts, `python -m pip install excel2sbol` is sufficient; the GUI extra is only needed to run `ui/app.py`.

## How to use

**1) Choose an Excel Template**
Choose an excel template from the [templates folder](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/resources/templates).
We suggest choosing the latest version. Fill out the template as the instructions indicate. 

**2) Install the Converter**
There are several ways to install the converter. The easiest is via pip: `pip install excel2sbol` but it can also be done by [cloning the repository](https://github.com/SynBioDex/Excel-to-SBOL/wiki/2.-Cloning-From-GitHub).

**3) Run the Converter**
Use the code below to run the converter. Converter file needs to be within the same directory as the Excel template.
The following script asks the user for the name of the input file, version of SBOL to use, and offers the option to sign in to gain access to private repositories.

If you want to use the tool in offline mode for a custom SynBioHub instance, leave the "Domain" field empty on the spreadsheet "Welcome page".

[Converter File](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/resources/Excel2SBOLConverter.py)

Tip: the use of `os.getcwd()` and `os.path.join` is recommended for the creation of the file paths. This is safer from a cybersecurity stand point and provide better operating system interoperability.

**4) Use the output file**
The SBOL file that is output can then be used by further [SBOL tools](https://sbolstandard.org/applications/) or uploaded to an SBOL repository like [SynBioHub](https://synbiohub.org/).

# Example Conversion

A data-filled [spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/resources/templates/Sample_template_Excel2SBOL.xlsm) was converted to an [SBOL file](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/resources/templates/Sample_template_Excel2SBOL.xml).

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
                                   
cd ./Excel_to_SBOL/src/excel2sbol
                                   
3. Install an editable version of the package: `python -m pip install -e .` (will overwrite the directory in site-packages with a symbolic link to the locations repository). If a virtual environment is being used the python -m can be left off.

# Excel2SBOL Paper

An updated version of the Excel template referenced in the paper [Excel–SBOL Converter: Creating SBOL from Excel Templates and Vice Versa](https://pubs.acs.org/doi/full/10.1021/acssynbio.2c00521) can be found [here](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/tests/test_files/sb2c00521_si_001.xlsx).

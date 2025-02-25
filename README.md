# Excel-to-SBOL

**Excel-to-SBOL** is an open source python library that converts [Excel Templates](https://github.com/SynBioDex/Excel-to-SBOL/tree/master/excel2sbol/resources/templates) to [SBOL](https://sbolstandard.org/) documents.

A similar utility developed for SBOL3 support (developed by Jake Beal) is [SBOL-utilities](https://github.com/SynBioDex/SBOL-utilities).

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
```

# Excel2SBOL Converter

import excel2sbol.converter as conf
from datetime import datetime
import excel_sbol_utils.library2 as exutil2
import getpass
import requests

# Ask the user for the name of the input file
input_file = input("Please enter the name of the input file: ")

# Get the current date
current_date = datetime.now().strftime("%y.%m.%d.%H.%M.%S")

# Add the current date to the output file name
output_file = "Output_SBOL_" + current_date + ".xml"

# Ask the user for the version of SBOL to use
while True:
    sbol_version = input("Please enter the version of SBOL to use (2 or 3): ")
    if sbol_version in ['2', '3']:
        sbol_version = int(sbol_version)
        break
    else:
        print("Invalid input. Please enter either 2 or 3.")

# Ask the user if they want to sign in or not to use private repos
while True:
    signin_permission = input("Do you want to sign in? (y/n): ")
    if signin_permission in ['y', 'n']:
        break
    else:
        print("Invalid input. Please enter either y or n.")

if signin_permission == 'y':
    for attempt in range(1, 3 + 1):
        domain = input("Please enter the domain name: ")
        domain = domain.rstrip("/")
        try:
            response = requests.get(domain)
            response.raise_for_status()  
            print("URL reached successfully")
            break
        except requests.exceptions.RequestException as e:
            print(f"Wrong domain name. Attempt {attempt} of 3.")
            if attempt == 3:
                print("Maximum attempts reached. Exiting the program.")
                exit()

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        user_email = input("Please enter your email address: ")
        user_password = getpass.getpass("Please enter your password: ")
        

        login_response = requests.post(
            f"{domain}/login",
            headers={'Accept': 'plain/text'},
            data={'email': user_email, 'password': user_password}
        )

        if login_response.status_code == 200:
            print("Login successful.")
            conf.converter(input_file, output_file, sbol_version=sbol_version, username=user_email, password=user_password, url=domain)
            break
        else:
            print(f"Login unsuccessful. Attempt {attempt} of {max_attempts}.")
            if attempt == max_attempts:
                print("Maximum login attempts reached. Exiting the program.")
                exit()
else:
    conf.converter(input_file, output_file, sbol_version=sbol_version)

```

Tip: the use of `os.getcwd()` and `os.path.join` is reccommended for the creation of the file paths. This is safer from a cybersecurity stand point and provide better operating system interoperability.

**4) Use the output file**
The SBOL file that is output can then be used by further [SBOL tools](https://sbolstandard.org/applications/) or uploaded to an SBOL repository like [SynBioHub](https://synbiohub.org/).

# Example Conversion

A data-filled [spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/readme/excel2sbol/resources/templates/Example.xlsm) was converted to an [SBOL file](https://github.com/SynBioDex/Excel-to-SBOL/blob/readme/excel2sbol/tests/test_files/Example.xml).

**Example Spreadsheet**
![Example Spreadsheet](https://github.com/SynBioDex/Excel-to-SBOL/blob/readme/images/sample-template.png)

**Example SBOL**
![Example SBOL](https://github.com/SynBioDex/Excel-to-SBOL/blob/readme/images/sample-xml.png)



# Architecture

The [repository architecture and module architecture](https://github.com/SynBioDex/Excel-to-SBOL/wiki/4.-Excel2SBOL-Module-and-Repository-Architecture) are described in the wiki.

# Publishing

A new version of the python package is automatically published via [the python-publish GitHub action](https://github.com/SynBioDex/Excel-to-SBOL/blob/master/.github/workflows/python-publish.yml) whenever a new release is created.

Alternatively you can also make changes to the package and then use it locally:
1. Clone the directory: `git clone https://github.com/SynBioDex/Excel-to-SBOL`
2. Change to the excel2sbol folder: 
                                   
cd ./Excel_to_SBOL/excel2sbol
                                   
3. Install an editable version of the package: `python -m pip install -e .` (will overwrite the directory in site-packages with a symbolic link to the locations repository). If a virtual environment is being used the python -m can be left off.

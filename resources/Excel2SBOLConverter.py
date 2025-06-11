# # Excel2SBOL Converter

# # Excel2SBOL Converter

import os
import glob
import excel2sbol as conf
from datetime import datetime
#import library2 as exutil2
import getpass
import requests
import pandas as pd


# Scan for Excel files in the current directory, ignoring temporary/cache files starting with "~$"
all_excels = glob.glob("*.xlsx") + glob.glob("*.xlsm")
excel_files = sorted([f for f in all_excels if not os.path.basename(f).startswith("~$")])

if not excel_files:
    print("No Excel files found in the current directory. Exiting.")
    exit()

if len(excel_files) == 1:
    input_file = excel_files[0]
    print(f"One Excel file found: {input_file}")
else:
    print("Multiple Excel files found:")
    for idx, fname in enumerate(excel_files, 1):
        print(f"{idx}. {fname}")
    while True:
        try:
            file_index = int(input("Enter the number of the file to convert: "))
            if 1 <= file_index <= len(excel_files):
                input_file = excel_files[file_index - 1]
                break
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid number.")

# Get the current date
current_date = datetime.now().strftime("%y.%m.%d.%H.%M.%S")


# Set output file name based on input file
base_name = os.path.splitext(input_file)[0]
output_file = f"{base_name}_" + current_date + ".xml"

# Retrieve SBOL version from Excel 'Init' sheet cell B1
try:
    df_init = pd.read_excel(input_file, sheet_name="Init", header=None, usecols="B", nrows=1)
    sbol_version = int(df_init.iloc[0, 0])
    print(f"Using SBOL version {sbol_version} from 'Init' sheet cell B1")
except Exception as e:
    print(f"Failed to read SBOL version from Excel file: {e}")
    # Fallback to user prompt if reading fails
    while True:
        sbol_version_input = input("Please enter the version of SBOL to use (2 or 3): ")
        if sbol_version_input in ['2', '3']:
            sbol_version = int(sbol_version_input)
            break
        else:
            print("Invalid input. Please enter either 2 or 3.")

# Ask the user if they want to sign in to use private repos
while True:
    signin_permission = input("Do you want to sign in? (y/n): ")
    if signin_permission in ['y', 'n']:
        break
    else:
        print("Invalid input. Please enter either y or n.")

if signin_permission == 'y':
    # Retrieve domain from Excel 'welcome' sheet cell C16
    try:
        df_welcome = pd.read_excel(input_file, sheet_name="welcome", header=None, usecols="C", nrows=16)
        raw_domain = df_welcome.iloc[15, 0]
        if pd.isna(raw_domain) or str(raw_domain).strip() == "":
            raise ValueError("Empty domain")
        domain = str(raw_domain).rstrip("/")
        print(f"Using domain {domain} from 'welcome' sheet cell C16")
    except Exception as e:
        print(f"Failed to read domain from Excel file: {e}")
        # Fallback to user prompt
        for attempt in range(1, 4):
            domain = input("Please enter the domain name: ").rstrip("/")
            try:
                response = requests.get(domain)
                response.raise_for_status()
                print("URL reached successfully")
                break
            except requests.exceptions.RequestException:
                print(f"Wrong domain name. Attempt {attempt} of 3.")
                if attempt == 3:
                    print("Maximum attempts reached. Exiting the program.")
                    exit()

    # Determine user email source
    while True:
        self_generated = input("Is this file one you generated? (y/n): ")
        if self_generated in ['y', 'n']:
            break
        else:
            print("Invalid input. Please enter either y or n.")

    if self_generated == 'y':
        # Retrieve email from Excel 'welcome' sheet cell C8
        try:
            df_email = pd.read_excel(input_file, sheet_name="welcome", header=None, usecols="C", nrows=8)
            raw_email = df_email.iloc[7, 0]
            if pd.isna(raw_email) or str(raw_email).strip() == "":
                raise ValueError("Empty email")
            user_email = str(raw_email)
            print(f"Using email {user_email} from 'welcome' sheet cell C8")
        except Exception as e:
            print(f"Failed to read email from Excel file: {e}")
            user_email = input("Please enter your email address: ")
    else:
        user_email = input("Please enter your email address: ")

    # Prompt for password
    for attempt in range(1, 4):
        user_password = getpass.getpass("Please enter your password: ")
        login_response = requests.post(
            f"{domain}/login",
            headers={'Accept': 'plain/text'},
            data={'email': user_email, 'password': user_password}
        )
        if login_response.status_code == 200:
            print("Login successful.")
            conf.converter(input_file, output_file, sbol_version=sbol_version,
                           username=user_email, password=user_password, url=domain)
            break
        else:
            print(f"Login unsuccessful. Attempt {attempt} of 3.")
            if attempt == 3:
                print("Maximum login attempts reached. Exiting the program.")
                exit()
else:
    conf.converter(input_file, output_file, sbol_version=sbol_version)

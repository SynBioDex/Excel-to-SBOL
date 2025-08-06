# # Excel2SBOL Converter

# import excel2sbol.converter as conf

from excel2sbol.converter import converter
from datetime import datetime
import excel2sbol.library2 as exutil2
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
            # conf.converter(input_file, output_file, sbol_version=sbol_version, username=user_email, password=user_password, url=domain)
            converter(input_file, output_file, sbol_version=sbol_version, username=user_email, password=user_password, url=domain)
            break
        else:
            print(f"Login unsuccessful. Attempt {attempt} of {max_attempts}.")
            if attempt == max_attempts:
                print("Maximum login attempts reached. Exiting the program.")
                exit()
else:
    # conf.converter(input_file, output_file, sbol_version=sbol_version)
    converter(input_file, output_file, sbol_version=sbol_version)



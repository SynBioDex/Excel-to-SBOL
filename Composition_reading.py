#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 14:57:34 2020

@author: isapoetzsch
"""
#Set up
import os
import pandas as pd
from excel2sbol import quality_check_metadata, load_libraries, get_data
from excel2sbol import get_parts, check_name, write_sbol_comp, fix_msec_sbol

cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
path_filled = os.path.join(cwd, "darpa_template.xlsx")
path_blank = os.path.join(cwd, "templates/darpa_template_blank.xlsx")


#Load Data
startrow_composition = 9
sheet_name = "Composite Parts"
nrows = 8
use_cols = [0,1]
#read in whole composite sheet below metadata
table = pd.read_excel (path_filled, sheet_name = sheet_name, 
                        header = None, skiprows = startrow_composition)

#Load Metadata
filled_composition_metadata = pd.read_excel (path_filled, sheet_name = sheet_name,
                              header= None, nrows = nrows, usecols = use_cols)
blank_composition_metadata = pd.read_excel (path_blank, sheet_name = sheet_name,
                              header= None, nrows = nrows, usecols = use_cols)

#Compare the metadata to the template
quality_check_metadata(filled_composition_metadata, blank_composition_metadata)

#Load Libraries required for Parts
libraries = load_libraries(table)

#Loop over all rows and find those where each block begins
compositions, list_of_rows = get_data(table)
            
#Extract parts from table
compositions, all_parts = get_parts(list_of_rows, table, compositions)

#Check if Collection names are alphanumeric and separated by underscore
compositions = check_name(compositions)

#Create sbol
doc = write_sbol_comp(libraries, compositions)
# doc.write("Compositions1.xml")

# #Edit igem2sbol activity to include milliseconds and avoid validation error
# #The underlying issue was already reported
# with open("Compositions1.xml", "r") as file:
#     data = file.read()
    
# with open("Compositions1.xml", "w") as file:
#     data = data.replace("<prov:endedAtTime>2017-03-06T15:00:00+00:00</prov:endedAtTime>", "<prov:endedAtTime>2017-03-06T15:00:00.000+00:00</prov:endedAtTime>")
#     file.write(data)
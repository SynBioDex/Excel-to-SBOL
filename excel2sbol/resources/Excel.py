#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 18:33:56 2020

@author: isapoetzsch
"""

#Setup
import pandas as pd
import os
from excel2sbol.utils.converter_utils import read_library, quality_check, write_sbol


cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
path_blank = os.path.join(cwd, "templates/darpa_template_blank.xlsx")
path_filled = None #os.path.join("C:\\Users\\JVM\\Downloads\\build-request-template_BsPpVn.xlsx")
file_path_out = None #"C:\\Users\\JVM\\Downloads\\converted.xml"

#Read in template and filled spreadsheet for the Parts library
start_row = 13
nrows = 8
description_row = 9

filled_library, filled_library_metadata, filled_description = read_library(path_filled,  
                start_row = start_row, nrows = nrows, description_row = description_row)
blank_library, blank_library_metadata, blank_description = read_library(path_blank,  
                start_row = start_row, nrows = nrows, description_row = description_row)


ontology = pd.read_excel(path_filled, header=None, sheet_name= "Ontology Terms", skiprows=3, index_col=0)
ontology= ontology.to_dict("dict")[1]


quality_check(filled_library, blank_library, filled_library_metadata, blank_library_metadata, filled_description, blank_description)

#Create SBOL document
doc = write_sbol(filled_library, filled_library_metadata, filled_description, ontology)
doc.write(file_path_out)
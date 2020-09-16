#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 18:33:56 2020

@author: isapoetzsch
"""

#Setup
import pandas as pd
import numpy as np
import os
import math
import logging
import col_to_excel
from col_to_excel import col_to_excel
import sbol2
from sbol2 import Document, Component, ComponentDefinition
from sbol2 import BIOPAX_DNA, Sequence, SBOL_ENCODING_IUPAC, Config





#Read in template and filled spreadsheet for the Parts library
def read_library(path, start_row, nrows, description_row, use_cols = [0, 1], 
                 sheet_name = "Library", description_col = [0]):
    """
    the function reads and formats an excel spreadsheet

    Parameters
    ----------
    path : STRING
        Path to Excel Spreadsheet
    start_row : INTEGER
        Defines first row to be read for the parts table
    nrows: INTEGER
        Defines number of rows to be read for the metadata section
    usecols: LIST, default = [0, 1]
        Defines which columns should be read for the metadata section (note column A is 0)
    sheet_name: STRING, default = "Library"
        Defines the name of the spreadsheet that should be read
    description_row: INTEGER
        Defines the row where the description is situated
    description_col: INTEGER, default = 0
        Defines which column the description is in
    

    Returns
    -------
     basic_DNA_parts: DATAFRAME
         The parts table with headers from row=start_row and data from all rows after that.
     metadata: DATAFRAME, (usecols x nrows)
         A header less table of length nrows and width usecols
    description: DATAFRAME, (description_col x 1)
         A table consisting usually of a single cell and the header "Design Description"
     
     Example
     -------
     cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
     path_filled = os.path.join(cwd, "darpa_template.xlsx")
     filled_library, filled_metadata, filled_description = read_library(path_filled,  
                 start_row = 13, nrows = 8, description_row = 9)

    """
    basic_DNA_parts = pd.read_excel (path, sheet_name = sheet_name, 
                                     header= 0, skiprows = start_row)
    
    metadata = pd.read_excel (path, sheet_name = sheet_name,
                              header= None, nrows = nrows, usecols = use_cols)
    
    description = pd.read_excel (path, sheet_name = sheet_name, skiprows = description_row,
                                 nrows = 1, usecols = description_col)
    
    return (basic_DNA_parts, metadata, description)


#Description
def quality_check(filled_library, blank_library, filled_metadata, blank_metadata, filled_description,
                  blank_description, nrows, description_row, description_col=[0], use_cols = [0,1]):
    """
    the function compares the edited excel spreadsheet with the template

    Parameters
    ----------
    filled_library : DATAFRAME
        Dataframe containing the library part data
    blank_library : DATAFRAME
        Dataframe containing the library part template
    filled_metadata : DATAFRAME
        Dataframe containing the metadata
    blank_metadata : DATAFRAME
        Dataframe containing the metadata template
    filled_description : DATAFRAME
        Dataframe containing the description data
    blank_description : DATAFRAME
        Dataframe containing the description template
    nrows: INTEGER
        Defines number of rows to be read for the metadata section
    description_row: INTEGER
        Defines the row where the description is situated
    description_col: INTEGER, default = 0
        Defines which column the description is in
    usecols: LIST, default = [0, 1]
        Defines which columns were used read for the metadata section (note column A is 0)

    Returns
    -------
     basic_DNA_parts: STRING
         The parts table with headers from row=start_row and data from all rows after that.
         
     
     Example
     -------
     cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
     path_filled = os.path.join(cwd, "darpa_template.xlsx")
     filled_library, filled_metadata, filled_description = read_library(path_filled,  
                 start_row = 13, nrows = 8, description_row = 9)

    """
    if filled_description.columns != "Design Description":
        col = col_to_excel(description_col+1)
        logging.warning(f"{col}{description_row+1} has been corrupted, it should be labelled 'Design Description' with the description in A11")
    
    #Metadata
    comparison = np.where((filled_metadata == blank_metadata)|(blank_metadata.isna()), True, False)
    excel_cell_names = []
    for column in range(0, len(use_cols)):
        for row in range(0, comparison.shape[0]):
            col = use_cols[column]
            excel_cell_names.append(f"{col_to_excel(col+1)}{row+1}")
    excel_cell_names = np.reshape(excel_cell_names, comparison.shape, order='F')
    excel_cell_names = pd.DataFrame(excel_cell_names)
    excel_cell_names.where(np.logical_not(comparison))
    
    if not(comparison.all()) :
        logging.warning("Some cells do not match the template")
        for number in range(0, nrows-1) :
            if filled_metadata.iloc[number, 0] != blank_metadata.iloc[number, 0]:
                logging.warning(f"""The excel cell {excel_cell_names.loc[number, 0]} has been corrupted and 
                      should contain {blank_metadata.iloc[number, 0]}""")
                      
    #Library data
    filled_columns = set(filled_library.columns)
    blank_columns = set(blank_library.columns)
    
    if not(blank_columns.issubset(filled_columns)) :
        missing_columns = blank_columns - filled_columns
        logging.warning(f"Some of the required columns are missing. They are {missing_columns}.")
    return
#quality_check(filled_library, blank_library, filled_library_metadata, blank_library_metadata, filled_description, blank_description)

#Create SBOL document
def write_sbol(filled_library, filled_library_metadata, filled_description, ontology, molecule_type = BIOPAX_DNA,
               part_column = "Part Name", sequence_column = "Sequence", description_column = "Description (Optional)",
               role_column = "Role", length_column = "length (bp)"):
    """
    the function reads an excel spreadsheet and converts it into valid sbol

    Parameters
    ----------
    filled_library : DATAFRAME
        Dataframe containing the library part data
    filled_metadata : DATAFRAME
        Dataframe containing the metadata
    filled_description : DATAFRAME
        Dataframe containing the description data
    ***ONTOLOGY
    molecule_type : STRING, default = BIOPAX_DNA
        Molecule type
    part_column : STRING, default = "Part Name"
        Name of the dataframe column that contains the part names
    sequence_column : STRING, default = "Sequence"
        Name of the dataframe column that contains the sequence
    description_column : STRING, default = "Description (Optional)"
        Name of the dataframe column that contains the library description
    role_column : STRING, default = "Role"
        Name of the dataframe column that contains the Role
    length_column : STRING, default = "length (bp)"
        Name of the dataframe column that contains the sequence length
    

    Returns
    -------
     doc: SBOL Document
         Document containing all components and sequences
     
     Example
     -------
     Doc = write_sbol(filled_library, filled_library_metadata, filled_description)

    """
    doc = Document()
    Config.setOption('sbol_typed_uris', False)
    
    #Define SBOL object and components
    #Parts Library
    #molecule_type = BIOPAX_DNA #Change later
    #part_column = "Part Name"
    #sequence_column = "Sequence"
    #description_column = "Description (Optional)"
    #role_column = "Role"
    #length_column = "length (bp)"
    
    for index, row in filled_library.iterrows():
        component = ComponentDefinition(row[part_column], molecule_type)
        component.roles = ontology[row[role_column]]
        component.name = row[part_column]
        if not(pd.isnull(row[description_column])):
            component.description = row[description_column]
        doc.addComponentDefinition(component)
        
        row[sequence_column] = "".join(row[sequence_column].split())
        row[sequence_column] = row[sequence_column].replace( u"\ufeff", "")
        row[sequence_column] = row[sequence_column].lower()
        if len(row[sequence_column]) != row[length_column]:
            logging.warning(f"The length of the sequence {row[part_column]} does not coincide with the length in the corresponding column 'length (bp)'")
        sequence = Sequence(f"{row[part_column]}_sequence", row[sequence_column], SBOL_ENCODING_IUPAC)
        doc.addSequence(sequence)
        component.sequences = sequence
    
    #Metadata
    doc.description = str(filled_description.values)
    doc.name = filled_library_metadata.iloc[0, 1]
    
    # doc.write('SBOL_testcollection.xml')
    
    return(doc)
    


# cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
# path_blank = os.path.join(cwd, "templates/darpa_template_blank.xlsx")
# path_filled = os.path.join("C:\\Users\\JVM\\Downloads\\build-request-template_BsPpVn.xlsx")
# file_path_out = "C:\\Users\\JVM\\Downloads\\converted.xml"

# start_row = 13
# nrows = 8
# description_row = 9

# filled_library, filled_library_metadata, filled_description = read_library(path_filled,  
#                 start_row = start_row, nrows = nrows, description_row = description_row)
# blank_library, blank_library_metadata, blank_description = read_library(path_blank,  
#                 start_row = start_row, nrows = nrows, description_row = description_row)


# ontology = pd.read_excel(path_filled, header=None, sheet_name= "Ontology Terms", skiprows=3, index_col=0)
# ontology= ontology.to_dict("dict")[1]
# doc = write_sbol(filled_library, filled_library_metadata, filled_description, ontology)
# doc.write(file_path_out)
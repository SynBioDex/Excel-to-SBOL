#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:03:38 2020

@author: isapoetzsch
"""
import pandas as pd
import numpy as np
import os
import logging
import re
import sbol2
from sbol2 import Document, Collection, Component, ComponentDefinition
from sbol2 import BIOPAX_DNA, Sequence, SBOL_ENCODING_IUPAC, Config

def col_to_excel(col):
    """
    Converts the column number to the excel column name (A, B, ... AA  etc)

    Parameters
    ----------
    col : INTEGER
        The number of the column to convert. Note that 1 converts to A

    Returns
    -------
    excel_col : STRING
        The string which describes the name of the column in Excel
        
    Example
    -------
    print(col_to_excel(9))

    """
    excel_col = ""
    div = col 
    
    while div>0:
        (div, mod) = divmod(div-1, 26) # will return (x, 0 .. 25)
        excel_col = chr(mod + 65) + excel_col

    return excel_col

def quality_check_metadata(filled_composition_metadata, blank_composition_metadata, 
                           use_cols = [0, 1], nrows = 8):
    """
    the function verifies that the filled metadata does not vary from the metadata template

    Parameters
    ----------
    filled_composition_metadata : DATAFRAME
        Dataframe containing the metadata
    blank_composition_metadata : DATAFRAME
        Dataframe containing the template metadata
    use_cols: LIST, default = [0, 1]
        Defines which columns should be read for the metadata section (note column A is 0)
    nrows: INTEGER, default = 8
        Defines number of rows to be read for the metadata section
    
    Returns
    -------
    NONE
     
    Example
    -------
    cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
    path_filled = os.path.join(cwd, "darpa_template.xlsx")
    path_blank = os.path.join(cwd, "templates/darpa_template_blank.xlsx")
    filled_metadata = pd.read_excel (path_filled)
    blank_metadata = pd.read_excel (path_blank)
    quality_check_metadata(filled_metadata, blank_metadata, 
                           use_cols = [0, 1], nrows = 8)
    """
    comparison = np.where((filled_composition_metadata == blank_composition_metadata)|(blank_composition_metadata.isna()), True, False)
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
            if filled_composition_metadata.iloc[number, 0] != blank_composition_metadata.iloc[number, 0]:
                logging.warning(f"""The excel cell {excel_cell_names.loc[number, 0]} has been corrupted and 
                      should contain {blank_composition_metadata.iloc[number, 0]}""")
    return()

def load_libraries(table):
    """
    the function extracts the libraries from the filled template table

    Parameters
    ----------
    table : DATAFRAME
        Dataframe containing the filled template starting with the libraries
    
    Returns
    -------
    libraries : DICT
        Dictionary containing the libraries, the keys are the library abbreviations and the
        corresponding value is the url, if no abbreviation is used, the url is used for both key and value
     
    Example
    -------
    cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
    path_filled = os.path.join(cwd, "darpa_template.xlsx")
    table = pd.read_excel (path_filled)
    libraries = load_libraries(table)
    """
    libraries = dict()
    if table.iloc[0][0] == "Libraries" and table.iloc[0][1] == "Abbreviations":
        for index, row in table.iloc[1:len(table)].iterrows():
            if row[0] == "Composite DNA Parts" or row.dropna().empty: 
                break
            else:
                #if there is no abbreviation, use full name as key
                if not pd.isnull(table.iloc[index][1]):
                    libraries[table.iloc[index][1]] = table.iloc[index][0]
                else:
                    libraries[table.iloc[index][0]] = table.iloc[index][0]
    else:
        logging.error("""The template was altered by removing the library section. 
                      This means no parts can be loaded and no SBOL can be created.""")
    return(libraries)

def get_data(table, labels = np.array(["Collection Name:", "Name:", "Description:", "Strain (optional)",
              "Integration Locus (optional)", "Part Sequence:"])):
    """
    the function extracts the collection information contained in the filled template

    Parameters
    ----------
    table : DATAFRAME
        Dataframe containing the filled template starting with the libraries
    labels : ARRAY, default = np.array(["Collection Name:", "Name:", "Description:", "Strain (optional)",
              "Integration Locus (optional)", "Part Sequence:"])
        Array containing the headers used in each composition block in the template
    
    Returns
    -------
    compositions : DICT
        Nested dictionary containing the collection names and the corresponding values are the names of
        the composite design which are also dictionary containing the design descriptions and an as of yet
        empty parts dictionary
    list_of_rows : LIST
        list of the rows where each block starts and the number of columns that are filled in 
     
    Example
    -------
    cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
    path_filled = os.path.join(cwd, "darpa_template.xlsx")
    table = pd.read_excel (path_filled)
    compositions, list_of_rows = get_data(table)
    """
    compositions = dict()
    list_of_rows = []

    #loop over all rows in sheet
    for index, row in table.iterrows():
        
        #check if six rows starting from current row equal the preset labels
        labs = np.asarray(table.iloc[index : index+6][0])
        comparison = labs == labels 
        
        #if labels do match
        if row[0] == "Collection Name:" and comparison.all() :
            collect_name = table.iloc[index][1]
            
            #see if the collection name already exists in compositions dictionary
            try:
                #if it does use the existing dictionary
                collection_dict = compositions[collect_name]
            except:
                #if not create a new one
                collection_dict = {}
                
            columns = 0
            #for every 'name' row cycle through the columns
            for column in range(1,len(table.iloc[index+1])): 
                part_name = table.iloc[index+1][column]
                #if the column isn't empty
                if type(part_name) is str:
                    collection_dict[part_name] = {"Description" : table.iloc[index+2][column],
                                                      "Parts" : {}}
                    columns += 1
            #add the index of collection name row to the list of rows
            #and add number of columns used
            list_of_rows.append((index, columns))  
                                                      
            #add new items to compositions dictionary
            compositions[collect_name] = collection_dict
    return(compositions, list_of_rows)

def get_parts(list_of_rows, table, compositions):
    """
    the function extracts the parts contained in the filled template and adds them to the compositions dictionary

    Parameters
    ----------
    list_of_rows : LIST
        list of the rows where each block starts and the number of columns that are filled in
    table : DATAFRAME
        Dataframe containing the filled template starting with the libraries
    compositions : DICT
        Nested dictionary containing the collection names and the corresponding values are the names of
        the composite design which are also dictionary containing the design descriptions and an as of yet
        empty parts dictionary
    
    Returns
    -------
    compositions : DICT
        Nested dictionary containing the collection names and the corresponding values are the names of
        the composite design which are also dictionary containing the design descriptions and a newly filled
        dictionary of parts
    all_parts : SET
        A set containing all parts that are used in the filled template
     
    Example
    -------
    cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
    path_filled = os.path.join(cwd, "darpa_template.xlsx")
    table = pd.read_excel (path_filled)
    compositions, list_of_rows = get_data(table)
    compositions, all_parts = get_parts(list_of_rows, table, compositions)
    """
    
    all_parts = []
    len_list_of_rows = len(list_of_rows)
    for index, value in enumerate(list_of_rows):
        row_index = value[0]
        collect_name = table.iloc[row_index][1]
        #for column in the row with names in it
        for column in range(1,value[1]+1):
            part_name = table.iloc[row_index+1][column]
            
            #if it is the last block in the spreadsheet
            if index == len_list_of_rows-1:
                #read from the parts row to the end of the table
                parts = table.iloc[row_index+5: len(table)][column].dropna()
            else:
                #if not last block, read until next block
                parts = table.iloc[row_index+5: list_of_rows[index+1][0]][column].dropna()
    
            if len(parts) == 0:
                logging.warning(f"The design {part_name} in the collection {collect_name} was empty and thus removed")
                del compositions[collect_name][part_name]
                    
            else:
                compositions[collect_name][part_name]['Parts'] = parts.tolist()
                all_parts+=parts.tolist()
                
    all_parts = set(all_parts) #set eliminates duplicates

    #delete any collections with no composite parts
    empty_collect = []
    for key in compositions:
        if len(compositions[key]) == 0:
            empty_collect.append(key)
    for key in empty_collect:
        logging.warning(f"The collection {key} was empty and thus removed")
        del compositions[key]
        if len(compositions) == 0: #Throw an error if no collections remain
            logging.error("None of the collections contain any parts and no SBOL can be created")
    return(compositions, all_parts)

def check_name(compositions):
    """
    the function verifies that the collection names are alphanumeric and separated by underscores
    if that is not the case the special characters are replaced by their unicode decimal code number

    Parameters
    ----------
    compositions : DICT
        Nested dictionary containing the collection names and the corresponding values are the names of
        the composite design which are also dictionary containing the design descriptions and a
        dictionary of parts
    
    Returns
    -------
    compositions : DICT
        Nested dictionary containing the corrected collection names if that was necessary and the 
        corresponding values are the names of the composite design which are also dictionary containing 
        the design descriptions and a dictionary of parts
     
    Example
    -------
    cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
    path_filled = os.path.join(cwd, "darpa_template.xlsx")
    table = pd.read_excel (path_filled)
    compositions, list_of_rows = get_data(table)
    compositions, all_parts = get_parts(list_of_rows, table, compositions)
    compositions = check_name(compositions)
    """
    
    for key in compositions:
        old = key #for error warning
        title = key.replace('_', '') #remove underscore to use isalnum()
        if title.isalnum():
            print(f"Collection name {key} is valid")
        else: #replace special characters with numbers
            for letter in title:
                if ord(letter) > 122:
                    #122 is the highest decimal code number for common latin letters or arabic numbers
                    #this helps identify special characters like ä or ñ, which isalnum() returns as true
                    #the characters that don't meet this criterion are replaced by their decimal code number separated by an underscore
                    key = key.replace(letter, str( f"_{ord(letter)}"))
                else:
                    letter = re.sub('[\w, \s]', '', letter) #remove all letters, numbers and whitespaces
                    #this enables replacing all other special characters that are under 122
                    if len(letter) > 0:
                        key = key.replace(letter, str( f"_u{ord(letter)}"))
            temp_collect = compositions[old]
            del compositions[old]
            compositions[key] = temp_collect
            print(f"Collection name {old} was not valid and replaced by {key}")
    
    return(compositions)

def write_sbol_comp(libraries, compositions, all_parts):
    """
    the function pulls the parts from their SynBioHub libraries and compiles them into an SBOL document

    Parameters
    ----------
    libraries : DICT
        Dictionary containing the libraries, the keys are the library abbreviations and the
        corresponding value is the url, if no abbreviation is used, the url is used for both key and value
    compositions : DICT
        Nested dictionary containing the collection names and the corresponding values are the names of
        the composite design which are also dictionary containing the design descriptions and a
        dictionary of parts
    all_parts : SET
        A set containing all parts that are used in the filled template
        
    Returns
    -------
    doc: SBOL Document
        Document containing all components and sequences
     
    Example
    -------
    cwd = os.path.dirname(os.path.abspath("__file__")) #get current working directory
    path_filled = os.path.join(cwd, "darpa_template.xlsx")
    table = pd.read_excel (path_filled)
    compositions, list_of_rows = get_data(table)
    compositions, all_parts = get_parts(list_of_rows, table, compositions)
    compositions = check_name(compositions)
    doc = write_sbol_comp(libraries, compositions)
    """  
    
    doc = Document()
    sbol2.Config.setOption('sbol_typed_uris', False)
    
    for library in libraries:
        sbol_library = sbol2.PartShop(libraries[library])
        for part in all_parts:
            try:
                sbol_library.pull(part, doc)
            except:
                print(f"The part {part} was not in library {library}")
    
    
    for collection in compositions:
        coll = Collection(collection) #create collections
        doc.addCollection(coll)
        for design in compositions[collection]:
            composite_design = doc.componentDefinitions.create(design)
            composite_design.assemblePrimaryStructure(compositions[collection][design]["Parts"])
            composite_design.compile()
            composite_design.sequence
    
            if type(compositions[collection][design]["Description"]) is str:
                composite_design.description = compositions[collection][design]["Description"]
            
            coll.members += [composite_design.identity] #add designs to respective collections
    return(doc)

def fix_msec_sbol(file_path):
    #Edit igem2sbol activity to include milliseconds and avoid validation error
    #The underlying issue was already reported
    with open(file_path, "r") as file:
        data = file.read()
        
    with open(file_path, "w") as file:
        data = data.replace("<prov:endedAtTime>2017-03-06T15:00:00+00:00</prov:endedAtTime>", "<prov:endedAtTime>2017-03-06T15:00:00.000+00:00</prov:endedAtTime>")
        file.write(data)
        
    return ()

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
    
    return(doc)

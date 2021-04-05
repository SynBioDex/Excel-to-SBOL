import os
import pandas as pd
import sbol2
import string
import re
import logging
from sbol2 import Document, Collection, Component, ComponentDefinition
from sbol2 import BIOPAX_DNA, Sequence, SBOL_ENCODING_IUPAC, Config, SO_CIRCULAR

template_dict = {"darpa_template_blank_v005_20220222.xlsx":
                    {"library_start_row": 18,
                    "sheet_name": "Library",
                    "number_of_collection_rows": 8,
                    "collection_columns": [0,1],
                    "description_start_row": 10,
                    "description_columns": [0]
                    },

                "darpa_template_blank_v006_20210405.xlsx":
                    {"library_start_row": 18,
                    "sheet_name": "Library",
                    "number_of_collection_rows": 8,
                    "collection_columns": [0,1],
                    "description_start_row": 10,
                    "description_columns": [0]
                    }
                }

template_name = "darpa_template_blank_v005_20220222.xlsx"
name_of_file = "pichia_toolkit_KWK_v002"

cwd = os.getcwd()
path = os.path.join(cwd,"excel2sbol","tests","data",f"{name_of_file}.xlsx")
file_path_out = os.path.join(cwd,"excel2sbol","tests","data",f"{name_of_file}.xml")

#pull values from template dict
start_row = template_dict[template_name]["library_start_row"]
sheet_name = template_dict[template_name]["sheet_name"]
collection_rows = template_dict[template_name]["number_of_collection_rows"]
description_start_row = template_dict[template_name]["description_start_row"]
collection_cols = template_dict[template_name]["collection_columns"]
description_cols = template_dict[template_name]["description_columns"]

#pull in collection info
collection_info = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=collection_rows, usecols=collection_cols, index_col=0).to_dict('index')
description_info = pd.read_excel(path, sheet_name=sheet_name, header=None, skiprows=description_start_row, nrows=1, usecols=description_cols).iloc[0,0]


#read in the body of the sheet
sheet_read = pd.read_excel(path, sheet_name=sheet_name, header=0, skiprows=start_row).fillna("")
sheet_dict = sheet_read.to_dict('index')

#pull in the column definitions from the excel sheet
column_read_dict = pd.read_excel(path, sheet_name="column_definitions", header=0, index_col=0).to_dict('index')

#%%
def col_to_num(col_name):
    #takes an excel column name, e.g. AA and converts it to a zero indexed number
    num = 0
    for letter in col_name:
        if letter in string.ascii_letters:
            num = num * 26 + (ord(letter.upper()) - ord('A')) + 1
    num = num - 1
    return num

def check_name(name_to_check):
    """
    the function verifies that the names is alphanumeric and separated by underscores
    if that is not the case the special characters are replaced by their unicode decimal code number

    Parameters
    ----------
    name_to_check : string
    
    Returns
    -------
    compliant_name : string
        alphanumberic name with special characters replaced by _u###
    """
    
    
    if not bool(re.match('^[a-zA-Z0-9]+$', name_to_check)):
        #replace special characters with numbers
        for letter in name_to_check:
            if ord(letter) > 122 or ord(letter)<48:
                #122 is the highest decimal code number for common latin letters or arabic numbers
                #this helps identify special characters like ä or ñ, which isalnum() returns as true
                #the characters that don't meet this criterion are replaced by their decimal code number separated by an underscore
                name_to_check = name_to_check.replace(letter, str( f"_{ord(letter)}"))
            elif ord(letter) == 32:
                name_to_check = name_to_check.replace(letter, "_")
            else:
                letter = re.sub('[\w, \s]', '', letter) #remove all letters, numbers and whitespaces
                #this enables replacing all other special characters that are under 122
                if len(letter) > 0:
                    name_to_check = name_to_check.replace(letter, str( f"_u{ord(letter)}_"))
    
    if name_to_check[0].isnumeric():
        #ensures it doesn't start with a number
        name_to_check = f"_{name_to_check}"

    return(name_to_check)

class column:
    def __init__(self, path, column_dict_entry):
        self.sbol_term = column_dict_entry['SBOL Term']
        self.namespace_url = column_dict_entry['Namespace URL']
        self.lookup = column_dict_entry['Sheet Lookup']
        self.replacement_lookup = column_dict_entry['Replacement Lookup']

        if self.lookup:
            #create a lookup dictionary from human readable to actual values
            self.sheet_name = column_dict_entry['Sheet Name']
            self.col_from = col_to_num(column_dict_entry['From Col'])
            self.col_to = col_to_num(column_dict_entry['To Col'])
            self.lookup_dict = pd.read_excel(path, sheet_name=self.sheet_name, header=0, usecols=[self.col_from, self.col_to], index_col=0).to_dict('index')

class table:
    def __init__(self, table_doc_path, column_read_dict, sheet_dict):
        self.column_list = {}
        for col in column_read_dict.items():
            self.column_list[col[0]] = column(table_doc_path, col[1])

class sbol_methods:
    #create a method for each sbol term that can be called via the column class
    def switch(self, sbol_term, namespace_url, component, doc, cell_value):
        self.cell_value = cell_value
        self.sbol_term = sbol_term
        self.namespace_url = namespace_url
        self.doc = doc

        #Try redoing this with suggested form
        try: #try looking for a specified function
            return getattr(self, sbol_term)()
        except AttributeError: #use the default add function
            return getattr(self, 'add_new')()

    def Not_applicable(self):
        pass
    
    def add_new(self):
        logging.warning(f'This sbol term ({self.sbol_term}) has not yet been implemented so it has been added via the default method')
        self.sbol_term_prefix = self.sbol_term.split("_",1)[0]
        self.sbol_term_suffix = self.sbol_term.split("_",1)[1]
        if self.sbol_term_prefix not in {'rdf', 'rdfs', 'xsd', 'sbol'}:
            self.doc.addNamespace(self.namespace_url, self.sbol_term_prefix)
        setattr(component, self.sbol_term_suffix, sbol2.TextProperty(component, f'{self.namespace_url}{self.sbol_term_suffix}', 0, 1))
        setattr(component, self.sbol_term_suffix, str(cell_value))


    def sbh_alteredSequence(self):
        #currently uris don't go out to actuall activities. Fix uri to make this properly work
        component.wasGeneratedBy =  cell_value

    def sbh_dataSource(self):
        component.wasDerivedFrom = cell_value
        if "pubmed.ncbi.nlm.nih.gov/" in cell_value:
            self.doc.addNamespace('http://purl.obolibrary.org/obo/', 'obo')
            component.OBI_0001617 = sbol2.TextProperty(component, f'http://purl.obolibrary.org/obo/OBI_0001617', 0, 1,[])
            component.OBI_0001617 = cell_value.split(".gov/")[1].replace("/","")


    def sbh_sourceOrganism(self):
        #this together with target organism could be implemented in a better and more general way, possibly a general uri version
        self.doc.addNamespace('https://wiki.synbiohub.org/wiki/Terms/synbiohub#', 'sbh')
        component.sourceOrganism = sbol2.URIProperty(component, f'https://wiki.synbiohub.org/wiki/Terms/synbiohub#sourceOrganism', 0, 1,[])
        component.sourceOrganism = f'https://identifiers.org/taxonomy:{cell_value}'

    def sbh_targetOrganism(self):
        self.doc.addNamespace('https://wiki.synbiohub.org/wiki/Terms/synbiohub#', 'sbh')
        component.targetOrganism = sbol2.URIProperty(component, f'https://wiki.synbiohub.org/wiki/Terms/synbiohub#targetOrganism', 0, 1,[])
        component.targetOrganism = f'https://identifiers.org/taxonomy:{cell_value}'


    def sbol_role(self):
        if len(component.roles) == 0:
            component.roles = self.cell_value
        else:
            component.roles = component.roles + [self.cell_value]

    
    def sbol_roleCircular(self):
        if len(component.roles) == 0 and self.cell_value:
            component.roles = SO_CIRCULAR
        elif self.cell_value:
            component.roles = component.roles + [SO_CIRCULAR]


    def sbol_displayId(self):
        component.name= self.cell_value
        component.displayId = check_name(self.cell_value)

    
    def dcterms_description(self):
        component.description = str(self.cell_value)

    
    def sbol_sequence(self):
        self.cell_value = "".join(self.cell_value.split()).replace( u"\ufeff", "").lower() #removes spaces, enters, and makes all lower case
        sequence = Sequence(f"{component.displayId}_sequence", self.cell_value, SBOL_ENCODING_IUPAC)
        sequence.name = f"{component.name} Sequence"
        doc.addSequence(sequence)
        component.sequences = sequence


#%%
sheet_table = table(path, column_read_dict, sheet_dict)
doc = Document()
molecule_type = BIOPAX_DNA
Config.setOption('sbol_typed_uris', False)

#Metadata
if len(str(description_info))>0:
    doc.description = str(description_info)
doc.name = list(collection_info['Collection Name'].values())[0]


for row in sheet_dict.values():
    #set up component
    component = ComponentDefinition(check_name(row["Part Name"]), molecule_type)

    for col in row:
        if row[col] != '':
            cell_value = row[col]
            if sheet_table.column_list[col].lookup and not sheet_table.column_list[col].replacement_lookup:
                #pull converted cell value from lookup table created by table, column class
                cell_value = list(sheet_table.column_list[col].lookup_dict[cell_value].values())[0]
            elif sheet_table.column_list[col].lookup:
                #create a url based on the prefix
                cell_value_prefix = cell_value.split(":",1)[0]
                cell_value_suffix = cell_value.split(":",1)[1]
                cell_value = list(sheet_table.column_list[col].lookup_dict[cell_value_prefix].values())[0].replace("{REPLACE_HERE}", cell_value_suffix)
            
            #carry out method of column processing based on sbol_term of the column
            column_method = sbol_methods()
            column_result = column_method.switch(sheet_table.column_list[col].sbol_term, sheet_table.column_list[col].namespace_url, component, doc, cell_value)

    doc.addComponentDefinition(component)
# print(doc)
doc.write(file_path_out)
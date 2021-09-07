# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencie
import os
import json
import pandas as pd
import excel2sbol.column_functions as cf


class table:
    """Used to go from a regular dictionary to a dictionary of column objects
    """
    def __init__(self, table_doc_path, column_read_dict):
        """[summary]

        Args:
            table_doc_path (str): Full path to the input sheet
                E.g. 'C:/users/user/filled.xlsx'
            column_read_dict (dict): Dictionary of columns each with
                a dictionary. It takes the form:
                {column_name1:  {'SBOL Term': 'sbol_term',
                                'Namespace URL': 'nm_url',
                                'Sheet Lookup': 'TRUE',
                                'Replacement Lookup': 'TRUE',
                                'Sheet Name': 'Replacement',
                                'From Col': 'A', 'To Col': 'B'},
                column_name2:  {'SBOL Term': 'sbol_term',
                                'Namespace URL': 'nm_url',
                                'Sheet Lookup': 'TRUE',
                                'Replacement Lookup': 'TRUE',
                                'Sheet Name': 'Replacement',
                                'From Col': 'A', 'To Col': 'B'},
                }

        Raises:
            TypeError: If column_read_dict is not a dictionary a TypeError
                is raised.
        """

        if not isinstance(column_read_dict, dict):
            raise TypeError

        self.column_list = {}
        for key, value in column_read_dict.items():
            self.column_list[key] = cf.column(table_doc_path, value)


def read_in_sheet(templt_name, file_path_in):
    """This reads in an excel file and creates a series of dictionaries
    containing the relevant information based on the templt used.

    Args:
        templt_name (string): The name of the templt being used. It must be
        one of the names found in the file templt_constants.txt
        e.g. "darpa_templt_blank_v006_20210405.xlsx"
        file_path_in (string): The full filepath to the excel spreadsheet that
        needs to be read in.
        E.g. "C:\\Users\\Tester\\Downloads\\MyNiceLibrary.xlsx"

    Returns:
        column_read_dict (dictionary): The table of parts from
        excel in the format
                                    {
                                        part_name1: {col_nm1:col_val1,
                                                     col_nm2:col_val2},
                                        part_name2: {col_nm1:col_val1,
                                                     col_nm2:col_val2}
                                    }
        sheet_dict (dictionary): The column handelling sheet read in as a
                                dictionary of the format
                                    {
                                        col_nm1: {"SBOL Term":value1,
                                                  "Namespace URL":value2,
                                                  "Sheet Lookup":value3,
                                                  "Replacement Lookup":value4,
                                                  "Sheet Name":value5,
                                                  "From Col":value6,
                                                  "To Col":value7},
                                        col_nm2: {"SBOL Term":value1,
                                                  "Namespace URL":value2,
                                                  "Sheet Lookup":value3,
                                                  "Replacement Lookup":value4,
                                                  "Sheet Name":value5,
                                                  "From Col":value6,
                                                  "To Col":value7}
                                    }
        description_info (string): The library description from the
                                   'Design Description' box
        collection_info (dictionary): The collection information
                                      as a library of the format:
                                    {
                                        "Collection Name":value1,
                                        "Institution to Build":value2,
                                        "Date Created":value3,
                                        "Date Last Updated":value4,
                                        "Authors":value5,
                                        "Date Accepted":value6,
                                        "Person Accepting":value7,
                                        "SynBioHub Collection":value8
                                    }
    """

    file_dir = os.path.dirname(__file__)
    with open(os.path.join(file_dir,
                           'template_constants.txt')) as f:
        templt_dict = json.loads(f.read())

    # pull values from templt dict
    start_row = templt_dict[templt_name]["library_start_row"]
    sheet_name = templt_dict[templt_name]["sheet_name"]
    collection_rows = templt_dict[templt_name]["number_of_collection_rows"]
    description_start_row = templt_dict[templt_name]["description_start_row"]
    collection_cols = templt_dict[templt_name]["collection_columns"]
    description_cols = templt_dict[templt_name]["description_columns"]

    # pull in collection info
    collection_info = pd.read_excel(file_path_in, sheet_name=sheet_name,
                                    header=None, nrows=collection_rows,
                                    usecols=collection_cols,
                                    index_col=0, engine='openpyxl').to_dict('index')
    description_info = pd.read_excel(file_path_in, sheet_name=sheet_name,
                                     header=None,
                                     skiprows=description_start_row, nrows=1,
                                     usecols=description_cols, engine='openpyxl').iloc[0, 0]

    # read in the body of the sheet
    sheet_read = pd.read_excel(file_path_in, sheet_name=sheet_name, header=0,
                               skiprows=start_row, engine='openpyxl').fillna("")
    sheet_dict = sheet_read.to_dict('index')

    # pull in the column definitions from the excel sheet
    column_read_dict = pd.read_excel(file_path_in,
                                     sheet_name="column_definitions", header=0,
                                     index_col=0, engine='openpyxl')
    column_read_dict = column_read_dict.to_dict('index')

    return (column_read_dict, sheet_dict, description_info, collection_info)

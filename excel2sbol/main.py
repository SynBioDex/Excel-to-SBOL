import argparse
import excel2sbol.utils.converter_utils as converter_utils
import pandas as pd

def convert_part_library(template_file: str, input_excel: str):
    # Read in template and filled spreadsheet for the Parts library
    start_row = 13
    nrows = 8
    description_row = 9
    filled_library, filled_library_metadata, filled_description = converter_utils.read_library(input_excel,
                                                                               start_row=start_row, nrows=nrows,
                                                                               description_row=description_row)
    blank_library, blank_library_metadata, blank_description = converter_utils.read_library(template_file,
                                                                            start_row=start_row, nrows=nrows,
                                                                            description_row=description_row)

    ontology = pd.read_excel(input_excel, header=None, sheet_name="Ontology Terms", skiprows=3, index_col=0)
    ontology = ontology.to_dict("dict")[1]

    converter_utils.quality_check(filled_library,
                                  blank_library,
                                  filled_library_metadata,
                                  blank_library_metadata,
                                  filled_description,
                                  blank_description, nrows, description_row)

    # Create SBOL document
    doc = converter_utils.write_sbol(filled_library, filled_library_metadata, filled_description, ontology)
    return doc

def convert_composition_reading(template_file: str, input_excel: str):
    # Load Data
    startrow_composition = 9
    sheet_name = "Composite Parts"
    nrows = 8
    use_cols = [0, 1]
    # read in whole composite sheet below metadata
    table = pd.read_excel(input_excel, sheet_name=sheet_name,
                          header=None, skiprows=startrow_composition)

    # Load Metadata
    filled_composition_metadata = pd.read_excel(input_excel, sheet_name=sheet_name,
                                                header=None, nrows=nrows, usecols=use_cols)
    blank_composition_metadata = pd.read_excel(template_file, sheet_name=sheet_name,
                                               header=None, nrows=nrows, usecols=use_cols)

    # Compare the metadata to the template
    converter_utils.quality_check_metadata(filled_composition_metadata, blank_composition_metadata)

    # Load Libraries required for Parts
    libraries = converter_utils.load_libraries(table)

    # Loop over all rows and find those where each block begins
    compositions, list_of_rows = converter_utils.get_data(table)

    # Extract parts from table
    compositions, all_parts = converter_utils.get_parts(list_of_rows, table, compositions)

    # Check if Collection names are alphanumeric and separated by underscore
    compositions = converter_utils.check_name(compositions)

    # Create sbol
    doc = converter_utils.write_sbol_comp(libraries, compositions, all_parts)
    return doc

def main():
    parser = argparse.ArgumentParser(description='Creates libraries of basic parts by converting a spreadsheet to SBOL.')
    parser.add_argument('-if', '--input_file', nargs='?',
                        required=True, help='Path to excel file.')
    parser.add_argument('-of', '--output_file', nargs='?',
                        required=False, help='Name of output file.')

    input_args = parser.parse_args()
    input_excel_file = input_args.input_file
    output_file_path = input_args.output_file

if __name__ == '__main__':
    main()

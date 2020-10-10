import argparse
import excel2sbol.utils.converter_utils as converter_utils
import pandas as pd

def convert_part_library(input_excel: str, output_file: str):
    # Read in template and filled spreadsheet for the Parts library
    start_row = 13
    nrows = 8
    description_row = 9
    path_blank = None # TODO: os.path.join(cwd, "templates/darpa_template_blank.xlsx")
    filled_library, filled_library_metadata, filled_description = converter_utils.read_library(input_excel,
                                                                               start_row=start_row, nrows=nrows,
                                                                               description_row=description_row)
    blank_library, blank_library_metadata, blank_description = converter_utils.read_library(path_blank,
                                                                            start_row=start_row, nrows=nrows,
                                                                            description_row=description_row)

    ontology = pd.read_excel(input_excel, header=None, sheet_name="Ontology Terms", skiprows=3, index_col=0)
    ontology = ontology.to_dict("dict")[1]

    converter_utils.quality_check(filled_library, blank_library, filled_library_metadata, blank_library_metadata, filled_description, blank_description)

    # Create SBOL document
    doc = converter_utils.write_sbol(filled_library, filled_library_metadata, filled_description, ontology)
    doc.write(output_file)

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

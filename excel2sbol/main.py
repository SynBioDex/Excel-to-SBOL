import argparse

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

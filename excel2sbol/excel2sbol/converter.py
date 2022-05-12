from ensurepip import version
import excel2sbol.compiler_test as e2s


def converter(file_path_in, file_path_out, sbol_version=3):
    """Convert a given excel file to SBOL

    Args:
        file_path_in (string): path to excel file
        file_path_out (string): desired path to sbol file
        sbol_version (int): sbol version number, defaults to 3
    """
    col_read_df, to_convert, compiled_sheets, version_info = e2s.initialise(file_path_in)

    sbol_version = version_info
    print(f'Conversion will happen with sbol version {sbol_version} as specified in the excel sheet')

    if sbol_version == 2:
        doc, dict_of_objs, sht_convert_dict = e2s.parse_objects(col_read_df,
                                                                to_convert,
                                                                compiled_sheets)
    elif sbol_version == 3:
        doc, dict_of_objs, sht_convert_dict = e2s.parse_objects3(col_read_df,
                                                                 to_convert,
                                                                 compiled_sheets)

    e2s.column_parse(to_convert, compiled_sheets, sht_convert_dict,
                     dict_of_objs, col_read_df, doc, file_path_out,
                     sbol_version=sbol_version)

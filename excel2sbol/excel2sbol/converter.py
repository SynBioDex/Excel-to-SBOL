import os
import excel2sbol.compiler_test as e2s


# the homespace only works if the change is made to pysbol2 shown
# in https://github.com/SynBioDex/pySBOL2/pull/411/files
cwd = os.getcwd()
file_path_in = os.path.join(cwd, 'excel2sbol', 'tests', 'test_files',
                            'pichia_comb_dev_compiler_sbol3.xlsx')
file_path_out = os.path.join(cwd, 'out.xml')
sbol_version = 3

col_read_df, to_convert, compiled_sheets = e2s.initialise(file_path_in)

if sbol_version == 2:
    doc, dict_of_objs, sht_convert_dict = e2s.parse_objects(col_read_df,
                                                            to_convert,
                                                            compiled_sheets)
elif sbol_version == 3:
    doc, dict_of_objs, sht_convert_dict = e2s.parse_objects3(col_read_df,
                                                            to_convert,
                                                            compiled_sheets)

e2s.column_parse(to_convert, compiled_sheets, sht_convert_dict, dict_of_objs,
                 col_read_df, doc, file_path_out, sbol_version=sbol_version)

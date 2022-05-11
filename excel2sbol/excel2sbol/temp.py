import excel2sbol.converter as conv
import os

cwd = os.getcwd()
print(cwd)
file_path_in = os.path.join(cwd, "excel2sbol", 'tests', 'test_files', 'pichia_comb_dev_compiler_sbol3_v006.xlsx')
file_path_out = os.path.join(cwd, "excel2sbol", 'tests', 'test_files', 'sbol_utilities.xml')


conv.converter(file_path_in, file_path_out, sbol_version=2)

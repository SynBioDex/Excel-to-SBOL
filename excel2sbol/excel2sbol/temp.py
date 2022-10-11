import excel2sbol.converter as conv
import os

cwd = os.getcwd()
print(cwd)

file_path_in = os.path.join(cwd, "excel2sbol", 'tests', 'test_files',
                            'SBOL3_simple_library4.xlsx')
file_path_out = os.path.join(cwd, "excel2sbol", 'tests', 'test_files',
                             'SBOL3_simple_library4.nt')

conv.converter(file_path_in, file_path_out)
# conv.converter(file_path_in, file_path_out, sbol_version=2,
#                homespace="http://examples.org/")

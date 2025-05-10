# import excel2sbol.converter as conv
import sys
import os

sys.path.insert(0, '/Users/william/Desktop/Code/GLL/Excel-to-SBOL/excel2sbol/excel2sbol')
import converter as conv


cwd = os.chdir('/Users/william/Desktop/Code/GLL/Excel-utilities')
cwd = os.getcwd()
print(cwd)

file_path_in = os.path.join(cwd, 'two_backbones.xlsx')
file_path_out = os.path.join(cwd, 'two_backbones.nt')

conv.converter(file_path_in, file_path_out, file_format='sorted nt')
# conv.converter(file_path_in, file_path_out, sbol_version=2,
#                homespace="http://examples.org/")

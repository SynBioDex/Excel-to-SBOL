import os
from excel2sbol.converter import converter as e2s

file_path_in = "C:\\Users\\saisa\\Excel-to-SBOL\\excel2sbol\\tests\\test_files\\test_version5_flapjack_compiler_sbol3_v0014.xlsx"
file_path_out = "C:\\Users\\saisa\\Excel-to-SBOL\\excel2sbol\\tests\\test_files\\output.xml"

e2s(file_path_in, file_path_out, sbol_version=2)


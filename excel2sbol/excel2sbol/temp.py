# This file contains the code you need to run the converter.
import excel2sbol.converter_function as conv
import os
cwd = os.getcwd()
file_path_out = os.path.join(cwd, "output.xml")
file_url = os.path.join(cwd, "pichia_toolkit_KWK_v002 copy_Prubhtej.xlsx")
conv.converter("excel2bol_darpa_template_blank_v006_20210405.xlsx", file_url, file_path_out)
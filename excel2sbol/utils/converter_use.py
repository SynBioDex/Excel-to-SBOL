import os
import utils.converter_function as conf

cwd = os.getcwd()

template_name = "darpa_template_blank_v005_20220222.xlsx"
name_of_file = "pichia_toolkit_KWK_v002"

file_path_in = os.path.join(cwd, "excel2sbol", "tests",
                            "data", f"{name_of_file}.xlsx")
file_path_out = os.path.join(cwd, "excel2sbol", "tests", "data",
                             f"{name_of_file}.xml")


conf.converter(template_name, file_path_in, file_path_out)

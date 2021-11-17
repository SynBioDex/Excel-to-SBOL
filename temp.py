import excel2sbol.converter_function as e2s
import os
import tyto

print(tyto.endpoint.Ontobee.get_uri_by_term(getattr(tyto, "NCBITaxon"), 'Saccharomyces cerevisiae'))

cwd = os.getcwd()
template_name = "excel2bol_darpa_template_blank_v008_20211110.xlsx"
file_path_in = os.path.join(cwd, 'excel2sbol', 'tests', 'test_files', 'pichia_comb_dev.xlsx')
file_path_out = os.path.join(cwd, 'out.html')
e2s.converter(template_name, file_path_in, file_path_out)

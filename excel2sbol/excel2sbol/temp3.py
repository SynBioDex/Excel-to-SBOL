# # import sbol3
import sbol2
import excel2sbol.helper_functions as hf
import os
import re


name = "hello world!1a"
print(hf.check_name(name))

# cwd = os.getcwd()
# file_path_out = os.path.join(cwd, "excel2sbol", 'tests', 'test_files', 'ACS_sbol_parts.xml')

# comps = ["A, B, C", "D", "E"]

# doc = sbol2.Document()

# obja = sbol2.ComponentDefinition("A")
# objb = sbol2.ComponentDefinition("B")
# objc = sbol2.ComponentDefinition("C")
# objd = sbol2.ComponentDefinition("D")
# obje = sbol2.ComponentDefinition("E")

# doc.add(obja)
# doc.add(objb)
# doc.add(objc)
# doc.add(objd)
# doc.add(obje)

# comdev = sbol2.CombinatorialDerivation("comdev")
# doc.add(comdev)

# comp_ind = 0
# variant_comps = {}
# for ind, comp in enumerate(comps):
#     if "," in comp or type(comdev) == sbol2.combinatorialderivation.CombinatorialDerivation:
#         comps[ind] = f'{comdev.displayId}_subcomponent_{comp_ind}'
#         uri = f'{comdev.displayId}_subcomponent_{comp_ind}'
#         sub_comp = sbol2.ComponentDefinition(uri)
#         sub_comp.displayId = f'{comdev.displayId}_subcomponent_{comp_ind}'
#         doc.add(sub_comp)
#         variant_comps[f'subcomponent_{comp_ind}'] = {'object': sub_comp, 'variant_list': comp}
#         comp_ind += 1
#     else:
#         comps[ind] = hf.check_name(comps[ind])

# temp = sbol2.ComponentDefinition("comdev_template")
# temp.displayId = f'{comdev.displayId}_template'
# doc.add(temp)

# temp.assemblePrimaryStructure(comps)
# # temp.compile(assembly_method=None)

# comdev.masterTemplate = temp
# for var in variant_comps:
#     #var = hf.check_name(var)
#     var_comp = sbol2.VariableComponent(f'var_{var}')
#     var_comp.displayId = f'var_{var}'
#     var_comp.variable = variant_comps[var]['object']

#     var_list = re.split(",", variant_comps[var]['variant_list'])
#     var_list = [f'{sbol2.getHomespace()}/{hf.check_name(x.strip())}' for x in var_list]
#     var_comp.variants = var_list
#     comdev.variableComponents.add(var_comp)


# doc.write(file_path_out)





# # doc = sbol3.Document()

# # colec = sbol3.Collection('FinalProducts', name='FinalProducts')
# # doc.add(colec)

# # # print(sbol3.get_namespace())

# # sbol_objs = doc.objects
# # sbol_objs_names = [x.name for x in sbol_objs]
# # if 'FinalProducts' not in sbol_objs_names:
# #     colec = sbol3.Collection('FinalProducts', name='FinalProducts')
# #     # colec.members.append('test')
# #     doc.add(colec)
# # else:
# #     colec = sbol_objs[sbol_objs_names.index('FinalProducts')]

# # colec.members.append('this')

# sbol2.CombinatorialDerivation()
# sbol2.ComponentDefinition()
# sbol2.getHomespace()
# sbol2.URIRef


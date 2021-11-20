import excel2sbol.converter_function as e2s
import os
import tyto
import sbol2

# print(tyto.endpoint.Ontobee.get_uri_by_term(getattr(tyto, "NCBITaxon"), 'Saccharomyces cerevisiae'))

cwd = os.getcwd()
template_name = "excel2bol_darpa_template_blank_v008_20211110.xlsx"
file_path_in = os.path.join(cwd, 'excel2sbol', 'tests', 'test_files', 'pichia_comb_dev.xlsx')
file_path_out = os.path.join(cwd, 'out.html')
e2s.converter(template_name, file_path_in, file_path_out)


######################################################################################
# doc = sbol2.Document()


# # add a component with annotation and start and end
# obj = sbol2.ComponentDefinition("hello")
# comp = sbol2.Component('hi')
# seqAn = sbol2.SequenceAnnotation('hi_ann')
# seqAn.component = comp
# r = seqAn.locations.createRange('hi_ann_range')
# r.start = 1
# r.end = 7
# obj.components.add(comp)
# obj.sequenceAnnotations.add(seqAn)
# doc.addComponentDefinition(obj)

# # add component made from sub components
# obj1 = doc.componentDefinitions.create("Bye")

# cd1 = sbol2.ComponentDefinition("hello1")
# hel1_seq = sbol2.Sequence("hel1_seq")
# hel1_seq.elements = "aaaaaaaaaaaaaaaaaaaaaaaaaaat"
# cd1.sequence = hel1_seq
# doc.add(cd1)

# cd2 = sbol2.ComponentDefinition("hello2")
# hel2_seq = sbol2.Sequence("hel2_seq")
# hel2_seq.elements = "aaaaaaaaaaaaaaaaaaaaaaaaaaat"
# cd2.sequence = hel2_seq
# doc.add(cd2)

# cd3 = sbol2.ComponentDefinition("hello3")
# hel3_seq = sbol2.Sequence("hel3_seq")
# hel3_seq.elements = "aaaaaaaaaaaaaaaaaaaaaaaaaaat"
# cd3.sequence = hel3_seq
# doc.add(cd3)

# obj1.assemblePrimaryStructure(['hello1', 'hello2', 'hello3'])
# obj1.compile(assembly_method=None)

# # sbol2.ComponentDefinition.compi
# # obj.sequence


# # composite_design = doc.componentDefinitions.create(design)
# # composite_design.assemblePrimaryStructure(compositions[collection][design]["Parts"])
# # composite_design.compile()
# # composite_design.sequence


# doc.write(file_path_out)

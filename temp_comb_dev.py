# https://sbolstandard.org/docs/SBOL2.3.0.pdf
import sbol2
import os

# print(sbol2.SBOL_COMBINATORIAL_DERIVATION)

cwd = os.getcwd()
file_path_out = os.path.join(cwd, 'out.html')

doc = sbol2.Document()

# rbs:cds1,cds2,cds3:term IMPLEMENT THIS AS A COMBINATORIAL DERIVATION

# might need to add code to add generic locations and sequence annotations for each component
# additionally might need to allow constraints to be added and orientation of parts to be set
obj = doc.componentDefinitions.create("temp")

comp = sbol2.ComponentDefinition('prom')
# seqAn = sbol2.SequenceAnnotation('prom_ann')
# seqAn.component = comp
doc.add(comp)
# obj.components.add(comp)
# obj.sequenceAnnotations.add(seqAn)

comp = sbol2.ComponentDefinition('cds')
save_this = comp
# seqAn = sbol2.SequenceAnnotation('cds_ann')
# seqAn.component = comp
doc.add(comp)
# obj.components.add(comp)
# obj.sequenceAnnotations.add(seqAn)

comp = sbol2.ComponentDefinition('term')
# seqAn = sbol2.SequenceAnnotation('term_ann')
# seqAn.component = comp
doc.add(comp)
# obj.components.add(comp)
# obj.sequenceAnnotations.add(seqAn)


obj.assemblePrimaryStructure(['prom', 'cds', 'term'])
# obj.compile(assembly_method=None)


comb_dev = sbol2.CombinatorialDerivation('comb')
comb_dev.masterTemplate = obj
var = sbol2.VariableComponent('cds_variable')
var.variable = save_this
var1 = sbol2.ComponentDefinition('var_1')
var2 = sbol2.ComponentDefinition('var_2')
var.variants = [var1, var2]
comb_dev.variableComponents.add(var)

doc.add(comb_dev)


# doc.addComponentDefinition(obj)
doc.write(file_path_out)

#############################################################################################################################################
# # add component made from sub components
# comb_dev = sbol2.CombinatorialDerivation('bye')
# # obj1 = doc.componentDefinitions.create("Bye")

# cd1 = sbol2.ComponentDefinition("hello1")
# hel1_seq = sbol2.Sequence("hel1_seq")
# hel1_seq.elements = "aaaaaaaaaaaaaaaaaaaaaaaaaaa"
# cd1.sequence = hel1_seq
# doc.add(cd1)

# cd2 = sbol2.ComponentDefinition("hello2")
# hel2_seq = sbol2.Sequence("hel2_seq")
# hel2_seq.elements = "gggggggggggggggggggggggggg"
# cd2.sequence = hel2_seq
# doc.add(cd2)

# cd3 = sbol2.ComponentDefinition("hello3")
# hel3_seq = sbol2.Sequence("hel3_seq")
# hel3_seq.elements = "ccccccccccccccccccccccccccccccccccccccc"
# cd3.sequence = hel3_seq
# doc.add(cd3)

# obj1.assemblePrimaryStructure(['hello1', 'hello2', 'hello3'])
# obj1.compile(assembly_method=None)

#############################################################################################################################################


# composite_design = doc.componentDefinitions.create(design)
# composite_design.assemblePrimaryStructure(compositions[collection][design]["Parts"])
# composite_design.compile()
# composite_design.sequence




# class CombinatorialDerivation(TopLevel):

#     def __init__(self, type_uri=SBOL_COMBINATORIAL_DERIVATION,
#                  uri=URIRef("example"),
#                  strategy='http://sbols.org/v2#enumerate',
#                  version=VERSION_STRING):
#         super().__init__(type_uri, uri, version)
#         # Todo in original source, it doesn't look like strategy is used
#         self.strategy = URIProperty(self, SBOL_STRATEGY, '1', '1', [])
#         self.masterTemplate = ReferencedObject(self, SBOL_TEMPLATE,
#                                                SBOL_COMBINATORIAL_DERIVATION,
#                                                '0', '1', [])
#         self.variableComponents = OwnedObject(self, SBOL_VARIABLE_COMPONENTS,
#                                               VariableComponent,
#                                               '0', '*', [])
#####################################################################################
# def make_combinatorial_derivation(document, display_id,part_lists,reverse_complements,constraints):
#     # Make the combinatorial derivation and its template
#     template = sbol3.Component(display_id + "_template", sbol3.SBO_DNA)
#     document.add(template)
#     cd = sbol3.CombinatorialDerivation(display_id, template)
#     cd.strategy = sbol3.SBOL_ENUMERATE
#     # for each part, make a SubComponent or LocalSubComponent in the template and link them together in sequence
#     template_part_list = []
#     for part_list,rc in zip(part_lists,reverse_complements):
#         # it's a variable if there are multiple values or if there's a single value that's a combinatorial derivation
#         if len(part_list)>1 or not isinstance(part_list[0],sbol3.Component):
#             sub = sbol3.LocalSubComponent({sbol3.SBO_DNA}) # make a template variable
#             sub.name = "Part "+str(len(template_part_list)+1)
#             template.features.append(sub)
#             var = sbol3.VariableFeature(cardinality=sbol3.SBOL_ONE, variable=sub)
#             cd.variable_features.append(var)
#             # add all of the parts as variables
#             for part in part_list:
#                 if isinstance(part,sbol3.Component): var.variants.append(part)
#                 elif isinstance(part,sbol3.CombinatorialDerivation): var.variant_derivations.append(part)
#                 else: raise ValueError("Don't know how to make library element for "+part.name+", a "+str(part))
#         else: # otherwise it's a fixed element of the template
#             sub = sbol3.SubComponent(part_list[0])
#             template.features.append(sub)
#         # in either case, orient and order the template elements
#         sub.orientation = (sbol3.SBOL_REVERSE_COMPLEMENT if rc else sbol3.SBOL_INLINE)
#         if template_part_list: template.constraints.append(sbol3.Constraint(sbol3.SBOL_MEETS,template_part_list[-1],sub))
#         template_part_list.append(sub)
#     # next, add all of the constraints to the template
#     #template.constraints = (make_constraint(c.strip(),template_part_list) for c in (constraints.split(',') if constraints else [])) # impacted by pySBOL3 appending
#     c_list = (make_constraint(c.strip(),template_part_list) for c in (constraints.split(',') if constraints else []))
#     for c in c_list: template.constraints.append(c)
#     # return the completed part
#     return cd

# print(obj)
# doc.add(obj)
# file_path_out = os.path.join(cwd, 'outing.html')
# doc.write(file_path_out)

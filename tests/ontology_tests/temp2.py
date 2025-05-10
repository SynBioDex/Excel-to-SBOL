import sbol3
import os

direct = os.path.split(__file__)[0]
file_path_out = os.path.join(direct, 'out.nt')

doc = sbol3.Document()
comp = sbol3.Component('http://sbolstandard.org/testfiles/hello', sbol3.SBO_DNA)
comp.derived_from = (['www.example.com'])
seq = sbol3.Sequence('http://sbolstandard.org/testfiles/hello_sequence', elements='ATGC')
doc.add(comp)
doc.add(seq)

comp.sequences = [seq]

doc.change_object_namespace([seq], 'http://parts.igem.org', doc)

doc.write(file_path_out)
# https://sbolstandard.org/docs/SBOL2.3.0.pdf
import sbol3
import os
import rdflib

# print(sbol2.SBOL_COMBINATORIAL_DERIVATION)

cwd = os.getcwd()
file_path_out = os.path.join(cwd, 'out.nt')

doc = sbol3.Document()


obj = sbol3.Component('hello', [sbol3.SBO_DNA])

ns = 'http://parts.igem.org'
doc.bind('igem', ns)
doc.add(obj)

doc.change_object_namespace([obj], ns)
obj.display_id

obj.name = 'hello'


# obj2 = sbol3.Component(f'{ns}/{obj.display_id}', obj.types, namespace=ns)
# obj2._properties = obj._properties
# obj2.namespace = ns

# need to do this and then replace the object in the object dictionary
# also create a hash map of new to old
# at the end replace any old with new (to account for e.g. sequence references etc) # might need to implicitly update sequences
# and for genbank update display id
# only do it for literal part = true
# might need to move where in the document the obj add happens?

doc.write(file_path_out)

import tyto
import sbol3

print(tyto.endpoint.Ontobee.get_uri_by_term(tyto.SBO, 'DNA'))

print(sbol3.SBO_PROTEIN)
# import sbol3

# doc = sbol3.Document()

# colec = sbol3.Collection('FinalProducts', name='FinalProducts')
# doc.add(colec)

# # print(sbol3.get_namespace())

# sbol_objs = doc.objects
# sbol_objs_names = [x.name for x in sbol_objs]
# if 'FinalProducts' not in sbol_objs_names:
#     colec = sbol3.Collection('FinalProducts', name='FinalProducts')
#     # colec.members.append('test')
#     doc.add(colec)
# else:
#     colec = sbol_objs[sbol_objs_names.index('FinalProducts')]

# colec.members.append('this')
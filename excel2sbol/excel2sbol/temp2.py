import sbol2
import os
import sbol_utilities.conversion as conv


doc = sbol2.Document()
comp = sbol2.Component("hello")
doc.add(comp)
cwd = os.getcwd()
print(doc)
file_path_out = os.path.join(cwd, "excel2sbol", 'tests', 'test_files', 'out_test.xml')
doc.write(file_path_out)

doc3 = conv.convert2to3(file_path_out)
print(doc3)
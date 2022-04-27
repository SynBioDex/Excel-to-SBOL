import sbol2
import os

cwd = os.getcwd()
print(cwd)
file_path_out = os.path.join(cwd, "excel2sbol", 'tests', 'test_files', 'out2.xml')

doc = sbol2.Document()

fc1 = sbol2.FunctionalComponent("fc1")
fc2 = sbol2.FunctionalComponent("fc2")
cp1 = sbol2.ComponentDefinition("cp1")

doc.add(cp1)

fc2.definition = cp1

mod1 = sbol2.ModuleDefinition("mod1")
mod2 = sbol2.ModuleDefinition("mod2")

doc.add(mod1)
doc.add(mod2)

mod1.functionalComponents.add(fc1)
mod2.functionalComponents.add(fc1)



doc.write(file_path_out)
from hashlib import new
import re
import logging
import sbol3
import warnings
import excel2sbol.helpers as helpers


def objectType(rowobj):
	# used to decide the object type in the converter function
	pass

def types(rowobj):
	pass

def displayId(rowobj):
	# used to set the object display id in converter function
	pass

def addToDescription(rowobj):
	current = getattr(rowobj.obj, 'description')
	if isinstance(current, type(None)):
		current = ""
	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]
		if isinstance(val, str): 
			current = current + "\n" + col + ": " + val
		else:
			raise TypeError(f"A multicolumn value was unexpectedly given in addToDescription, {rowobj.col_cell_dict}")
	setattr(rowobj.obj, 'description', current)

constraint_pattern = re.compile(r'Part\s+(\d+)\s+(.+?)\s+Part\s+(\d+)')
constraint_dict = {'same as': sbol3.SBOL_VERIFY_IDENTICAL,
                   'different from': sbol3.SBOL_DIFFERENT_FROM,
                   'same orientation as': sbol3.SBOL_SAME_ORIENTATION_AS,
                   'different orientation from': sbol3.SBOL_SAME_ORIENTATION_AS}

def make_constraint(constraint, part_list, template):
    m = constraint_pattern.match(constraint)
    if not m:
        raise ValueError(f'Constraint "{constraint}" does not match pattern "Part X relation Part Y"')
    try:
        restriction = constraint_dict[m.group(2)]
    except KeyError:
        raise ValueError(f'Do not recognize constraint relation in "{constraint}"')
    x = int(m.group(1)) # Part numbers 
    y = int(m.group(3))
    if x is y:
        raise ValueError(f'A part cannot constrain itself: {constraint}')
    for n in [x,y]:
       if not (0 < n <= len(part_list)):
           raise ValueError(f'Part number "{str(n)}" is not between 1 and {len(part_list)}')
    return sbol3.Constraint(restriction, template.features[x-1].identity, template.features[y-1].identity)

def subcomponents(rowobj, template): #UPDATE TO WORK WITH CELL DICT, ALLOW CONSTRAINTS
	if 'subcomp' in rowobj.col_cell_dict:
		subcomps = list(rowobj.col_cell_dict['subcomp'].values())
	if 'constraint' in rowobj.col_cell_dict:
		constraints = list(rowobj.col_cell_dict['constraint'].values())
		c_split = constraints[0].split(',')
		c_list = (make_constraint(c.strip(), subcomps, template) for c in c_split)
	else:
		constraints = []


	if 'backbone' in rowobj.col_cell_dict:
		# If this row has a backbone, create a new combinatorial derivation

		# Determine if there are multiple comps per part
		multiple = False

		for sub in rowobj.col_cell_dict['subcomp']:
			if "," in rowobj.col_cell_dict['subcomp'][sub]:
				multiple = True
				break
			else:
				multiple = False

		# 1. If there are multiple comps per part, create ins_templat

		if multiple:
			temp = sbol3.Component(identity=f'{rowobj.obj.displayId}_ins_template', types=sbol3.SBO_DNA)

			newobj = sbol3.CombinatorialDerivation(identity=f'{rowobj.obj.displayId}_ins', template=temp, name=f'{rowobj.obj.name} insert', \
				strategy=sbol3.SBOL_ENUMERATE, description=rowobj.obj.description)

			rowobj.obj.description = None

			rowobj.doc.add(temp) # Add the template
			rowobj.doc.add(newobj) # Add the combdev _ins to the document connected to the template

			rowobj.obj_dict[temp.display_id] = {'uri': temp.type_uri, 'object': temp,
									'displayId': temp.display_id}
			backbones = list(rowobj.col_cell_dict['backbone'].values())
			backbones = backbones[0].split(", ")

			back = True
			oldobj = rowobj.obj
			rowobj.obj = newobj
		else:
			# 2. Otherwise, create _ins without the template 

			# Create new component _ins without the template
			newobj = sbol3.Component(identity=f'{rowobj.obj.displayId}_ins', name=f'{rowobj.obj.name} insert', \
				 description=rowobj.obj.description, types=sbol3.SBO_DNA, roles=sbol3.SO_ENGINEERED_REGION)

			# Set description to None
			rowobj.obj.description = None

			rowobj.doc.add(newobj)

			backbones = list(rowobj.col_cell_dict['backbone'].values())
			backbones = backbones[0].split(", ")


			back = True
			oldobj = rowobj.obj
			rowobj.obj = newobj
	else:
		back = False


	# if type is compdef do one thing, if combdev do another, else error
	if isinstance(rowobj.obj, sbol3.component.Component):
		for sub in subcomps:
			sub_part = sbol3.SubComponent(f'{sbol3.get_namespace()}/{sub}')
			rowobj.obj.features.append(sub_part)
		# self.obj.assemblePrimaryStructure(self.cell_val)
		# self.obj.compile(assembly_method=None)

	elif isinstance(rowobj.obj, sbol3.combderiv.CombinatorialDerivation):
		variant_comps = []
		comp_ind = 0
		
		# Need to update for multiple backbones, as well as remove hardcoding
		# Check SBOL Utilities for reasoning for multiple backbones

		if back:
			# Currently this code creates a template for the insertion of the backbone into the main combinatorialderivation
			tempObj = rowobj.obj_dict[f'{oldobj.display_id}_template']['object']

			sub = sbol3.LocalSubComponent(types=sbol3.SBO_DNA, name="Inserted Construct")
			tempObj.features.append(sub)
			backbone_sub = sbol3.VariableFeature(cardinality=sbol3.SBOL_ONE, variable=sub, variant_derivations=rowobj.obj)
			oldobj.variable_features.append(backbone_sub)

			if len(backbones) == 1:

				subComp = sbol3.SubComponent(instance_of=rowobj.obj_dict[backbones[0]]['object'])
				rowobj.obj_dict[f'{oldobj.display_id}_template']['object'].features.append(subComp)
				constr1 = sbol3.Constraint(restriction=sbol3.SBOL_MEETS, object=subComp, subject=sub)
				constr2 = sbol3.Constraint(restriction=sbol3.SBOL_MEETS, object=sub, subject=subComp)
				rowobj.obj_dict[f'{oldobj.display_id}_template']['object'].constraints.append(constr1)
				rowobj.obj_dict[f'{oldobj.display_id}_template']['object'].constraints.append(constr2)
			else:

				newLocalSub = sbol3.LocalSubComponent(name="Vector", types=sbol3.SBO_DNA)
				tempObj.features.append(newLocalSub)

				newVarFeature = sbol3.VariableFeature(variable=newLocalSub, variants=(rowobj.obj_dict[i]['object'] for i in backbones), cardinality=sbol3.SBOL_ONE)
				oldobj.variable_features.append(newVarFeature)

				constr1 = sbol3.Constraint(restriction=sbol3.SBOL_MEETS, object=newLocalSub, subject=sub)
				constr2 = sbol3.Constraint(restriction=sbol3.SBOL_MEETS, object=sub, subject=newLocalSub)

				rowobj.obj_dict[f'{oldobj.display_id}_template']['object'].constraints.append(constr1)
				rowobj.obj_dict[f'{oldobj.display_id}_template']['object'].constraints.append(constr2)

		
		else:
			temp = rowobj.obj_dict[f'{rowobj.obj.display_id}_template']['object']

		comp_list = subcomps
		
		for ind, comp in enumerate(comp_list):
			if "," in comp or type(rowobj.obj_dict[comp]['object']) == \
									sbol3.combderiv.CombinatorialDerivation:
				tempLocalSub = sbol3.LocalSubComponent(name=f"Part {comp_ind + 1}", orientation=sbol3.SBOL_INLINE, types=sbol3.SBO_DNA)
				temp.features.append(tempLocalSub)
				variant_comps.append(tempLocalSub)
				varFeature = sbol3.VariableFeature(cardinality=sbol3.SBOL_ONE, variable=f'{sbol3.get_namespace()}/{temp.display_id}/{tempLocalSub.display_id}')
				for part in comp.split(", "):
					varFeature.variants.append(f'{sbol3.get_namespace()}/{helpers.check_name(part)}')
				rowobj.obj.variable_features.append(varFeature)
				if comp_ind != 0:
					constr = sbol3.Constraint(restriction=sbol3.SBOL_MEETS, object=tempLocalSub, subject=variant_comps[comp_ind -1])
					temp.constraints.append(constr)
				
				comp_ind += 1
			else:
				tempSub = sbol3.SubComponent(name=f'Part {comp_ind + 1}', instance_of=f'{rowobj.obj_dict[comp]["uri"]}', orientation=sbol3.SBOL_INLINE)
				temp.features.append(tempSub)
				variant_comps.append(tempSub)
				if comp_ind != 0:
					constr = sbol3.Constraint(restriction=sbol3.SBOL_MEETS, object=tempSub, subject=variant_comps[comp_ind -1])
					temp.constraints.append(constr)
				comp_ind += 1

		if 'backbone' in rowobj.col_cell_dict:
			template = temp
			
		else:
			template = rowobj.obj_dict[f'{rowobj.obj.display_id}_template']['object']

		if constraints:
			for constraint in c_list:
				template.constraints.append(constraint)

	else:
		raise KeyError(f'The object type "{type(rowobj.obj)}" does not allow subcomponents. (sheet:{rowobj.sheet}, row:{rowobj.sht_row}, sbol term dict:{rowobj.col_cell_dict})')

def dataSource(rowobj):
	prefs = rowobj.col_cell_dict['pref']
	vals = rowobj.col_cell_dict['val']
	for colnum in range(len(prefs.keys())):
		# as column names are different for the different multicol values
		pref = prefs[list(prefs.keys())[colnum]]
		val = vals[list(vals.keys())[colnum]]

		datasource_dict = {'GenBank':{'Replace Example':'https://www.ncbi.nlm.nih.gov/nuccore/{REPLACE_HERE}', 'Literal Part':'TRUE', 'Namespace':'https://www.ncbi.nlm.nih.gov/nuccore', 'Prefix':'gb'},
				   'PubMed':{'Replace Example':'https://pubmed.ncbi.nlm.nih.gov/{REPLACE_HERE}/', 'Literal Part':'FALSE', 'Namespace':'', 'Prefix':'', 'derived_from':''},
				   'iGEM registry':{'Replace Example':'http://parts.igem.org/Part:{REPLACE_HERE}', 'Literal Part':'TRUE', 'Namespace':'http://parts.igem.org', 'Prefix':'igem'},
				   'AddGene':{'Replace Example':'https://www.addgene.org/{REPLACE_HERE}/', 'Literal Part':'FALSE', 'Namespace':'', 'Prefix':''},
				   'Seva plasmids':{'Replace Example':'http://www.sevahub.es/public/Canonical/{REPLACE_HERE}/1', 'Literal Part':'TRUE', 'Namespace':'', 'Prefix':''},
				   'Tax_id':{'Replace Example':'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={REPLACE_HERE}', 'Literal Part':'FALSE', 'Namespace':'', 'Prefix':''},
				   'SynBioHub':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'TRUE', 'Namespace':'', 'Prefix':''},
				   'URL':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'FALSE', 'Namespace':val, 'Prefix':'', 'derived_from':f'{val}/{rowobj.obj.displayId}'},
				   'Local Sequence File':{'Replace Example':'', 'Literal Part':'FALSE', 'Namespace':'', 'Prefix':''},
				   'URL for GenBank file':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'TRUE', 'Namespace':'', 'Prefix':''},
				   'URL for FASTA file':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'TRUE', 'Namespace':'', 'Prefix':''}
						}

		literal = datasource_dict[pref]['Literal Part']

		if literal == 'FALSE':
			if len(datasource_dict[pref]['derived_from']) > 0:
				rowobj.obj.derived_from = [datasource_dict[pref]['derived_from']]
			ns = datasource_dict[pref]['Namespace']
			if len(ns) > 0:
				if len(datasource_dict[pref]['Prefix']) > 0:
					if datasource_dict[pref]['Prefix'] not in rowobj.doc_pref_terms:
						rowobj.doc.bind(datasource_dict[pref]['Prefix'], ns)
						rowobj.doc_pref_terms.append(datasource_dict[pref]['Prefix'])
				
				old_id = rowobj.obj.identity
				rowobj.doc.change_object_namespace([rowobj.obj], ns)
				new_id = rowobj.obj.identity
				rowobj.data_source_id_to_update[old_id] = new_id

		else:
			ns = datasource_dict[pref]['Namespace']
			if len(ns) > 0:
				if len(datasource_dict[pref]['Prefix']) > 0:
					if datasource_dict[pref]['Prefix'] not in rowobj.doc_pref_terms:
						rowobj.doc.bind(datasource_dict[pref]['Prefix'], ns)
						rowobj.doc_pref_terms.append(datasource_dict[pref]['Prefix'])
				
				old_id = rowobj.obj.identity
				rowobj.doc.change_object_namespace([rowobj.obj], ns)
				new_id = rowobj.obj.identity
				rowobj.data_source_id_to_update[old_id] = new_id
				if val != rowobj.obj.display_id:
					new_identity = str(rowobj.obj.identity).replace(rowobj.obj.display_id, helpers.check_name(val))
					id_map = {rowobj.obj.identity:new_identity}
					rowobj.obj.set_identity(new_identity)
					rowobj.obj.update_all_dependents(id_map) # this function doesn't yet do everything it should
					rowobj.data_source_id_to_update[old_id] = new_identity

			if pref == 'URL for GenBank file' or pref == 'URL for FASTA file':	
				# Namespace is everything except the last part of the url
				# Loop backward through the value until a '/' is found
				# Everything before the '/' is the namespace
				old_val = val

				# Loop through the string backwards
				for i in range(len(val) - 1, 0, -1):
					if val[i] == '/':
						# Everything before the '/' is the namespace
						ns = val[:i]

						# Everything after the '/' is the display id
						val = val[i+1:len(val) - 3]

						break
				old_id = rowobj.obj.identity
				rowobj.doc.change_object_namespace([rowobj.obj], ns)
				new_id = rowobj.obj.identity
				rowobj.data_source_id_to_update[old_id] = new_id
				rowobj.obj.derived_from = [old_val]
				if val != rowobj.obj.display_id:
					new_identity = str(rowobj.obj.identity).replace(rowobj.obj.display_id, helpers.check_name(val))
					id_map = {rowobj.obj.identity:new_identity}
					rowobj.obj.set_identity(new_identity)
					rowobj.obj.update_all_dependents(id_map) # this function doesn't yet do everything it should
					rowobj.data_source_id_to_update[old_id] = new_identity

def sequence(rowobj):
	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]
		if isinstance(val, str):
			# might need to be careful if the object type is sequence!
			# THIS MIGHT HAVE BUGS IF MULTIPLE SEQUENCES ARE PROVIDED FOR
			# ONE OBJECT. E.g overwrite in self.obj.sequences = [val] ?
			if re.fullmatch(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', val):
				# if a url
				rowobj.obj.sequences = [val]

			elif re.match(r'^[a-zA-Z \s*]+$', val):
				# if a sequence string

				# removes spaces, enters, and makes all lower case
				val = "".join(val.split())
				val = val.replace(u"\ufeff", "").upper()

				# create sequence object
				sequence = sbol3.Sequence(f"{rowobj.obj.namespace}/{rowobj.obj.display_id}_sequence",
										elements=val, encoding=sbol3.IUPAC_DNA_ENCODING, namespace=rowobj.obj.namespace)
				# if rowobj.obj.name is not None:
				# 	sequence.name = f"{rowobj.obj.name} Sequence"

				rowobj.doc.add(sequence)

				# link sequence object to component definition
				rowobj.obj.sequences = [sequence]

			else:
				logging.warning(f'The cell value for {rowobj.obj.identity} is not an accepted sequence type, it has been added as a uri and left for post processing. Sequence value provided: {val} (sheet:{rowobj.sheet}, row:{rowobj.sht_row}, col:{col})')
				rowobj.obj.sequences = [val]
		else:
			raise TypeError(f"A multicolumn value was unexpectedly given in sequence, {rowobj.col_cell_dict}")

def circular(rowobj): # NOT IMPLEMENTED
	# if false add to linear collection if true add to types

	tempObj = rowobj.obj
	if rowobj.col_cell_dict['Circular'] not in tempObj.types:
		tempObj.types.append(rowobj.col_cell_dict['Circular'])

	pass

def finalProduct(rowobj):
	# create final products collection if it doesn't yet exist
	# add object to collection
	columns = rowobj.col_cell_dict
 
	for col in columns:
		# check if the cell value is true
		if columns[col]:
			doc = rowobj.doc

			sbol_objs = doc.objects
			sbol_objs_names = [x.name for x in sbol_objs]
			if 'Final Products' not in sbol_objs_names:
				colec = sbol3.Collection('FinalProducts', name='Final Products')
				colec.description = 'Final products desired for actual fabrication'

				sbol_objs = doc.objects
				sbol_objs_names = [x.name for x in sbol_objs]

				doc.add(colec)
				colec.members.append(rowobj.obj_uri)
			else:
				colec = sbol_objs[sbol_objs_names.index('Final Products')]
				colec.members.append(rowobj.obj_uri)

			if 'Linear DNA Products' not in sbol_objs_names:
				colec = sbol3.Collection('LinearDNAProducts', name='Linear DNA Products')
				colec.description = 'Linear DNA constructs to be fabricated'

				sbol_objs = doc.objects
				sbol_objs_names = [x.name for x in sbol_objs]

				doc.add(colec)
				colec.members.append(rowobj.obj)
			else:
				colec = sbol_objs[sbol_objs_names.index('Linear DNA Products')]
				colec.members.append(rowobj.obj)

			
			#add obj as member to final products
			

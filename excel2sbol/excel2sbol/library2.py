import sbol2
import excel2sbol.helpers as hf
import re
import logging
import requests
import urllib.parse
import webbrowser
import excel2sbol.converter as conv
import os 
import sys
import json
# might be better if some of the ones like data sources were put in a library
# which contained both sbol2 and sbol3. Then excel converter could check
# if in lib2 or lib_both for version 2 and lib3 or lib_both for version 3
# would reduce code duplication?

def biochemical_reaction(rowobj):
	chemical_name = rowobj.obj_uri.split("/")[-1]
	chemical_uri = rowobj.obj_uri
	module_def_name = f"{chemical_name}_production"
	
	enzyme_name = None
	substrate_name = None
	username = os.getenv("SBOL_USERNAME")
	password = os.getenv("SBOL_PASSWORD")
	url = os.getenv("SBOL_URL")
	
	if module_def_name not in [m.displayId for m in rowobj.doc.moduleDefinitions]:
		module_def = sbol2.ModuleDefinition(module_def_name)
	else:
		module_def = rowobj.doc.moduleDefinitions.get(module_def_name)
	
	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]
		if col == "Enzyme":
			if isinstance(val, str):
				enzyme_uri = val
				enzyme_name = val.split("/")[-1]

		if col == "Enzyme (URI)":
			if isinstance(val, str):
				valid_uri = link_validation(username, password, url, val)
				if not valid_uri:
					print(f"URI in '{val}' is invalid. Skipping addition for {col}.")
					print("Terminating")
					sys.exit(1)
					continue
				else:
					enzyme_uri = val
					enzyme_name = val.split("/")[-2]

		if col == "Substrate":
			if isinstance(val, str):
				substrate_uri = val
				substrate_name = val.split("/")[-1]
		
		if col == "Substrate (URI)":
			if isinstance(val, str):
				valid_uri = link_validation(username, password, url, val)
				if not valid_uri:
					print(f"URI in '{val}' is invalid. Skipping addition for {col}.")
					print("Terminating")
					sys.exit(1)
					continue
				else:
					substrate_uri = val
					substrate_name = val.split("/")[-2]

				
	# enzyme not provided
	if substrate_name is None:
		print("Substrate not provided. Just FC for enzyme will be created.")
		if enzyme_name not in [fc.displayId for fc in module_def.functionalComponents]:
			enzyme_fc = module_def.functionalComponents.create(enzyme_name)
			enzyme_fc.definition = enzyme_uri
		else:
			enzyme_fc = module_def.functionalComponents.get(enzyme_name)
		rowobj.doc.addModuleDefinition(module_def)
		return
	
	# substrate not provided
	if enzyme_name is None:
		print("Enzyme not provided. Just FC for substrate will be created.")
		if substrate_name not in [fc.displayId for fc in module_def.functionalComponents]:
			substrate_fc = module_def.functionalComponents.create(substrate_name)
			substrate_fc.definition = substrate_uri
		else:
			substrate_fc = module_def.functionalComponents.get(substrate_name)
		rowobj.doc.addModuleDefinition(module_def)
		return
	

	# substrate fc
	if substrate_name not in [fc.displayId for fc in module_def.functionalComponents]:
		substrate_fc = module_def.functionalComponents.create(substrate_name)
		substrate_fc.definition = substrate_uri
	else:
		substrate_fc = module_def.functionalComponents.get(substrate_name)

	# enzyme fc
	if enzyme_name not in [fc.displayId for fc in module_def.functionalComponents]:
		enzyme_fc = module_def.functionalComponents.create(enzyme_name)
		enzyme_fc.definition = enzyme_uri
	else:
		enzyme_fc = module_def.functionalComponents.get(enzyme_name)
	
	# chemical fc
	if chemical_name not in [fc.displayId for fc in module_def.functionalComponents]:
		chemical_fc = module_def.functionalComponents.create(chemical_name)
		chemical_fc.definition = chemical_uri
	else:
		chemical_fc = module_def.functionalComponents.get(chemical_name)
	
	# participation for substrate
	participation_substrate = sbol2.Participation(uri = f'{substrate_name}_reactant')
	participation_substrate.participant = substrate_fc
	participation_substrate.uri = f'{substrate_name}_reactant'
	participation_substrate.roles = [sbol2.SBO_REACTANT]

	# participation for enzyme
	participation_enzyme = sbol2.Participation(uri = f'{enzyme_name}_modifier')
	participation_enzyme.participant = enzyme_fc
	participation_enzyme.uri = f'{enzyme_name}_modifier'
	participation_enzyme.roles = ["http://identifiers.org/biomodels.sbo/SBO:0000019"] #'SBO_MODIFIER'

	# participation for profuct
	participation_product = sbol2.Participation(uri = f'{chemical_name}_product')
	participation_product.participant = chemical_fc
	participation_product.uri = f'{chemical_name}_product'
	participation_product.roles = [sbol2.SBO_PRODUCT]

	# define the interaction
	interaction_name = f'{chemical_name}_biochemical_reaction'
	interaction_type = sbol2.SBO_BIOCHEMICAL_REACTION
	interaction = sbol2.Interaction(interaction_name, interaction_type)

	interaction.participations.add(participation_substrate)
	interaction.participations.add(participation_enzyme)
	interaction.participations.add(participation_product)
	
	module_def.interactions.add(interaction)
	rowobj.doc.addModuleDefinition(module_def)
		
		
def module(rowobj):
	module_name_pref = rowobj.obj_uri.split("/")[-1]
	# print("Module Def Name: ", module_name_pref)
	module_def_name = f"{module_name_pref}_module_definition"
	if module_def_name not in [m.displayId for m in rowobj.doc.moduleDefinitions]:
		module_def = sbol2.ModuleDefinition(module_def_name)
	else:
		module_def = rowobj.doc.moduleDefinitions.get(module_def_name)
	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]

		for col in rowobj.col_cell_dict.keys():
			val = rowobj.col_cell_dict[col]

			if isinstance(val, str):
				module_uris = val.split(",")

			for module_uri in module_uris:
				module_uri = module_uri.strip()
				module_name = module_uri.split("/")[-2]
				# print("Module Name: ", module_name)
				# print("Module URI: ", module_uri)
				if module_name not in [m.displayId for m in module_def.modules]:
					mod = module_def.modules.create(module_name)
					mod.definition = module_uri
				else:
					mod = module_def.modules.get(module_name)
			
	if module_name not in [m.displayId for m in rowobj.doc.moduleDefinitions]:
		rowobj.doc.addModuleDefinition(module_def)	


def funcComp(rowobj):
	module_def_name = rowobj.obj_uri.split("/")[-1]
	# print("MD Name: ", module_def_name)
	fc_name = None
	module_name = f"{module_def_name}_module_definition"
	if module_name not in [m.displayId for m in rowobj.doc.moduleDefinitions]:
		module_def = sbol2.ModuleDefinition(module_name)
	else:
		module_def = rowobj.doc.moduleDefinitions.get(module_name)

	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]
		# print("FC links: ", val)
		fc_uris = [val] if isinstance(val, str) else val
		
		for fc_uri in fc_uris:
			fc_name = fc_uri.split("/")[-2]
			# print("FC Name: ", fc_name)
			# print("FC URI: ", fc_uri)
			if fc_name not in [fc.displayId for fc in module_def.functionalComponents]:
				fc = module_def.functionalComponents.create(fc_name)
				fc.definition = fc_uri
			else:
				fc = module_def.functionalComponents.get(fc_name)
			
	if module_name not in [m.displayId for m in rowobj.doc.moduleDefinitions]:
		rowobj.doc.addModuleDefinition(module_def)	



def objectType(rowobj):
    # used to decide the object type in the converter function
    pass

def is_url(str):
	try:
		res = urllib.parse.urlparse(str)
		return all([res.scheme, res.netloc])
	except ValueError:
		return False

def displayId(rowobj):
    # used to check the object display id in the converter function
	username = os.getenv("SBOL_USERNAME")
	password = os.getenv("SBOL_PASSWORD")
	
	dict = os.getenv("SBOL_DICTIONARY")
	data = json.loads(dict)
	url = data["Domain"].strip()
	if url.endswith('/'):
		url = url[:-1]
	collection = data["Library Name"]
	
	master_collection = False
	private_collection = False
	if data["Domain"].strip() == "":
		# print("No domain name provided. Proceeding without checking displayId.")
		return
	
	if is_url(collection) == False:
		private_collection = False
		
		if data["Master Collection"].strip() == "":
			master_collection = False
		else:
			collection = data["Master Collection"]
			master_collection = True
	else:
		private_collection = True

		
	
	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]

		if col == "Previous Version (URI)":
			# print(rowobj.obj)
			# print(rowobj.col_cell_dict)
			display_id = rowobj.col_cell_dict['Part Id']
			previous_id = rowobj.col_cell_dict['Previous Version (URI)']
			rowobj.obj.wasDerivedFrom = previous_id
			return
		
		val = hf.check_name(val)
		# print("Display ID: ", val)
		
		if private_collection == True:
			
			if username is None or password is None or url is None:
				print("No login credentials provided. Proceeding without login.")
				print("Unable to search in a private collection without login credentials.")
				print("Terminating")
				sys.exit(1)
			else:
				part_shop = sbol2.PartShop(collection)
				try:
					part_shop.login(username, password)
				except Exception as e:
					print(f"Login failed: {e}")
					exit(1)

				search_results = part_shop.search_exact(val, property_uri='http://sbols.org/v2#displayId')
				if len(search_results) > 0 :
					for part in search_results:
						print(f"Part with display ID:  {part.displayId}  already exists in the collection at URL {part.identity}.")
						print("XML file will NOT be generated.")
						os.environ["COUNTER"] = "Error found"

		else:
			
			if master_collection == True:
				
				# part_shop = sbol2.PartShop(collection)
				if username is None or password is None or url is None:
					
					part_shop = sbol2.PartShop(collection)
				else:
					part_shop = sbol2.PartShop(collection)
					try:
						part_shop.login(username, password)
					except Exception as e:
						print(f"Login failed: {e}")
						exit(1)

				search_results = part_shop.search_exact(val, property_uri='http://sbols.org/v2#displayId')
				if len(search_results) > 0 :
					for part in search_results:
						print(f"Part with display ID:  {part.displayId}  already exists in the collection at URL {part.identity}.")
						print("XML file will NOT be generated.")
						os.environ["COUNTER"] = "Error found"
			elif master_collection == False:
				
				# part_shop = sbol2.PartShop(url)
				if username is None or password is None or url is None:
					
					part_shop = sbol2.PartShop(url)
				else:
					part_shop = sbol2.PartShop(collection)
					try:
						part_shop.login(username, password)
					except Exception as e:
						print(f"Login failed: {e}")
						exit(1)
				search_results = part_shop.search_exact(val, property_uri='http://sbols.org/v2#displayId')
				if len(search_results) > 0 :
					for part in search_results:
						print(f"Part with display ID:  {part.displayId}  already exists in the collection at URL {part.identity}.")
						print("Just a warning. XML file will be generated.")
				
		
		

	


    

def types(rowobj):
    for col in rowobj.col_cell_dict.keys():
        # overwrites standard #DnaRegion biopax where another type is given
        val = rowobj.col_cell_dict[col]
        if val not in rowobj.obj.types[0] and len(rowobj.obj.types) == 1:
            rowobj.obj.types = val

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


def moduleModuleDefiniton(rowobj): #NOT IMPLEMENTED
    # module_name_pref = self.obj_uri.split("/")[-1]
    # module_name_suf = self.cell_val.split("/")[-1]
    # mod1 = sbol2.Module(f"{module_name_pref}_{module_name_suf}")
    # mod1.definition = self.cell_val

    # self.obj.modules.add(mod1)
    pass

def additionalFuncComponent(rowobj): #NOT IMPLEMENTED
    # fc_name_pref = self.obj_uri.split("/")[-1]
    # fc_name_suf = self.cell_val.split("/")[-1]

    # fc1 = sbol2.FunctionalComponent(f"{fc_name_pref}_{fc_name_suf}")
    # fc1.definition = self.cell_val
    # self.obj.functionalComponents.add(fc1)
    pass

def definedFuncComponent(rowobj): #NOT IMPLEMENTED
    # if isinstance(self.cell_val, list):
    #     # pulling the functional component object
    #     # by the name (hence the split) from the obj_cit
    #     fcobj = self.obj_dict[self.cell_val[0].split("/")[-1]]['object']
    # else:
    #     # pulling the functional component object
    #     # by the name (hence the split) from the obj_cit
    #     fcobj = self.obj_dict[self.cell_val.split("/")[-1]]['object']

    # # print(self.obj, fcobj)
    # self.obj.functionalComponents.add(fcobj.copy())
    pass

def sequence_authentication(email, password, base_url,uri):
	
	login_data = {
		'email': email, 
		'password': password
	}
	if email is None or password is None or base_url is None:
		seq_search = requests.get(
					f'https://synbiohub.org/{uri}',
					headers={
						'Accept': 'application/json'
		}
				)
		if seq_search.status_code == 200:
			public_results = seq_search.json()
			if public_results:
				if len(public_results) > 1:
					print("Number of duplicate sequences found: ", len(public_results))
				for result in public_results:
					print("The sequence already exists in the public repository. The URI is: ", result['uri'])
					return False
		else:
			# print("Sequence not found in public repository.")
			# double check the logic fo public repos and sequence search
			return True
	else:
		login_response = requests.post(
			f"{base_url}/login",
			headers={
				'Accept': 'plain/text'
			},
			data= login_data
		)
	if login_response.status_code == 200:
		sequence_search_response = requests.get(
					uri,
					headers={
						'Accept': 'application/json',
						'X-authorization': login_response.content
						}
				)
		if sequence_search_response.status_code == 200:
			search_results = sequence_search_response.json()
			if search_results:
				if len(search_results) > 1:
					
					print("Number of duplicate sequences found: ", len(search_results))
				for result in search_results:
					print("The sequence already exists in the database. The URI is: ", result['uri'])
					os.environ["COUNTER"] = "Error found"
				
				return False
		else:
			print("Sequence does not exist in the database. Adding sequence.")
			return True

		
		return True
	else:
		print("Login failed.")
		return False
	

def link_validation(email, password, base_url, target_url):
	# initial check w/out auth
	# print("Checking link: ", target_url)
	login_data = {
					'email': email, 
					'password': password
				}

	initial_response = requests.get(target_url, headers={'Accept': 'application/json'})
	# print("Initital response status code: ", initial_response.status_code)
	if initial_response.status_code == 200:
		# print("Link is accessible without authentication.")
		return True  
    
	# the link is not accessible without authentication, try logging in
	elif initial_response.status_code in {401, 403, 404}:
		if email is None or password is None or base_url is None:
			print(f"Need login credentials to access the link {target_url}.")
			print("This is a warning. XML file will NOT be generated.")
			os.environ["COUNTER"] = "Error found"
			# i just changed this to return True, but it was False
			return True
		else:
			login_response = requests.post(
				f"{base_url}/login",
				headers={
					'Accept': 'plain/text'
				},
				data= login_data
			)
			# print("Login response status code: ", login_response.status_code)
			
		
		# check if login was successful
		if login_response.status_code == 200:
			# retry accessing the link after logging in
			final_response = requests.get(target_url,headers = {'Accept': 'application/json', 'X-authorization': login_response.content})
			if final_response.status_code == 200:
				# print("Link is accessible after authentication.")
				return True
			else:
				# print("Link is not accessible after authentication.")
				return False
		
	print("Link is not accessible.")
	return False

def encodesFor(rowobj):

    module_name_pref = rowobj.obj_uri.split("/")[-1]
    module_name_suf = None
    username = os.getenv("SBOL_USERNAME")
    password = os.getenv("SBOL_PASSWORD")
    url = os.getenv("SBOL_URL")
    # print(rowobj.col_cell_dict)
    dict = os.getenv("SBOL_DICTIONARY")
    data = json.loads(dict)
	
    
    for col in rowobj.col_cell_dict.keys():
        val = rowobj.col_cell_dict[col]
        # print("Val: ", val)
        if isinstance(val, str):
            if col == "Encodes for":	
                module_name_suf = val.split("/")[-1]
                protein_comp_uri = val
                break
            elif col == "Encodes for (URI)":
                valid_uri = link_validation(username, password, url, val)
               
                if not valid_uri:
                    print(f"URI '{val}' is invalid. Skipping addition for {col}.")
                    print("Terminating")
                    sys.exit(1)
                    # return
                module_name_suf = val.split("/")[-2]
                protein_comp_uri = val
                break
   

	# create a new module definitions
    module_name = f"{module_name_pref}_{module_name_suf}"
   
    module_def = sbol2.ModuleDefinition(module_name)
    
	#create a fc for the protein
    if module_name_suf not in [fc.displayId for fc in module_def.functionalComponents]:
        protein_fc = module_def.functionalComponents.create(module_name_suf)
        protein_fc.definition = protein_comp_uri
    else:
        protein_fc = module_def.functionalComponents.get(module_name_suf)

	#create a fc for the dna
    if module_name_pref not in [fc.displayId for fc in module_def.functionalComponents]:
        dna_fc = module_def.functionalComponents.create(module_name_pref)
        dna_fc.definition = rowobj.obj_uri
    else:
        dna_fc = module_def.functionalComponents.get(module_name_pref)
      

    # participation_name = f'{module_name_pref}_template'
    participation = sbol2.Participation(uri = f'{module_name_pref}_template')
    participation.participant = dna_fc
    participation.uri = f'{module_name_pref}_template'
    participation.roles = [sbol2.SBOL_TEMPLATE]


    # participation_name2 = f'{module_name_suf}_product'
    participation2 = sbol2.Participation(uri= f'{module_name_suf}_product')
    participation2.participant = protein_fc
    participation2.uri = f'{module_name_suf}_product'
    participation2.roles = [sbol2.SBO_PRODUCT]


    interaction_name = f'{module_name_suf}_production'
    interaction_type = sbol2.SBO_GENETIC_PRODUCTION
    interaction = sbol2.Interaction(interaction_name, interaction_type)
    interaction.participations.add(participation)
    interaction.participations.add(participation2)

    module_def.interactions.add(interaction)
    rowobj.doc.addModuleDefinition(module_def)


def repressor(rowobj):
    module_name_pref = rowobj.obj_uri.split("/")[-1]
    # print(rowobj.col_cell_dict)
    module_name_suf = None
    for col in rowobj.col_cell_dict.keys():
        val = rowobj.col_cell_dict[col]
        username = os.getenv("SBOL_USERNAME")
        password = os.getenv("SBOL_PASSWORD")
        url = os.getenv("SBOL_URL")
        # print(username, password, url)
        if col == "Repressors (URI)" and isinstance(val, str):
            protein_comp_uris = val.split(",")
            # print("Protein comp uris: ", protein_comp_uris)
            
            for uri in protein_comp_uris:
                valid_uri = link_validation(username, password, url, uri)
                if not valid_uri:
                    print(f"URI '{val}' is invalid. Skipping addition for {col}.")
                    print("Terminating")
                    sys.exit(1)
                    continue
        else:
            protein_comp_uris = [val] if isinstance(val, str) else val

        for protein_comp_uri in protein_comp_uris:
            if col == "Repressors":
                module_name_suf = protein_comp_uri.split("/")[-1]

            elif col == "Repressors (URI)":
                module_name_suf = protein_comp_uri.split("/")[-2]

            module_name = f"{module_name_pref}_{module_name_suf}"
            module_def = sbol2.ModuleDefinition(module_name)

            if module_name_suf not in [fc.displayId for fc in module_def.functionalComponents]:
                protein_fc = module_def.functionalComponents.create(module_name_suf)
                protein_fc.definition = protein_comp_uri
            else:
                protein_fc = module_def.functionalComponents.get(module_name_suf)

            # create a dna functional component
            if module_name_pref not in [fc.displayId for fc in module_def.functionalComponents]:
                dna_fc = module_def.functionalComponents.create(module_name_pref)
                dna_fc.definition = rowobj.obj_uri
            else:
                dna_fc = module_def.functionalComponents.get(module_name_pref)

            # participation_name = f'{module_name_pref}_template'
            participation = sbol2.Participation(uri = f'{module_name_pref}_inhibited')
            participation.participant = dna_fc
            participation.uri = f'{module_name_pref}_inhibited'
            participation.roles = [sbol2.SBO_INHIBITED]


            # participation_name2 = f'{module_name_suf}_product'
            participation2 = sbol2.Participation(uri= f'{module_name_suf}_inhibition')
            participation2.participant = protein_fc
            participation2.uri = f'{module_name_suf}_inhibitor'
            participation2.roles = [sbol2.SBO_INHIBITOR]

            interaction_name = f'{module_name_suf}_repression'
            interaction_type = sbol2.SBO_INHIBITION
            interaction = sbol2.Interaction(interaction_name, interaction_type)
            interaction.participations.add(participation)
            interaction.participations.add(participation2)

            module_def.interactions.add(interaction)
            rowobj.doc.addModuleDefinition(module_def)


def activator(rowobj):

	module_name_pref = rowobj.obj_uri.split("/")[-1]
	module_name_suf = None
	# print(rowobj.col_cell_dict)
	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]
		username = os.getenv("SBOL_USERNAME")
		password = os.getenv("SBOL_PASSWORD")
		url = os.getenv("SBOL_URL")

		if col == "Activators (URI)" and isinstance(val, str):
			# print("Protein comp uris: ", val)
			protein_comp_uris = val.split(",")
			
			for uri in protein_comp_uris:
				# print(uri)
				valid_uri = link_validation(username, password, url, uri)
				if not valid_uri:
					print(f"URI in '{uri}' is invalid. Skipping addition for {col}.")
					print("Terminating")
					sys.exit(1)
					continue

		else:
			protein_comp_uris = [val] if isinstance(val, str) else val
		# print("Val: ", val)
		for protein_comp_uri in protein_comp_uris:

			if col == "Activators":
				# print("Protein comp uri: ", protein_comp_uri)
				module_name_suf = protein_comp_uri.split("/")[-1]

			elif col == "Activators (URI)":
				# print("Protein comp uri: ", protein_comp_uri)
				module_name_suf = protein_comp_uri.split("/")[-2]

			module_name = f"{module_name_pref}_{module_name_suf}"
			module_def = sbol2.ModuleDefinition(module_name)

			if module_name_suf not in [fc.displayId for fc in module_def.functionalComponents]:
				protein_fc = module_def.functionalComponents.create(module_name_suf)
				protein_fc.definition = protein_comp_uri
			else:
				protein_fc = module_def.functionalComponents.get(module_name_suf)

			# create a dna functional component
			if module_name_pref not in [fc.displayId for fc in module_def.functionalComponents]:
				dna_fc = module_def.functionalComponents.create(module_name_pref)
				dna_fc.definition = rowobj.obj_uri
			else:
				dna_fc = module_def.functionalComponents.get(module_name_pref)

			participation = sbol2.Participation(uri = f'{module_name_pref}_stimulated')
			participation.participant = dna_fc
			participation.uri = f'{module_name_pref}_stimulated'
			participation.roles = [sbol2.SBO_STIMULATED]



			participation2 = sbol2.Participation(uri= f'{module_name_suf}_stimulation')
			participation2.participant = protein_fc
			participation2.uri = f'{module_name_suf}_stimulator'
			participation2.roles = [sbol2.SBO_STIMULATOR]

			interaction_name = f'{module_name_suf}_activation'
			interaction_type = sbol2.SBO_STIMULATION
			interaction = sbol2.Interaction(interaction_name, interaction_type)
			interaction.participations.add(participation)
			interaction.participations.add(participation2)

			module_def.interactions.add(interaction)
			rowobj.doc.addModuleDefinition(module_def)     	

def complexComponent(rowobj):

	module_name_pref = rowobj.obj_uri.split("/")[-1]
	module_name_suf = None
	protein_comp_uri = None
	molecule_name = None
	molecule_comp_uri = None
	components = []
	username = os.getenv("SBOL_USERNAME")
	password = os.getenv("SBOL_PASSWORD")
	url = os.getenv("SBOL_URL")
	# if Components column present
	
	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]
		if col == "Components Ids":
			if isinstance(val, list) and len(val) > 0:
				
				for i in val[0:]:
					components.append((i.split("/")[-1], i))

		if col == "Components (URI)":
			if isinstance(val, list) and len(val) > 0:
				if isinstance(val, list) and len(val) > 0:
					invalid_uris = []  
					for uri in val:
						valid_uri = link_validation(username, password, url, uri)
						if not valid_uri:
							print(f"URI '{uri}' is invalid. Skipping addition for {col}.")
							invalid_uris.append(uri)

					if invalid_uris:
						print(f"Invalid URIs detected: {invalid_uris}. Skipping entire complex formation.")
						print("Terminating")
						sys.exit(1)
                		
						return
					else:
						# Process valid URIs

						for i in val[0:]:
							components.append((i.split("/")[-2], i))
				
	module_name = f"{module_name_pref}_complex_formation"    
	# create a new module definition
	module_def = sbol2.ModuleDefinition(module_name)



	# create a product functional component
	if module_name_pref not in [fc.displayId for fc in module_def.functionalComponents]:
		prod_fc = module_def.functionalComponents.create(module_name_pref)
		prod_fc.definition = rowobj.obj_uri
	else:
		prod_fc = module_def.functionalComponents.get(module_name_pref)
	
	# if exists, create functional components
	components_FC = []
	
	for name, uri in components:
		if name not in [fc.displayId for fc in module_def.functionalComponents]:
			elem_fc = module_def.functionalComponents.create(name)
			elem_fc.definition = uri
			components_FC.append(elem_fc)
		else:
			elem_fc = module_def.functionalComponents.get(name)
			components_FC.append(elem_fc)
	
	# participation for product
	participation = sbol2.Participation(uri = f'{module_name_pref}_product')
	participation.participant = prod_fc
	participation.uri = f'{module_name_pref}_product'
	participation.roles = [sbol2.SBO_PRODUCT]



	#create participation for each component
	components_participants = []
	for elem_fc in components_FC:
		participation3 = sbol2.Participation(uri= f'{elem_fc.displayId}_reactor')
		participation3.participant = elem_fc
		participation3.uri = f'{elem_fc.displayId}_reactor'
		participation3.roles = [sbol2.SBO_REACTANT]
		components_participants.append(participation3)
	
	# define the interaction
	interaction_name = f'{module_name_pref}_complex_formation'
	interaction_type = sbol2.SBO_NONCOVALENT_BINDING
	interaction = sbol2.Interaction(interaction_name, interaction_type)
	interaction.participations.add(participation)
	# interaction.participations.add(participation2)
	for part in components_participants:
		interaction.participations.add(part)

	module_def.interactions.add(interaction)
	rowobj.doc.addModuleDefinition(module_def)


    


def subcomponents(rowobj):
	sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
	if 'subcomp' in rowobj.col_cell_dict:
		subcomps = list(rowobj.col_cell_dict['subcomp'].values())
	if 'constraint' in rowobj.col_cell_dict:
		constraints = list(rowobj.col_cell_dict['constraint'].values())
	else:
		constraints = []

	if len(constraints) > 0:
		logging.warning(f'Constraints have not yet been implemented')

	#print(type(rowobj.obj))

    # if type is compdef do one thing, if combdev do another, else error
	if isinstance(rowobj.obj, sbol2.componentdefinition.ComponentDefinition):
		subcomps = [hf.check_name(x) for x in subcomps]	
		rowobj.obj.assemblePrimaryStructure(subcomps)
		#rowobj.obj.compile(assembly_method=None) #need to fix range for annotations if the sequence is only added later.

	elif isinstance(rowobj.obj, sbol2.combinatorialderivation.CombinatorialDerivation):
		comp_list = subcomps
		#print(f'comp list:{comp_list}')
		comp_ind = 0
		variant_comps = {}
		non_var_comps = []
		for ind, comp in enumerate(comp_list):
			if "," in comp or type(rowobj.obj_dict[comp]['object']) == \
									sbol2.combinatorialderivation.CombinatorialDerivation:
				comp_list[ind] = f'{rowobj.obj.displayId}_subcomponent_{comp_ind}'
				uri = f'{rowobj.obj.displayId}_subcomponent_{comp_ind}'
				sub_comp = sbol2.ComponentDefinition(uri)
				sub_comp.displayId = f'{rowobj.obj.displayId}_subcomponent_{comp_ind}'
				rowobj.doc.add(sub_comp)
				variant_comps[f'subcomponent_{comp_ind}'] = {'object': sub_comp, 'variant_list': comp}
				comp_ind += 1
			else:
				comp_list[ind] = hf.check_name(comp_list[ind])
				non_var_comps.append(hf.check_name(comp_list[ind]))

		template = sbol2.ComponentDefinition(f'{rowobj.obj.displayId}_template')
		template.displayId = f'{rowobj.obj.displayId}_template'
		rowobj.doc.add(template)

		#print(comp_list)
		#print(non_var_comps)
		template.assemblePrimaryStructure(comp_list)
		#template.compile(assembly_method=None)
		
		#or comp in non_var_comps:
			

		rowobj.obj.masterTemplate = template
		for var in variant_comps:
			#var = hf.check_name(var)
			var_comp = sbol2.VariableComponent(f'var_{var}')
			var_comp.displayId = f'var_{var}'
			var_comp.variable = variant_comps[var]['object']

			var_list = re.split(",", variant_comps[var]['variant_list'])
			var_list = [f'{sbol2.getHomespace()}{hf.check_name(x.strip())}' for x in var_list]
			var_comp.variants = var_list
			rowobj.obj.variableComponents.add(var_comp)

	else:
		raise KeyError(f'The object type "{type(rowobj.obj)}" does not allow subcomponents. (sheet:{rowobj.sheet}, row:{rowobj.sht_row}, col:{rowobj.col_cell_dict})')

def dataSource(rowobj):
	prefs = rowobj.col_cell_dict['pref']
	vals = rowobj.col_cell_dict['val']
	for colnum in range(len(prefs.keys())):
		# as column names are different for the different multicol values
		pref = prefs[list(prefs.keys())[colnum]]
		val = vals[list(vals.keys())[colnum]]

		datasource_dict = {'genbank':{'Replace Example':'https://www.ncbi.nlm.nih.gov/nuccore/{REPLACE_HERE}', 'Literal Part':'FALSE'},
						'pubmed':{'Replace Example':'https://pubmed.ncbi.nlm.nih.gov/{REPLACE_HERE}/', 'Literal Part':'FALSE'},
						'igem registry':{'Replace Example':'http://parts.igem.org/Part:{REPLACE_HERE}', 'Literal Part':'FALSE'},
						'addgene':{'Replace Example':'https://www.addgene.org/{REPLACE_HERE}/', 'Literal Part':'FALSE'},
						'seva plasmids':{'Replace Example':'http://www.sevahub.es/public/Canonical/{REPLACE_HERE}/1', 'Literal Part':'FALSE'},
						'tax_id':{'Replace Example':'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={REPLACE_HERE}', 'Literal Part':'FALSE'},
						'synbiohub':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'FALSE'},
						'local sequence file':{'Replace Example':'', 'Literal Part':'FALSE'},
						'url for genbank file':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'FALSE'},
						'url for fasta file':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'FALSE'},
				   		'doi':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'FALSE'}
						}
		#datasource_dict = {'GenBank':{'Replace Example':'https://www.ncbi.nlm.nih.gov/nuccore/{REPLACE_HERE}', 'Literal Part':'TRUE'},
		#				'PubMed':{'Replace Example':'https://pubmed.ncbi.nlm.nih.gov/{REPLACE_HERE}/', 'Literal Part':'FALSE'},
		#				'iGEM registry':{'Replace Example':'http://parts.igem.org/Part:{REPLACE_HERE}', 'Literal Part':'TRUE'},
		#				'AddGene':{'Replace Example':'https://www.addgene.org/{REPLACE_HERE}/', 'Literal Part':'FALSE'},
		#				'Seva plasmids':{'Replace Example':'http://www.sevahub.es/public/Canonical/{REPLACE_HERE}/1', 'Literal Part':'TRUE'},
		#				'Tax_id':{'Replace Example':'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={REPLACE_HERE}', 'Literal Part':'FALSE'},
		#				'SynBioHub':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'TRUE'},
		#				'Local Sequence File':{'Replace Example':'', 'Literal Part':'FALSE'},
		#				'URL for GenBank file':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'TRUE'},
		#				'URL for FASTA file':{'Replace Example':'{REPLACE_HERE}', 'Literal Part':'TRUE'}
		#				}

		literal = datasource_dict[pref.lower()]['Literal Part']

		if literal == 'FALSE':
			rowobj.obj.wasDerivedFrom = datasource_dict[pref.lower()]['Replace Example'].replace('{REPLACE_HERE}', str(val))

		else:
			#replace_str = datasource_dict[pref]['Replace Example']
			#rowobj.obj.wasDerivedFrom = 
			logging.warning('Literal data sources are not yet supported.')

def sequence(rowobj):
	
	for col in rowobj.col_cell_dict.keys():
		
		val = rowobj.col_cell_dict[col]
		# print(val)
		username = os.getenv("SBOL_USERNAME")
		password = os.getenv("SBOL_PASSWORD")
		url = os.getenv("SBOL_URL")
		dict = os.getenv("SBOL_DICTIONARY")
		data = json.loads(dict)
	
		if isinstance(val, str):
			# might need to be careful if the object type is sequence!
			# THIS MIGHT HAVE BUGS IF MULTIPLE SEQUENCES ARE PROVIDED FOR
			# ONE OBJECT. E.g overwrite in self.obj.sequences = [val] ?
			if re.fullmatch(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', val):
				# if a url
				# rowobj.obj.sequences = [val]

				valid_uri = link_validation(username, password, url, val)
				if not valid_uri:
					print("Terminating")
					sys.exit(1)
					return
				rowobj.obj.sequences = [val]

			elif re.match(r'^[a-zA-Z \s*]+$', val):
				# if a sequence string

				# removes spaces, enters, and makes all upper case
				val = "".join(val.split())
				val = val.replace(u"\ufeff", "").upper()

				uri = f'{url}/search/sequence={val}&'
				# if data["Domain"].strip() == "":
				# 	# print("Domain not provided. Proceding without checking the domain for duplicate sequences.")
				# 	return
				if data["Domain"].strip() != "":
					# print("Domain provided. Proceeding with checking the domain for duplicate sequences.")
					valid_uri = sequence_authentication(username, password, url,uri)
					if not valid_uri:
						print("Part name: ", rowobj.obj.identity.split('/')[-2])
						# print("Terminating")
						# sys.exit(1)
						return
				# create sequence object
				sequence = sbol2.Sequence(f"{rowobj.obj.displayId}_sequence",
										elements=val)
				if rowobj.obj.name is not None:
					sequence.name = f"{rowobj.obj.name} Sequence"

				# rowobj.doc.add(sequence)
				# MODIFIED THIS BC WAS GIVING A DUPLICATE ERROR
				if rowobj.doc.find(sequence.identity) is None:
					rowobj.doc.add(sequence)
				else:
					print(f"Object with URI {sequence.identity} already exists. Skipping addition.")

				# link sequence object to component definition
				rowobj.obj.sequences = [sequence]

			else:
				logging.warning(f'The cell value for {rowobj.obj.identity} is not an accepted sequence type, it has been added as a uri and left for post processing. Sequence value provided: {val} (sheet:{rowobj.sheet}, row:{rowobj.sht_row}, col:{col})')
				rowobj.obj.sequences = [val]
		else:
			raise TypeError(f"A multicolumn value was unexpectedly given in sequence, {rowobj.col_cell_dict}")

def proteinSequence(rowobj):

	for col in rowobj.col_cell_dict.keys():
		val = rowobj.col_cell_dict[col]
		username = os.getenv("SBOL_USERNAME")
		password = os.getenv("SBOL_PASSWORD")
		url = os.getenv("SBOL_URL")
		dict = os.getenv("SBOL_DICTIONARY")
		data = json.loads(dict)
		if isinstance(val, str):
			# might need to be careful if the object type is sequence!
			# THIS MIGHT HAVE BUGS IF MULTIPLE SEQUENCES ARE PROVIDED FOR
			# ONE OBJECT. E.g overwrite in self.obj.sequences = [val] ?
			if re.fullmatch(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', val):
				# if a url
				rowobj.obj.sequences = [val]
				valid_uri = link_validation(username, password, url, val)
				if not valid_uri:
					print(f"URI '{val}' is invalid. Skipping addition for {col}.")
					print("Terminating")
					sys.exit(1)
					return
				rowobj.obj.sequences = [val]

			elif re.match(r'^[ACDEFGHIKLMNPQRSTVWYacdefghiklmnpqrstvwy\s*]+$', val):
				# if a sequence string

				# removes spaces, enters, and makes all upper case
				val = "".join(val.split())
				# removes *
				val = val.replace('*', '')
				val = val.replace(u"\ufeff", "").upper()
				uri = f'{url}/search/sequence={val}&'
				# if data["Domain"].strip() == "":
				# 	# print("Domain not provided. Proceding without checking the domain for duplicate sequences.")
				# 	return
				if data["Domain"].strip() != "":
					# print("Domain provided. Proceeding with checking the domain for duplicate sequences.")
					valid_uri = sequence_authentication(username, password, url,uri)
					if not valid_uri:
						print("Part name: ", rowobj.obj.identity.split('/')[-2])
						# print("Terminating")
						# sys.exit(1)
						return
				
				# create sequence object
				protein_sequence = sbol2.Sequence(f"{rowobj.obj.displayId}_proteinSequence",
										elements=val, encoding='http://www.chem.qmul.ac.uk/iupac/AminoAcid/')
				if rowobj.obj.name is not None:
					protein_sequence.name = f"{rowobj.obj.name} Protein Sequence"

				rowobj.doc.add(protein_sequence)

				# link sequence object to component definition
				rowobj.obj.sequences = [protein_sequence.identity]

			else:
				logging.warning(f'The cell value for {rowobj.obj.identity} is not an accepted sequence type, it has been added as a uri and left for post processing. Sequence value provided: {val} (sheet:{rowobj.sheet}, row:{rowobj.sht_row}, col:{col})')
				rowobj.obj.sequences = [val]
		else:
			raise TypeError(f"A multicolumn value was unexpectedly given in sequence, {rowobj.col_cell_dict}")

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
			if 'FinalProducts' not in sbol_objs_names:
				colec = sbol2.Collection('FinalProducts', name='FinalProducts')

				sbol_objs = doc.objects
				sbol_objs_names = [x.name for x in sbol_objs]

				doc.add(colec)
			else:
				colec = sbol_objs[sbol_objs_names.index('FinalProducts')]
			
			# add obj as member to final products
			colec.members.append(rowobj.obj_uri)

def circular(rowobj): # NOT IMPLEMENTED
    pass

		





# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencies
import re
import sbol2
import sbol3
import pandas as pd
import logging
import excel2sbol.helper_functions as hf

class sbol_methods2:
    """A class used to implement a switch method based on an sbol_term. This
    is where the processing of column values happens.
    """

    def __init__(self, namespace_url, obj, obj_uri, obj_dict, doc, cell_value,
                 col_type, parental_lookup, sheet, col, display_id):
        """Initialisation of the sbol_methods class. This ensures
        that all the values that the switch case statements might need
        are available as properties of the self object.

        Args:
            namespace_url (str): A url to use for property definition. This
                    is only used if there is no established method function
                    associated with the sbol_term and the default method needs
                    to be used.
            component (sbol componentDefinition instance): The sbol component
                    definition that the value belongs to/should be added to
            doc (sbol doc instance): The sbol doc that the component definition
                    belongs to
            cell_value (str): The value of a cell. Due to the way it is read
                    in from excel this is expected to be a string. Manipulation
                    is possible if the type is expected to be something else,
                    e.g. integer
        """
        self.cell_val = cell_value
        self.obj = obj
        self.obj_uri = obj_uri
        self.obj_dict = obj_dict
        self.namespace_url = namespace_url
        self.doc = doc
        self.doc_pref_terms = ['rdf', 'rdfs', 'xsd', 'sbol']
        self.col_type = col_type
        self.parental_lookup = parental_lookup
        self.sheet = sheet
        self.sht_col = col
        self.sht_row = display_id

    # create method for each sbol term that can be called via the column class
    def switch(self, sbol_term):
        """Switch statement that calls a different method based on the
        sbol_term. For example if the sbol_term is sbh_alteredSequence
        then the function sbh_alteredSequence() will be run. If there is
        no function with a name equal to the sbol_term then the add_new method
        is run.

        Args:
            sbol_term (str): String indicating the method of processing
                    required by the cell_value

        Returns:
            Nothing is returned but the componentDefinition and sbol doc
            are updated according to the sbol_term and cell_value
        """
        self.sbol_term_pref = sbol_term.split("_", 1)[0]
        try:
            self.sbol_term_suf = sbol_term.split("_", 1)[1]
        except IndexError:
            raise ValueError(f"The SBOL Term '{sbol_term}' (sheet name: {self.sheet}) does not appear to have an underscore")

        if self.parental_lookup:
            # switches the object being worked on
            self.obj = self.obj_dict[self.cell_val]['object']
            self.cell_val = self.obj_uri

        # if not applicable then do nothing
        if sbol_term == "Not_applicable":
            pass

        # if a special function has been defined below then do something
        elif hasattr(self,  self.sbol_term_suf):
            return getattr(self, self.sbol_term_suf)()

        # if it is an sbol term use standard pySBOL implementation
        # unless it is a top level object in which case the standard
        # implementations don't work
        elif self.sbol_term_pref == "sbol":
            if hasattr(self.obj, self.sbol_term_suf):
                # if the attribute is a list append the new value
                if isinstance(getattr(self.obj, self.sbol_term_suf), list):
                    current = getattr(self.obj, self.sbol_term_suf)
                    # if the cell_val is a list append the whole list
                    if isinstance(self.cell_val, list):
                        setattr(self.obj, self.sbol_term_suf, current + self.cell_val)
                    else:
                        setattr(self.obj, self.sbol_term_suf, current + [self.cell_val])
                else:
                    # no iteration over list as else suggests that the property
                    # can't have multiple values
                    try:
                        current = getattr(self.obj, self.sbol_term_suf)
                        if isinstance(current, type(None)):
                            setattr(self.obj, self.sbol_term_suf, self.cell_val)
                        else:
                            if isinstance(self.cell_val, str) and isinstance(current, str):
                                value = current + "\n" + self.cell_val
                                logging.warning(f'The SBOL term {self.sbol_term_suf} for sheet:{self.sheet}, col: {self.sht_col}, row: {self.sht_row} is being concatenated {current} with {self.cell_val}')
                                setattr(self.obj, self.sbol_term_suf, value)
                    except AttributeError:
                        raise ValueError(f"Can't set attribute {self.sbol_term_pref}_{self.sbol_term_suf} for sheet:{self.sheet}, col: {self.sht_col}, row: {self.sht_row}. It is likely an issue with plural e.g. not sbol_type but sbol_types")
            else:
                raise ValueError(f'This SBOL object ({type(self.obj)}) has no attribute {self.sbol_term_suf}. The column definitions sheet SBOL Term needs to be updated. (sheet:{self.sheet}, row: {self.sht_row}, col:{self.sht_col})')

        else:
            # logging.warning(f'This sbol term ({self.sbol_term}) has not yet been implemented so it has been added via the default method')
            # define a new namespace if needed
            if self.sbol_term_pref not in self.doc_pref_terms:
                self.doc.addNamespace(self.namespace_url, self.sbol_term_pref)
                self.doc_pref_terms.append(self.sbol_term_pref)

            # if type is uri make it a uri property
            if self.col_type == "URI":
                # * allows multiple instance of this property
                if not hasattr(self.obj, self.sbol_term_suf):
                    setattr(self.obj, self.sbol_term_suf,
                            sbol2.URIProperty(self.obj,
                                              f'{self.namespace_url}{self.sbol_term_suf}',
                                              '0', '*', []))
                    setattr(self.obj, self.sbol_term_suf, self.cell_val)
                else:
                    if not isinstance(self.cell_val, list):
                        self.cell_val = [self.cell_val]
                    current = getattr(self.obj, self.sbol_term_suf)
                    setattr(self.obj, self.sbol_term_suf, current + self.cell_val)

            # otherwise implement as text property
            else:
                # * allows multiple instance of this property
                if not hasattr(self.obj, self.sbol_term_suf):
                    setattr(self.obj, self.sbol_term_suf,
                            sbol2.TextProperty(self.obj,
                                               f'{self.namespace_url}{self.sbol_term_suf}',
                                               '0', '*'))
                    setattr(self.obj, self.sbol_term_suf, str(self.cell_val))
                else:
                    if not isinstance(self.cell_val, list):
                        self.cell_val = [self.cell_val]
                    current = getattr(self.obj, self.sbol_term_suf)
                    setattr(self.obj, self.sbol_term_suf, current + self.cell_val)

    def objectType(self):
        # used to decide the object type in the converter function
        pass

    def displayId(self):
        # used to set the object display id in converter function
        pass

    def types(self):
        # overwrites standard #DnaRegion biopax where another type is given
        if self.cell_val not in self.obj.types[0] and len(self.obj.types) == 1:
            self.obj.types = self.cell_val

    def addToDescription(self):
        current = getattr(self.obj, 'description')
        if isinstance(current, type(None)):
            current = ""
        new = current + "\n" + self.sht_col + ": " + self.cell_val
        setattr(self.obj, 'description', new)


    def moduleModuleDefiniton(self):
        module_name_pref = self.obj_uri.split("/")[-1]
        module_name_suf = self.cell_val.split("/")[-1]
        mod1 = sbol2.Module(f"{module_name_pref}_{module_name_suf}")
        mod1.definition = self.cell_val

        self.obj.modules.add(mod1)

    def additionalFuncComponent(self):
        fc_name_pref = self.obj_uri.split("/")[-1]
        fc_name_suf = self.cell_val.split("/")[-1]

        fc1 = sbol2.FunctionalComponent(f"{fc_name_pref}_{fc_name_suf}")
        fc1.definition = self.cell_val
        self.obj.functionalComponents.add(fc1)

    def definedFunComponent(self):
        if isinstance(self.cell_val, list):
            # pulling the functional component object
            # by the name (hence the split) from the obj_cit
            fcobj = self.obj_dict[self.cell_val[0].split("/")[-1]]['object']
        else:
            # pulling the functional component object
            # by the name (hence the split) from the obj_cit
            fcobj = self.obj_dict[self.cell_val.split("/")[-1]]['object']

        # print(self.obj, fcobj)
        self.obj.functionalComponents.add(fcobj.copy())

    def subcomponents(self):
        # if type is compdef do one thing, if combdev do another, else error
        if isinstance(self.obj, sbol2.componentdefinition.ComponentDefinition):
            self.obj.assemblePrimaryStructure(self.cell_val)
            self.obj.compile(assembly_method=None)

        elif isinstance(self.obj, sbol2.combinatorialderivation.CombinatorialDerivation):
            comp_list = self.cell_val
            comp_ind = 0
            variant_comps = {}
            for ind, comp in enumerate(comp_list):
                if "," in comp:
                    comp_list[ind] = f'{self.obj.displayId}_subcomponent_{comp_ind}'
                    uri = f'{self.obj.displayId}_subcomponent_{comp_ind}'
                    sub_comp = sbol2.ComponentDefinition(uri)
                    sub_comp.displayId = f'{self.obj.displayId}_subcomponent_{comp_ind}'
                    self.doc.add(sub_comp)
                    variant_comps[f'subcomponent_{comp_ind}'] = {'object': sub_comp, 'variant_list': comp}
                    comp_ind += 1

            template = sbol2.ComponentDefinition(f'{self.obj.displayId}_template')
            template.displayId = f'{self.obj.displayId}_template'
            self.doc.add(template)

            template.assemblePrimaryStructure(comp_list)
            template.compile(assembly_method=None)

            self.obj.masterTemplate = template
            for var in variant_comps:
                var_comp = sbol2.VariableComponent(f'var_{var}')
                var_comp.displayId = f'var_{var}'
                var_comp.variable = variant_comps[var]['object']

                var_list = re.split(",", variant_comps[var]['variant_list'])
                var_list = [f'{sbol2.getHomespace()}{x.strip()}' for x in var_list]
                var_comp.variants = var_list
                self.obj.variableComponents.add(var_comp)

        else:
            raise KeyError(f'The object type "{type(self.obj)}" does not allow subcomponents. (sheet:{self.sheet}, row:{self.sht_row}, col:{self.sht_col})')

    def dataSource(self):
        self.obj.wasDerivedFrom = self.cell_val
        if "pubmed.ncbi.nlm.nih.gov/" in self.cell_val:
            if 'obo' not in self.doc_pref_terms:
                self.doc.addNamespace('http://purl.obolibrary.org/obo/', 'obo')
                self.doc_pref_terms.append('obo')

            self.obj.OBI_0001617 = sbol2.TextProperty(self.obj,
                                                            'http://purl.obolibrary.org/obo/OBI_0001617',
                                                            0, 1, [])
            self.obj.OBI_0001617 = self.cell_val.split(".gov/")[1].replace("/", "")

    def sequence(self):
        # might need to be careful if the object type is sequence!
        if re.fullmatch(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.cell_val):
            # if a url
            self.obj.sequences = self.cell_val

        elif re.match(r'^[a-zA-Z \s*]+$', self.cell_val):
            # if a sequence string

            # removes spaces, enters, and makes all lower case
            self.cell_val = "".join(self.cell_val.split())
            self.cell_val = self.cell_val.replace(u"\ufeff", "").lower()

            # create sequence object
            sequence = sbol2.Sequence(f"{self.obj.displayId}_sequence",
                                      self.cell_val, sbol2.SBOL_ENCODING_IUPAC)
            if self.obj.name is not None:
                sequence.name = f"{self.obj.name} Sequence"

            self.doc.addSequence(sequence)

            # link sequence object to component definition
            self.obj.sequences = sequence

        else:
            self.obj.sequences = self.cell_val
            logging.warning(f'The cell value for {self.obj.identity} is not an accepted sequence type but it has been left for post processing. Sequence value provided: {self.cell_val} (sheet:{self.sheet}, row:{self.sht_row}, col:{self.sht_col})')
            # raise ValueError(f'The cell value for {self.obj.identity} is not an accepted sequence type, please use a sequence string or uri instead. Sequence value provided: {self.cell_val} (sheet:{self.sheet}, row:{self.sht_row}, col:{self.sht_col})')

class sbol_methods3:
    """A class used to implement a switch method based on an sbol_term. This
    is where the processing of column values happens.
    """

    def __init__(self, namespace_url, obj, obj_uri, obj_dict, doc, cell_value,
                 col_type, parental_lookup, sheet, col, display_id):
        """Initialisation of the sbol_methods class. This ensures
        that all the values that the switch case statements might need
        are available as properties of the self object.

        Args:
            namespace_url (str): A url to use for property definition. This
                    is only used if there is no established method function
                    associated with the sbol_term and the default method needs
                    to be used.
            component (sbol componentDefinition instance): The sbol component
                    definition that the value belongs to/should be added to
            doc (sbol doc instance): The sbol doc that the component definition
                    belongs to
            cell_value (str): The value of a cell. Due to the way it is read
                    in from excel this is expected to be a string. Manipulation
                    is possible if the type is expected to be something else,
                    e.g. integer
        """
        self.cell_val = cell_value
        self.obj = obj
        self.obj_uri = obj_uri
        self.obj_dict = obj_dict
        self.namespace_url = namespace_url
        self.doc = doc
        self.doc_pref_terms = ['rdf', 'rdfs', 'xsd', 'sbol']
        self.col_type = col_type
        self.parental_lookup = parental_lookup
        self.sheet = sheet
        self.sht_col = col
        self.sht_row = display_id

    # create method for each sbol term that can be called via the column class
    def switch(self, sbol_term):
        """Switch statement that calls a different method based on the
        sbol_term. For example if the sbol_term is sbh_alteredSequence
        then the function sbh_alteredSequence() will be run. If there is
        no function with a name equal to the sbol_term then the add_new method
        is run.

        Args:
            sbol_term (str): String indicating the method of processing
                    required by the cell_value

        Returns:
            Nothing is returned but the componentDefinition and sbol doc
            are updated according to the sbol_term and cell_value
        """
        self.sbol_term_pref = sbol_term.split("_", 1)[0]
        try:
            self.sbol_term_suf = sbol_term.split("_", 1)[1]
        except IndexError:
            raise ValueError(f"The SBOL Term '{sbol_term}' (sheet name: {self.sheet}) does not appear to have an underscore")

        if self.parental_lookup:
            # switches the object being worked on
            self.obj = self.obj_dict[self.cell_val]['object']
            self.cell_val = self.obj_uri

        # if not applicable then do nothing
        if sbol_term == "Not_applicable":
            pass

        # if a special function has been defined below then do something
        elif hasattr(self,  self.sbol_term_suf):
            return getattr(self, self.sbol_term_suf)()

        # if it is an sbol term use standard pySBOL implementation
        # unless it is a top level object in which case the standard
        # implementations don't work
        elif self.sbol_term_pref == "sbol":
            if hasattr(self.obj, self.sbol_term_suf):
                # if the attribute is a list append the new value
                if isinstance(getattr(self.obj, self.sbol_term_suf), list):
                    current = getattr(self.obj, self.sbol_term_suf)
                    # if the cell_val is a list append the whole list
                    if isinstance(self.cell_val, list):
                        setattr(self.obj, self.sbol_term_suf, current + self.cell_val)
                    else:
                        setattr(self.obj, self.sbol_term_suf, current + [self.cell_val])
                elif isinstance(getattr(self.obj, self.sbol_term_suf), sbol3.refobj_property.ReferencedObjectList):
                    getattr(getattr(self.obj, self.sbol_term_suf), 'append')(self.cell_val)
                else:
                    # no iteration over list as else suggests that the property
                    # can't have multiple values
                    setattr(self.obj, self.sbol_term_suf, self.cell_val)
            else:
                raise ValueError(f'This SBOL object ({type(self.obj)}) has no attribute {self.sbol_term_suf} (sheet:{self.sheet}, row:{self.sht_row}, col:{self.sht_col})')

        else:
            # logging.warning(f'This sbol term ({self.sbol_term}) has not yet been implemented so it has been added via the default method')
            # define a new namespace if needed
            if self.sbol_term_pref not in self.doc_pref_terms:
                self.doc.addNamespace(self.namespace_url, self.sbol_term_pref)
                self.doc_pref_terms.append(self.sbol_term_pref)

            # if type is uri make it a uri property
            if self.col_type == "URI":
                # * allows multiple instance of this property
                if not hasattr(self.obj, self.sbol_term_suf):
                    setattr(self.obj, self.sbol_term_suf,
                            sbol3.URIProperty(self.obj,
                                              f'{self.namespace_url}{self.sbol_term_suf}',
                                              '0', '*', initial_value=[self.cell_val]))
                else:
                    if not isinstance(self.cell_val, list):
                        self.cell_val = [self.cell_val]
                    current = getattr(self.obj, self.sbol_term_suf)
                    setattr(self.obj, self.sbol_term_suf, list(current) + self.cell_val)

            # otherwise implement as text property
            else:
                # * allows multiple instance of this property
                if not hasattr(self.obj, self.sbol_term_suf):
                    setattr(self.obj, self.sbol_term_suf,
                            sbol3.TextProperty(self.obj,
                                               f'{self.namespace_url}{self.sbol_term_suf}',
                                               '0', '*', initial_value=str(self.cell_val)))
                else:
                    if not isinstance(self.cell_val, list):
                        self.cell_val = [self.cell_val]
                    current = getattr(self.obj, self.sbol_term_suf)
                    setattr(self.obj, self.sbol_term_suf, list(current) + self.cell_val)

    def objectType(self):
        # used to decide the object type in the converter function
        pass

    def types(self):
        # used to decide the molecule type in the converter function
        pass

    def displayId(self):
        # used to set the object display id in converter function
        pass

    def addToDescription(self):
        current = getattr(self.obj, 'description')
        if isinstance(current, type(None)):
            current = ""
        new = current + "\n" + self.sht_col + ": " + self.cell_val
        setattr(self.obj, 'description', new)

    def subcomponents(self):
        # if type is compdef do one thing, if combdev do another, else error
        if isinstance(self.obj, sbol3.component.Component):
            for sub in self.cell_val:
                sub_part = sbol3.SubComponent(f'{sbol3.get_namespace()}{sub}')
                self.obj.features.append(sub_part)
            # self.obj.assemblePrimaryStructure(self.cell_val)
            # self.obj.compile(assembly_method=None)

        elif isinstance(self.obj, sbol3.combderiv.CombinatorialDerivation):
            comp_list = self.cell_val
            comp_ind = 0
            variant_comps = {}
            for ind, comp in enumerate(comp_list):
                if "," in comp:
                    comp_list[ind] = f'{self.obj.displayId}_subcomponent_{comp_ind}'
                    uri = f'{self.obj.displayId}_subcomponent_{comp_ind}'
                    sub_comp = sbol3.Component(uri, sbol3.SBO_DNA)
                    sub_comp.displayId = f'{self.obj.displayId}_subcomponent_{comp_ind}'
                    self.doc.add(sub_comp)
                    variant_comps[f'subcomponent_{comp_ind}'] = {'object': sub_comp, 'variant_list': comp}
                    comp_ind += 1

            # # move this to the object creation section
            # template = sbol2.ComponentDefinition(f'{self.obj.displayId}_template')
            # template.displayId = f'{self.obj.displayId}_template'
            # self.doc.add(template)


            template = self.obj_dict[f'{self.obj.displayId}_template']['object']

            for sub in comp_list:
                sub_part = sbol3.SubComponent(f'{sbol3.get_namespace()}{sub}')
                template.features.append(sub_part)
            # template.assemblePrimaryStructure(comp_list)
            # template.compile(assembly_method=None)

            self.obj.masterTemplate = template
            for var in variant_comps:
                var_comp = sbol3.VariableFeature(cardinality=sbol3.SBOL_ONE,
                                                 variable=f'var_{var}')
                var_comp.displayId = f'var_{var}'
                var_comp.variable = variant_comps[var]['object']

                var_list = re.split(",", variant_comps[var]['variant_list'])
                var_list = [f'{sbol3.get_namespace()}{x.strip()}' for x in var_list]
                var_comp.variants = var_list
                self.obj.variable_features.append(var_comp)

        else:
            raise KeyError(f'The object type "{type(self.obj)}" does not allow subcomponents. (sheet:{self.sheet}, row:{self.sht_row}, col:{self.sht_col})')

    def dataSource(self):
        self.obj.wasDerivedFrom = self.cell_val
        if "pubmed.ncbi.nlm.nih.gov/" in self.cell_val:
            if 'obo' not in self.doc_pref_terms:
                self.doc.addNamespace('http://purl.obolibrary.org/obo/', 'obo')
                self.doc_pref_terms.append('obo')

            self.obj.OBI_0001617 = sbol3.TextProperty(self.obj,
                                                            'http://purl.obolibrary.org/obo/OBI_0001617',
                                                            0, 1, [])
            self.obj.OBI_0001617 = self.cell_val.split(".gov/")[1].replace("/", "")

    def sequence(self):
        # might need to be careful if the object type is sequence!
        if re.fullmatch(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.cell_val):
            # if a url
            self.obj.sequences = [self.cell_val]

        elif re.match(r'^[a-zA-Z \s*]+$', self.cell_val):
            # if a sequence string

            # removes spaces, enters, and makes all lower case
            self.cell_val = "".join(self.cell_val.split())
            self.cell_val = self.cell_val.replace(u"\ufeff", "").lower()

            # create sequence object
            sequence = sbol3.Sequence(f"{self.obj.displayId}_sequence",
                                      elements=self.cell_val)
            if self.obj.name is not None:
                sequence.name = f"{self.obj.name} Sequence"

            self.doc.add(sequence)

            # link sequence object to component definition
            self.obj.sequences = [sequence]

        else:
            logging.warning(f'The cell value for {self.obj.identity} is not an accepted sequence type, it has been added as a uri and left for post processing. Sequence value provided: {self.cell_val} (sheet:{self.sheet}, row:{self.sht_row}, col:{self.sht_col})')
            self.obj.sequences = [self.cell_val]

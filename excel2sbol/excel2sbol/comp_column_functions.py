# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencies
import re
import sbol2
import pandas as pd
import excel2sbol.helper_functions as hf

class sbol_methods:
    """A class used to implement a switch method based on an sbol_term. This
    is where the processing of column values happens.
    """

    def __init__(self, namespace_url, obj, doc, cell_value, split_on,
                 col_type, pattern, object_type):
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
        self.object_type = object_type
        self.namespace_url = namespace_url
        self.doc = doc
        self.doc_pref_terms = ['rdf', 'rdfs', 'xsd', 'sbol']
        self.split_on = split_on
        self.col_type = col_type
        self.pattern = pattern

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
        self.sbol_term_suf = sbol_term.split("_", 1)[1]

        # if not applicable then do nothing
        if sbol_term == "Not_applicable":
            pass

        # if a special function has been defined below then do something
        elif hasattr(self,  self.sbol_term_suf):
            return getattr(self, self.sbol_term_suf)()

        # if it is an sbol term use standard pySBOL implementation
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
                    setattr(self.obj, self.sbol_term_suf, self.cell_val)
            else:
                raise ValueError(f'This SBOL object ({self.object_type}) has no attribute {self.sbol_term_suf}')

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
                    current = current = getattr(self.obj, self.sbol_term_suf)
                    setattr(self.obj, self.sbol_term_suf, current + self.cell_val)

            # otherwise implement as text property
            else:
                # print(self.sbol_term_suf, self.sbol_term_pref, self.namespace_url, self.cell_val)
                # * allows multiple instance of this property
                if not hasattr(self.obj, self.sbol_term_suf):
                    setattr(self.obj, self.sbol_term_suf,
                            sbol2.TextProperty(self.obj,
                                               f'{self.namespace_url}{self.sbol_term_suf}',
                                               '0', '*'))
                    setattr(self.obj, self.sbol_term_suf, self.cell_val)
                else:
                    if not isinstance(self.cell_val, list):
                        self.cell_val = [self.cell_val]
                    current = current = getattr(self.obj, self.sbol_term_suf)
                    setattr(self.obj, self.sbol_term_suf, current + self.cell_val)

    def objectType(self):
        # used to decide the object type in the converter function
        pass

    def displayId(self):
        # used to set the object display id in converter function
        pass

    def subcomponents(self):
        for sub in self.cell_val:
            print(self.doc)
            if sub not in self.doc.componentDefinitions:
                print("sub", sub)
                cd = sbol2.ComponentDefinition(sub) # HOW DO I GET THIS TO NOT GIVE EXAMPLES.ORG/HTTPS/IGEMSTUFF
                cd_seq = sbol2.Sequence(f'{sub}_seq')
                cd_seq.elements = "aaaaaaaaaaaaaa" # NEEEEEEEEEEEEEEEEEEEEEEEEEDS EDITTING!!!!!!!!!!!!!!!!
                cd.sequence = cd_seq
                self.doc.add(cd)
        # print(self.cell_val)
        self.obj.assemblePrimaryStructure(self.cell_val)
        self.obj.compile(assembly_method=None)
        # obj.sequence

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
            raise ValueError(f'The cell value for {self.obj.identity} is not an accepted sequence type, please use a sequence string or uri instead. Sequence value provided: {self.cell_val}')

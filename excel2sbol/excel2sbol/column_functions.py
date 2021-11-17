# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencies
import re
import sbol2
import pandas as pd
import excel2sbol.helper_functions as hf


class column:
    """A class used solely to create a column object, potentially with
    a look up dictionary.
    """
    def __init__(self, file_path_in, column_dict_entry):
        """This takes in a dictionary and creates a column object as that is
        easier to handle for other functions. A lookup dictionary is created
        if needed.

        Args:
            file_path_in (str): The full path to the spreadsheet with ontologies
                                to b used in lookup dictionaries
                                The string is only used if
                                column_dict_entry['Sheet Lookup'] is true.
                                E.g. c:/users/user/test.xlsx
            column_dict_entry (dict): the dictionary containing all the
                                    information about the column. It should
                                    have the form:
                                    {'SBOL Term': 'sbol_term',
                                    'Namespace URL': 'nm_url',
                                    'Sheet Lookup': 'TRUE',
                                    'Replacement Lookup': 'TRUE',
                                    'Sheet Name': 'Replacement',
                                    'From Col': 'A', 'To Col': 'B'}
        """
        self.sbol_term = column_dict_entry['SBOL Term']
        self.namespace_url = column_dict_entry['Namespace URL']
        self.lookup = column_dict_entry['Sheet Lookup']
        self.replacement_lookup = column_dict_entry['Replacement Lookup']
        self.tyto_lookup = column_dict_entry['Tyto Lookup']
        self.onto_name = column_dict_entry['Ontology Name']
        self.pattern = column_dict_entry['Pattern']
        self.split_on = column_dict_entry['Split On']
        self.col_type = column_dict_entry['Type']

        self.lookup = hf.truthy_strings(self.lookup)
        self.replacement_lookup = hf.truthy_strings(self.replacement_lookup)

        if self.lookup:
            # create a lookup dictionary from human readable to actual values
            self.sheet_name = column_dict_entry['Sheet Name']

            if type(column_dict_entry['From Col']) == str:
                # if string convert column from name to 0-indexed
                self.col_from = hf.col_to_num(column_dict_entry['From Col'])
            elif type(column_dict_entry['From Col']) == int:
                # if integer remove one to make it zero indexed
                self.col_from = int(column_dict_entry['From Col']) - 1

            if str(column_dict_entry['To Col']).isdigit():
                # if integer remove one to make it zero indexed
                self.col_to = int(column_dict_entry['To Col']) - 1
            elif type(column_dict_entry['To Col']) == str:
                # if string convert column from name to 0-indexed
                self.col_to = hf.col_to_num(column_dict_entry['To Col'])

            if self.col_from > self.col_to:
                # if col_from is bigger ind_col is 1 as the index column
                # will appear after the value column
                ind_col = 1
            else:
                ind_col = 0

            # read in lookup dictionary
            self.lookup_dict = pd.read_excel(file_path_in,
                                             sheet_name=self.sheet_name,
                                             header=0, usecols=[self.col_from,
                                                                self.col_to], engine='openpyxl')
            # remove any rows that only contain blanks
            temp_dict = self.lookup_dict.dropna(axis='rows', how='all')

            if len(self.lookup_dict) > len(temp_dict):
                # This is done in case the table doesn't start at the top
                # of the sheet but after a few rows.
                # if blanks were removed reset the index and rename the columns
                # based on the first row, then remove the first row, set the
                # index equal to the ind_col and turn it into a dictionary
                temp_dict.reset_index(drop=True, inplace=True)
                temp_dict.columns = temp_dict.iloc[0]
                temp_dict = temp_dict.drop([0])
                temp_dict.set_index(temp_dict.columns[ind_col], inplace=True)
                self.lookup_dict = temp_dict.to_dict('index')
            else:
                # if there were no blank top rows simply set the index equal
                # to the first column and drop the rest
                self.lookup_dict.set_index(self.lookup_dict.columns[ind_col],
                                           inplace=True)
                self.lookup_dict = self.lookup_dict.to_dict('index')


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

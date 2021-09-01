# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencie
import logging
import sbol2
import pandas as pd
import re
import validators
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
                                                                self.col_to])
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

    def __init__(self, namespace_url, component, doc, cell_value):
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
        self.component = component
        self.namespace_url = namespace_url
        self.doc = doc

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
        self.sbol_term = sbol_term
        # Try redoing this with suggested form
        try:  # try looking for a specified function
            return getattr(self, sbol_term)()
        except AttributeError:  # use the default add function
            return getattr(self, 'add_new')()

    def Not_applicable(self):
        """This is a method called to indicate nothing should happen
        """
        pass

    def add_new(self):
        """This method is used as the else case for the switch statement
        It splits the sbol_term e.g. sbh_designNotes into a prefix and suffix,
        checks if the prefix is already defined, if not it defines the prefix
        using the namespace url. Then the cell value is added as an object of
        the namespace url. E.g. sbh:designNotes:cell_value where sbh=name_space
        """
        logging.warning(f'This sbol term ({self.sbol_term}) has not yet been implemented so it has been added via the default method')
        self.sbol_term_prefix = self.sbol_term.split("_", 1)[0]
        self.sbol_term_sfx = self.sbol_term.split("_", 1)[1]
        if self.sbol_term_prefix not in {'rdf', 'rdfs', 'xsd', 'sbol'}:
            self.doc.addNamespace(self.namespace_url, self.sbol_term_prefix)
        setattr(self.component, self.sbol_term_sfx,
                sbol2.TextProperty(self.component,
                                   f'{self.namespace_url}{self.sbol_term_sfx}',
                                   0, 1))
        setattr(self.component, self.sbol_term_sfx, str(self.cell_val))

    def sbh_alteredSequence(self):
        """This is used to refer to how a sequence has been altered between
        the source and input into the spreadsheet. It is implemented by the
        wasGeneratedBy property. The cell_values should be a set of urls
        pointing to predefined github actions like
        https://synbiohub.org/public/Excel2SBOL/codon_optimisation/1

        Raises:
            TypeError: If the cell_value is not a string
            ValueError: If the cell_value is not a url with synbiohub.org
                    in it.
        """
        if not isinstance(self.cell_val, str):
            raise TypeError(f'Unexpected type: {type(self.cell_val)}, of cell: {self.cell_val}')
        elif not validators.url(self.cell_val):
            raise ValueError
        elif "synbiohub.org" not in self.cell_val:
            raise ValueError
        else:
            self.component.wasGeneratedBy = self.cell_val

    def sbh_dataSource(self):
        """This is used to point to the data source where the data was pulled
        from using the wasDerivedFrom property. If it is a pubmed source then
        the obo term is also used as an indicator of the source.

        Raises:
            TypeError: If the cell_value is not a string
            ValueError: If the value is not a url
        """
        if type(self.cell_val) != str:
            raise TypeError(f'Unexpected type: {type(self.cell_val)}, of cell: {self.cell_val}')
        elif not validators.url(self.cell_val):
            raise ValueError
        else:
            if self.cell_val[-1] == '/':
                self.cell_val = self.cell_val[:-1]
            self.component.wasDerivedFrom = self.cell_val
            if "pubmed.ncbi.nlm.nih.gov/" in self.cell_val:
                self.doc.addNamespace('http://purl.obolibrary.org/obo/', 'obo')
                self.component.OBI_0001617 = sbol2.TextProperty(self.component,
                                                                'http://purl.obolibrary.org/obo/OBI_0001617',
                                                                0, 1, [])
                self.component.OBI_0001617 = self.cell_val.split(".gov/")[1].replace("/", "")

    def sbh_sourceOrganism(self):
        """Used to indicate the source organism. What organism was the part
        taken from? This is implemented using a new property added to the sbh
        name space. It is implemented using the ncbi:taxonomy resource.
        The cell_value should be a number indicating the ncbi:taxonomy

        Raises:
            TypeError: If not a string or integer, or if it is a boolean
            ValueError: If it is not a string that can be converted to an
                    integer or an integer
        """
        # this together with target organism could be implemented in a better
        # and more general way, possibly a general uri version
        if not isinstance(self.cell_val, (str, int, float)):
            raise TypeError(f'Unexpected type: {type(self.cell_val)}, of cell: {self.cell_val}')
        elif type(self.cell_val) == str and not self.cell_val.isdigit():
            raise ValueError(f'Unexpected value of cell: {self.cell_val}')
        elif type(self.cell_val) == bool:
            raise TypeError(f'Unexpected type: {type(self.cell_val)}, of cell: {self.cell_val}')
        else:
            if isinstance(self.cell_val, float):
                self.cell_val = int(self.cell_val)
            self.doc.addNamespace('https://wiki.synbiohub.org/wiki/Terms/synbiohub#', 'sbh')
            self.component.sourceOrganism = sbol2.URIProperty(self.component, 'https://wiki.synbiohub.org/wiki/Terms/synbiohub#sourceOrganism', 0, 1, [])
            self.component.sourceOrganism = f'https://identifiers.org/taxonomy:{self.cell_val}'

    def sbh_targetOrganism(self):
        """Used to indicate the target organism. What organism was the part
        designed for? This is implemented using a new property added to the sbh
        name space. It is implemented using the ncbi:taxonomy resource.
        The cell_value should be a number indicating the ncbi:taxonomy

        Raises:
            TypeError: If not a string or integer, or if it is a boolean
            ValueError: If it is not a string that can be converted to an
                    integer or an integer
        """
        if not isinstance(self.cell_val, (str, int, float)):
            raise TypeError(f'Unexpected type: {type(self.cell_val)}, of cell: {self.cell_val}')
        elif type(self.cell_val) == str and not self.cell_val.isdigit():
            raise ValueError(f'Unexpected value of cell: {self.cell_val}')
        elif type(self.cell_val) == bool:
            raise TypeError(f'Unexpected type: {type(self.cell_val)}, of cell: {self.cell_val}')
        else:
            if isinstance(self.cell_val, float):
                self.cell_val = int(self.cell_val)
            self.doc.addNamespace('https://wiki.synbiohub.org/wiki/Terms/synbiohub#', 'sbh')
            self.component.targetOrganism = sbol2.URIProperty(self.component, 'https://wiki.synbiohub.org/wiki/Terms/synbiohub#targetOrganism', 0, 1, [])
            self.component.targetOrganism = f'https://identifiers.org/taxonomy:{self.cell_val}'

    def sbol_role(self):
        """Used to process roles. It uses the built in functionality of sbol
        roles. It can add a role to the end of a list or create a new roles
        object.

        Raises:
            TypeError: If cell_value is not a string
            ValueError: If cell_value doesn't seem to be an
                'identifiers.org/so/SO:' term
        """
        if not isinstance(self.cell_val, str):
            raise TypeError
        elif not re.match(r"http:\/\/identifiers.org/so/SO:[0-9]{7}",
                          self.cell_val):
            raise ValueError

        # new object created if it doesn't exist yet, otherwise append
        # the role to the enbd of the existing roles object
        if len(self.component.roles) == 0:
            self.component.roles = self.cell_val
        else:
            self.component.roles = self.component.roles + [self.cell_val]

    def sbol_roleCircular(self):
        """If the value is True then add the circular role to the
        componentDefinition roles

        Raises:
            TypeError: Raised if cell_value is not a form of True, False
                (including 1, 0 and string versions)
        """
        bool_ls = ['true', 'false', '1', '0']

        # convert cell_value to boolean if it can be converted, otherwise
        # raise a type error
        if isinstance(self.cell_val, str) and self.cell_val.lower() in bool_ls:
            if self.cell_val.lower() in ['true', '1']:
                self.cell_val = True
            else:
                self.cell_val = False
        elif isinstance(self.cell_val, int) and self.cell_val in [1, 0]:
            if self.cell_val == 1:
                self.cell_val = True
            else:
                self.cell_val = False
        elif not isinstance(self.cell_val, (bool)):
            raise TypeError

        # add the circular role to the end of the roles object, or create
        # a new roles object based on if the roles object exists or not
        if len(self.component.roles) == 0 and self.cell_val:
            self.component.roles = sbol2.SO_CIRCULAR
        elif self.cell_val:
            self.component.roles = self.component.roles + [sbol2.SO_CIRCULAR]

    def sbol_displayId(self):
        """Sets the human readable name to cell_value and the displayId
        to the alphanumeric version of the cell_value
        """
        self.component.name = self.cell_val
        self.component.displayId = hf.check_name(self.cell_val)

    def dcterms_description(self):
        """Takes the cell_value and adds it as a description to the
            component definition object

        Raises:
            TypeError: Raised if the cell_value is not a string, or a string
                that is only a number
        """
        if not isinstance(self.cell_val, str):
            raise TypeError
        elif self.cell_val.isdigit():
            raise TypeError

        self.component.description = str(self.cell_val)

    def sbol_sequence(self):
        """Used to add a sequence to the componentdefinition and create
        a sequence object to which the componentdefinition points. The
        sequence is only output as lowercase

        Raises:
            TypeError: Raised if the cell_value is not a string or contains
                    characters other than a-z (lower or upper) and spaces
            TypeError: [description]
        """
        if not isinstance(self.cell_val, str):
            raise TypeError
        elif not bool(re.match('^[a-zA-Z ]+$', self.cell_val)):
            raise TypeError

        # removes spaces, enters, and makes all lower case
        self.cell_val = "".join(self.cell_val.split())
        self.cell_val = self.cell_val.replace(u"\ufeff", "").lower()

        # create sequence object
        sequence = sbol2.Sequence(f"{self.component.displayId}_sequence",
                                  self.cell_val, sbol2.SBOL_ENCODING_IUPAC)
        sequence.name = f"{self.component.name} Sequence"
        self.doc.addSequence(sequence)

        # link sequence object to component definition
        self.component.sequences = sequence

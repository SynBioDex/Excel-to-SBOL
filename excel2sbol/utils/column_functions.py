import logging
import sbol2
import pandas as pd
import re
import validators
import utils.helper_functions as hf


class column:
    def __init__(self, file_path_in, column_dict_entry):
        """[summary]

        Args:
            file_path_in ([type]): [description]
            column_dict_entry ([type]): [description]
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
                self.col_from = hf.col_to_num(column_dict_entry['From Col'])
            elif type(column_dict_entry['From Col']) == int:
                self.col_from = int(column_dict_entry['From Col']) - 1

            if str(column_dict_entry['To Col']).isdigit():
                self.col_to = int(column_dict_entry['To Col']) - 1
            elif type(column_dict_entry['To Col']) == str:
                self.col_to = hf.col_to_num(column_dict_entry['To Col'])

            if self.col_from > self.col_to:
                ind_col = 1
            else:
                ind_col = 0

            self.lookup_dict = pd.read_excel(file_path_in,
                                             sheet_name=self.sheet_name,
                                             header=0, usecols=[self.col_from,
                                                                self.col_to])
            temp_dict = self.lookup_dict.dropna(axis='rows', how='all')
            if len(self.lookup_dict) > len(temp_dict):
                temp_dict.reset_index(drop=True, inplace=True)
                temp_dict.columns = temp_dict.iloc[0]
                temp_dict = temp_dict.drop([0])
                temp_dict.set_index(temp_dict.columns[ind_col], inplace=True)
                self.lookup_dict = temp_dict.to_dict('index')
            else:
                self.lookup_dict.set_index(self.lookup_dict.columns[ind_col],
                                           inplace=True)
                self.lookup_dict = self.lookup_dict.to_dict('index')


class sbol_methods:

    def __init__(self, namespace_url, component, doc, cell_value):
        self.cell_val = cell_value
        self.component = component
        self.namespace_url = namespace_url
        self.doc = doc

    # create method for each sbol term that can be called via the column class
    def switch(self, sbol_term):
        """[summary]

        Args:
            sbol_term ([type]): [description]
            namespace_url ([type]): [description]
            component ([type]): [description]
            doc ([type]): [description]
            cell_value ([type]): [description]

        Returns:
            [type]: [description]
        """
        self.sbol_term = sbol_term
        # Try redoing this with suggested form
        try:  # try looking for a specified function
            return getattr(self, sbol_term)()
        except AttributeError:  # use the default add function
            return getattr(self, 'add_new')()

    def Not_applicable(self):
        """[summary]
        """
        pass

    def add_new(self):
        """[summary]
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
        """[summary]
        """
        # currently uris don't go out to actual activities.
        # Fix uri to make this properly work
        if not isinstance(self.cell_val, str):
            raise TypeError
        elif not validators.url(self.cell_val):
            raise ValueError
        elif "synbiohub.org" not in self.cell_val:
            raise ValueError
        else:
            self.component.wasGeneratedBy = self.cell_val

    def sbh_dataSource(self):
        """[summary]
        """
        if type(self.cell_val) != str:
            raise TypeError
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
        """[summary]
        """
        # this together with target organism could be implemented in a better
        # and more general way, possibly a general uri version
        if not isinstance(self.cell_val, (str, int)):
            raise TypeError
        elif type(self.cell_val) == str and not self.cell_val.isdigit():
            raise ValueError
        elif type(self.cell_val) == bool:
            raise TypeError
        else:
            self.doc.addNamespace('https://wiki.synbiohub.org/wiki/Terms/synbiohub#', 'sbh')
            self.component.sourceOrganism = sbol2.URIProperty(self.component, 'https://wiki.synbiohub.org/wiki/Terms/synbiohub#sourceOrganism', 0, 1, [])
            self.component.sourceOrganism = f'https://identifiers.org/taxonomy:{self.cell_val}'

    def sbh_targetOrganism(self):
        """[summary]
        """
        if not isinstance(self.cell_val, (str, int)):
            raise TypeError
        elif type(self.cell_val) == str and not self.cell_val.isdigit():
            raise ValueError
        elif type(self.cell_val) == bool:
            raise TypeError
        else:
            self.doc.addNamespace('https://wiki.synbiohub.org/wiki/Terms/synbiohub#', 'sbh')
            self.component.targetOrganism = sbol2.URIProperty(self.component, 'https://wiki.synbiohub.org/wiki/Terms/synbiohub#targetOrganism', 0, 1, [])
            self.component.targetOrganism = f'https://identifiers.org/taxonomy:{self.cell_val}'

    def sbol_role(self):
        """[summary]
        """
        if not isinstance(self.cell_val, str):
            raise TypeError
        elif not re.match(r"http:\/\/identifiers.org/so/SO:[0-9]{7}",
                          self.cell_val):
            raise ValueError
        if len(self.component.roles) == 0:
            self.component.roles = self.cell_val
        else:
            self.component.roles = self.component.roles + [self.cell_val]

    def sbol_roleCircular(self):
        """[summary]
        """
        bool_ls = ['true', 'false', '1', '0']
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

        if len(self.component.roles) == 0 and self.cell_val:
            self.component.roles = sbol2.SO_CIRCULAR
        elif self.cell_val:
            self.component.roles = self.component.roles + [sbol2.SO_CIRCULAR]

    def sbol_displayId(self):
        """[summary]
        """
        self.component.name = self.cell_val
        self.component.displayId = hf.check_name(self.cell_val)

    def dcterms_description(self):
        """[summary]
        """
        if not isinstance(self.cell_val, str):
            raise TypeError
        elif self.cell_val.isdigit():
            raise TypeError

        self.component.description = str(self.cell_val)

    def sbol_sequence(self):
        """[summary]
        """
        if not isinstance(self.cell_val, str):
            raise TypeError
        elif not bool(re.match('^[a-zA-Z ]+$', self.cell_val)):
            raise TypeError

        # removes spaces, enters, and makes all lower case
        self.cell_val = "".join(self.cell_val.split())
        self.cell_val = self.cell_val.replace(u"\ufeff", "").lower()

        sequence = sbol2.Sequence(f"{self.component.displayId}_sequence",
                                  self.cell_val, sbol2.SBOL_ENCODING_IUPAC)
        sequence.name = f"{self.component.name} Sequence"
        self.doc.addSequence(sequence)
        self.component.sequences = sequence

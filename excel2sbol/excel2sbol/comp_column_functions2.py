# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencies
import sbol3
import sbol2
from inspect import getmembers, isfunction
import excel_sbol_utils.library3 as exutil3
import excel_sbol_utils.library2 as exutil2


class rowobj():

    def __init__(self, obj, obj_uri, obj_dict, doc, col_cell_dict,
                 sheet, display_id, term_coldef_df,  doc_pref_terms, data_source_id_to_update):
        self.obj = obj
        self.obj_uri = obj_uri
        self.obj_dict = obj_dict
        self.doc = doc
        self.sheet = sheet
        self.col_cell_dict = col_cell_dict
        self.sht_row = display_id
        self.term_coldef_df = term_coldef_df
        self.doc_pref_terms = doc_pref_terms
        self.data_source_id_to_update = data_source_id_to_update


class switch1():
    func_list2 = func_list = [o[0] for o in getmembers(exutil2) if isfunction(o[1])]
    func_list3 = func_list = [o[0] for o in getmembers(exutil3) if isfunction(o[1])]

    def switch(self, rowobj, sbol_term, sbol_version):
        if sbol_version == 2:
            self.func_list = self.func_list2
            exutil = exutil2
        elif sbol_version == 3:
            self.func_list = self.func_list3
            exutil = exutil3
        else:
            raise ValueError(f"SBOL Version ({sbol_version}) given to switch has not been implemented yet")

        # split sbol term into prefix and suffix
        self.sbol_term = sbol_term
        self.sbol_term_pref = sbol_term.split("_", 1)[0]
        try:
            self.sbol_term_suf = sbol_term.split("_", 1)[1]
        except IndexError:
            raise ValueError(f"The SBOL Term '{sbol_term}' (sheet name: {self.sheet}) does not appear to have an underscore")

        # if not applicable then do nothing
        if sbol_term == "Not_applicable":
            pass

        # if a special function has been defined in excel-sbol-utils then use that
        elif self.sbol_term_suf in self.func_list:
            return getattr(exutil, self.sbol_term_suf)(rowobj)

        # if it is an sbol term use standard pySBOL implementation
        # unless it is a top level object in which case the standard
        # implementations don't work
        elif self.sbol_term_pref == "sbol":

            for col in rowobj.col_cell_dict:

                cell_val = rowobj.col_cell_dict[col]

                parental_lookup = rowobj.term_coldef_df[rowobj.term_coldef_df['Column Name'] == col]['Parent Lookup']
                if parental_lookup.values[0]:
                    # switches the object being worked on
                    rowobj.obj = rowobj.obj_dict[cell_val]['object']
                    cell_val = rowobj.obj_uri

                if hasattr(rowobj.obj, self.sbol_term_suf):
                    # if the attribute is a list append the new value
                    if isinstance(getattr(rowobj.obj, self.sbol_term_suf), list):
                        current = getattr(rowobj.obj, self.sbol_term_suf)
                        # if the col_cell_dict has multiple columns append each

                        # if cell_val is a dict then mcol must have been given
                        if isinstance(cell_val, dict):
                            raise TypeError(f"A multicolumn value was unexpectedly given for sheet:{rowobj.sheet}, row:{rowobj.sht_row}, sbol term :{self.sbol_term}, sbol term dict: {rowobj.col_cell_dict}")
                        # if the cell_val is a list append the whole list
                        elif isinstance(cell_val, list):
                            setattr(rowobj.obj, self.sbol_term_suf, current + cell_val)
                        # otherwise append as a list object
                        else:
                            setattr(rowobj.obj, self.sbol_term_suf, current + [cell_val])

                    # if type sbol list then add by special append
                    # rather than regular list append
                    elif isinstance(getattr(rowobj.obj, self.sbol_term_suf), sbol3.refobj_property.ReferencedObjectList):

                        # if cell_val is a dict then mcol must have been given
                        if isinstance(cell_val, dict):
                            raise TypeError(f"A multicolumn value was unexpectedly given for sheet:{rowobj.sheet}, row:{rowobj.sht_row}, sbol term :{self.sbol_term}, sbol term dict: {rowobj.col_cell_dict}")
                        # else should be fine to append
                        else:
                            getattr(getattr(rowobj.obj, self.sbol_term_suf), 'append')(cell_val)

                    else:

                        # no iteration over list as else suggests that the property
                        # can't have multiple values

                        setattr(rowobj.obj, self.sbol_term_suf, cell_val)
                else:
                    raise ValueError(f'This SBOL object ({type(rowobj.obj)}) has no attribute {self.sbol_term_suf} (sheet:{rowobj.sheet}, row:{rowobj.sht_row}, sbol term dict:{rowobj.col_cell_dict})')

        else:
            # logging.warning(f'This sbol term ({self.sbol_term}) has not yet been implemented so it has been added via the default method')
            # define a new namespace if needed
            for col in rowobj.col_cell_dict:
                cell_val = rowobj.col_cell_dict[col]
                col_coldef_df = rowobj.term_coldef_df[rowobj.term_coldef_df['Column Name'] == col]

                if len(col_coldef_df) == 0:
                    raise TypeError(f"A multicolumn value was unexpectedly given for sheet:{rowobj.sheet}, row:{rowobj.sht_row}, sbol term :{self.sbol_term}, sbol term dict: {rowobj.col_cell_dict}")

                parental_lookup = col_coldef_df['Parent Lookup'].values[0]
                if parental_lookup:
                    # switches the object being worked on
                    rowobj.obj = rowobj.obj_dict[cell_val]['object']
                    cell_val = rowobj.obj_uri

                namespace_url = col_coldef_df['Namespace URL'].values[0]
                if self.sbol_term_pref not in rowobj.doc_pref_terms:
                    rowobj.doc.addNamespace(namespace_url, self.sbol_term_pref)
                    rowobj.doc_pref_terms.append(self.sbol_term_pref)

                col_type = col_coldef_df['Type'].values[0]
                # if type is uri make it a uri property
                if col_type == "URI":
                    # * allows multiple instance of this property
                    if not hasattr(rowobj.obj, self.sbol_term_suf):
                        if sbol_version == 2:
                            setattr(rowobj.obj, self.sbol_term_suf,
                                sbol2.URIProperty(rowobj.obj,
                                                f'{namespace_url}{self.sbol_term_suf}',
                                                '0', '*', []))
                            setattr(rowobj.obj, self.sbol_term_suf, cell_val)
                        elif sbol_version == 3:
                            setattr(rowobj.obj, self.sbol_term_suf,
                                sbol3.URIProperty(rowobj.obj,
                                                  f'{namespace_url}{self.sbol_term_suf}',
                                                  '0', '*', initial_value=[cell_val]))
                    else:
                        if not isinstance(cell_val, list):
                            cell_val = [cell_val]
                        current = getattr(rowobj.obj, self.sbol_term_suf)
                        setattr(rowobj.obj, self.sbol_term_suf, list(current) + cell_val)

                # otherwise implement as text property
                else:
                    # * allows multiple instance of this property
                    if not hasattr(rowobj.obj, self.sbol_term_suf):
                        if sbol_version == 2:
                            setattr(rowobj.obj, self.sbol_term_suf,
                                sbol2.TextProperty(rowobj.obj,
                                                f'{namespace_url}{self.sbol_term_suf}',
                                                '0', '*'))
                            setattr(rowobj.obj, self.sbol_term_suf, str(cell_val))
                        elif sbol_version == 3:
                            setattr(rowobj.obj, self.sbol_term_suf,
                                sbol3.TextProperty(rowobj.obj,
                                                   f'{namespace_url}{self.sbol_term_suf}',
                                                   '0', '*', initial_value=str(cell_val)))
                    else:
                        if not isinstance(cell_val, list):
                            cell_val = [cell_val]
                        current = getattr(rowobj.obj, self.sbol_term_suf)
                        setattr(rowobj.obj, self.sbol_term_suf, list(current) + cell_val)

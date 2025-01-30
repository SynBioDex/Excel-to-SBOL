import pandas as pd
import excel_sbol_utils.helpers as hf
import excel2sbol.lookup_compiler as lk
import excel2sbol.comp_column_functions2 as cf2
import logging
import sbol2
import sbol3
import math
import re
import os

# the homespace only works if the change is made to pysbol2 shown in https://github.com/SynBioDex/pySBOL2/pull/411/files

def initialise_welcome(file_path_in):
    init_info = pd.read_excel(file_path_in, sheet_name="Init",
                              skiprows=9, index_col=0,
                              engine='openpyxl')
    init_info = init_info.applymap(lambda x: x.strip() if isinstance(x, str) else x).to_dict('index')

    version_info = pd.read_excel(file_path_in, sheet_name="Init",
                                 nrows=4, index_col=0, header=None,
                                 engine='openpyxl')
    version_info = version_info.applymap(lambda x: x.strip() if isinstance(x, str) else x).to_dict('index')
    if 'Homespace' in version_info:
        homespace = version_info['Homespace'][1]
    else:
        homespace = ""
    version_info = version_info['SBOL Version'][1]

    # For key in dict read in sheet,
    # if sheet convert = true, add to convert list
    compiled_sheets = {}
    to_convert = []
    for sheet_name, val in init_info.items():
        # print(f"reading in {sheet_name}...")
        # MY CODE
        if sheet_name.lower() == "welcome":
            print("Processing the welcome page...")
            try:
                welcome_metadata = pd.read_excel(file_path_in, sheet_name=sheet_name,
                                                 index_col=0, engine='openpyxl').fillna("")
                print("Welcome Page Metadata:")
                
                dict = {}
                for _, row in welcome_metadata.iterrows():
                    if len(row) >= 2:
                        key, value = row[0], row[1]
                        if isinstance(key, str) and key.strip():
                            dict[key.strip()] = value.strip() if isinstance(value, str) else value
                for key, value in dict.items():
                    print(f"{key}: {value}")
                return dict
                
            except Exception as e:
                print(f"Error reading the welcome page: {e}")
                return None
            
        else:
            return
    
def initialise(file_path_in):
    init_info = pd.read_excel(file_path_in, sheet_name="Init",
                              skiprows=9, index_col=0,
                              engine='openpyxl')
    init_info = init_info.applymap(lambda x: x.strip() if isinstance(x, str) else x).to_dict('index')

    version_info = pd.read_excel(file_path_in, sheet_name="Init",
                                 nrows=4, index_col=0, header=None,
                                 engine='openpyxl')
    version_info = version_info.applymap(lambda x: x.strip() if isinstance(x, str) else x).to_dict('index')
    if 'Homespace' in version_info:
        homespace = version_info['Homespace'][1]
    else:
        homespace = ""
    version_info = version_info['SBOL Version'][1]

    # For key in dict read in sheet,
    # if sheet convert = true, add to convert list
    compiled_sheets = {}
    to_convert = []
    for sheet_name, val in init_info.items():
        # print(f"reading in {sheet_name}...")
        # MY CODE
        if sheet_name.lower() == "welcome":
            continue
		# MY CODE
        
        convert = val['Convert']

        if convert:
            to_convert.append(sheet_name.strip())

        # read in collections, description, library
        sheet_dict = {}

        if val['Has Collections']:
            x = val['Collect Cols']
            x = x.split(',')
            x = [int(i) for i in x]

            sheet_dict['collection_info'] = pd.read_excel(file_path_in, sheet_name=sheet_name,
                                                          header=None,
                                                          nrows=val['# of Collect Rows'],
                                                          usecols=x,
                                                          index_col=0,
                                                          engine='openpyxl').to_dict('index')
        else:
            sheet_dict['collection_info'] = {}

        if val['Has Descripts']:
            x = val['Descript Cols']
            if isinstance(x, (float, int)):
                x = int(x)
                x = [x]
            elif isinstance(x, str):
                x = x.split(',')
                x = [int(i) for i in x]

            sheet_dict['description'] = pd.read_excel(file_path_in,
                                                      sheet_name=sheet_name,
                                                      header=None,
                                                      skiprows=int(val['Descript Start Row']),
                                                      nrows=1,
                                                      usecols=x,
                                                      engine='openpyxl').iloc[0, 0]
        else:
            sheet_dict['description'] = ""

        skipval = val['Lib Start Row'] - 1  #to avoid zero index confusion
        lib_df = pd.read_excel(file_path_in, sheet_name=sheet_name,
                               header=0, skiprows=skipval,
                               engine='openpyxl').fillna("")
        sheet_dict['library'] = lib_df.applymap(lambda x: x.strip() if isinstance(x, str) else x).to_dict('list')

        # need dicitonary with as keys every column name and as values a list of values (note ordered list and need place holder empty values)
        compiled_sheets[sheet_name] = sheet_dict

    # read in column_dict sheet
    col_read_df = pd.read_excel(file_path_in,
                                sheet_name="column_definitions", header=0,
                                engine='openpyxl')
    col_read_df = col_read_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # processing to turn init columns into 'sheet' columns
    # pull all column names
    extra_cols = list(list(init_info.values())[0].keys())
    extra_cols = extra_cols[8:]
    for conv_sht in to_convert:
        for xcol in extra_cols:
            init_val = init_info[conv_sht][xcol]
            if isinstance(init_val, str) or not math.isnan(init_val):
                # add row to col def sheet
                new_row = col_read_df[col_read_df['Sheet Name'] == 'Init']
                new_row = new_row[new_row['Column Name'] == xcol].to_dict('records')
                new_row[0]['Sheet Name'] = conv_sht
                new_row_df = pd.DataFrame(new_row)
                # col_read_df = col_read_df.append(new_row_df)
                col_read_df = pd.concat([col_read_df, new_row_df])

                # add col to compiled_sheets
                num_rows = len(list(compiled_sheets[conv_sht]['library'].values())[0])
                val_list = [init_val for x in range(num_rows)]  # make a list of appropriate length
                compiled_sheets[conv_sht]['library'][xcol] = val_list

    # re index as otherwise causes issues later
    col_read_df = col_read_df.reset_index(drop=True)
    return(col_read_df, to_convert, compiled_sheets, version_info, homespace)


def parse_objects(col_read_df, to_convert, compiled_sheets,
                  homespace='http://examples.org/', sbol_version=2):
    """Making a list of all objects in the document"""

    # create uris for every item in to convert sheets
    # (note might want generic top level
    # if object type is not an sbol object type)

    dict_of_objs = {}
    sht_convert_dict = {}
    doc = sbol2.Document()
    sbol2.setHomespace(homespace)

    # sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
    sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)

    for sht in to_convert:
        sht_df = col_read_df.loc[col_read_df['Sheet Name'] == sht]

        try:
            dis_name_col = sht_df.loc[col_read_df['SBOL Term'] == 'sbol_displayId']['Column Name'].values[0]
        except IndexError as e:
            raise KeyError(f'The sheet "{sht}" has no column with sbol_displayId as type. Thus the following error was raised: {e}')

        try:
            obj_type_col = sht_df.loc[col_read_df['SBOL Term'] == 'sbol_objectType']['Column Name'].values[0]
        except IndexError as e:
            raise KeyError(f'The sheet "{sht}" has no column with sbol_objectType as type. Thus the following error was raised: {e}')

        sht_convert_dict[sht] = dis_name_col
        ids = compiled_sheets[sht]['library'][dis_name_col]
        types = compiled_sheets[sht]['library'][obj_type_col]

        for ind, id in enumerate(ids):
            sanitised_id = hf.check_name(id)
            uri = f'{sbol2.getHomespace()}{sanitised_id}'

            if hasattr(sbol2, types[ind]):
                varfunc = getattr(sbol2, types[ind])
                if types[ind] == "CombinatorialDerivation":
                    # print('combdev', sanitised_id, types[ind])
                    # template = sbol2.ComponentDefinition(f'{sanitised_id}_template')
                    # template.displayId = f'{sanitised_id}_template'
                    # dict_of_objs[f'{sanitised_id}_template'] = {'uri': f'{sbol2.getHomespace()}{sanitised_id}_template',
                    #                                             'object': template, 'displayId': f'{sanitised_id}_template'}
                    obj = varfunc(uri=sanitised_id)
                    # print(f'here, {sanitised_id}')
                else:
                    # print(sanitised_id, types[ind])
                    obj = varfunc(sanitised_id)
                obj.displayId = sanitised_id
                # if "Supplement" in obj.displayId:
                #     print(obj, type(obj))

            else:
                # if not a known sbol class use generic toplevel
                obj = sbol2.TopLevel(type_uri=types[ind], uri=uri, version='1')

            dict_of_objs[id] = {'uri': uri, 'object': obj,
                                'displayId': sanitised_id}

    for obj_name in dict_of_objs:
        obj = dict_of_objs[obj_name]['object']
        # print(obj_name, obj, type(obj))
        doc.add(obj)
    return(doc, dict_of_objs, sht_convert_dict)


def parse_objects3(col_read_df, to_convert, compiled_sheets,
                   homespace='http://examples.org', sbol_version=3):
    """Making a list of all objects in the document"""

    # create uris for every item in to convert sheets
    # (note might want generic top level
    # if object type is not an sbol object type)

    dict_of_objs = {}
    sht_convert_dict = {}
    doc = sbol3.Document()
    sbol3.set_namespace(homespace)

    # sbol3.ConfigOptions.SBOL_TYPED_URIS = False
    # sbol3.Config.setOption(sbol3.ConfigOptions.SBOL_TYPED_URIS = False)
    # sbol3.Config.setOption(sbol3.ConfigOptions.SBOL_TYPED_URIS, False)

    for sht in to_convert:
        sht_df = col_read_df.loc[col_read_df['Sheet Name'] == sht]

        try:
            dis_name_col = sht_df.loc[col_read_df['SBOL Term'] == 'sbol_displayId']['Column Name'].values[0]
        except IndexError as e:
            raise KeyError(f'The sheet "{sht}" has no column with sbol_displayID as type. Thus the following error was raised: {e}')

        try:
            obj_type_col = sht_df.loc[col_read_df['SBOL Term'] == 'sbol_objectType']['Column Name'].values[0]
        except IndexError as e:
            raise KeyError(f'The sheet "{sht}" has no column with sbol_objectType as type. Thus the following error was raised: {e}')

        try:
            mol_type_col = sht_df.loc[col_read_df['SBOL Term'] == 'sbol_types']['Column Name'].values[0]
            mol_types = compiled_sheets[sht]['library'][mol_type_col]
        except IndexError:
            mol_types = None

        sht_convert_dict[sht] = dis_name_col
        ids = compiled_sheets[sht]['library'][dis_name_col]
        obj_types = compiled_sheets[sht]['library'][obj_type_col]

        for ind, id in enumerate(ids):
            sanitised_id = hf.check_name(id)

            uri = f'{sbol3.get_namespace()}/{sanitised_id}'

            if hasattr(sbol3, obj_types[ind]):
                varfunc = getattr(sbol3, obj_types[ind])
                if obj_types[ind] == "Component":
                    # checks that a molecule type is given and it isn't a boolean like circular
                    if mol_types is not None and isinstance(mol_types[ind], str):
                        obj = varfunc(f'{homespace}/{sanitised_id}', mol_types[ind])
                    else:
                        obj = varfunc(sanitised_id, sbol3.SBO_DNA)
                        logging.warning(f'As no molecule type was giving the component {id} was initiated as a DNA molecule')
                elif obj_types[ind] == "CombinatorialDerivation":
                    template = sbol3.Component(f'{homespace}/{sanitised_id}_template', sbol3.SBO_DNA)
                    template.displayId = f'{sanitised_id}_template'
                    dict_of_objs[f'{sanitised_id}_template'] = {'uri': f'{homespace}/{sanitised_id}_template',
                                                                'object': template, 'displayId': f'{sanitised_id}_template'}

                    obj = varfunc(sanitised_id, template)
                    # doesnt work for comb dev at the moment!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                else:
                    obj = varfunc(f'{homespace}/{sanitised_id}')
                obj.displayId = sanitised_id

            else:
                # if not a known sbol class use generic toplevel
                obj = sbol3.TopLevel(type_uri=obj_types[ind], identity=uri)

            dict_of_objs[id] = {'uri': uri, 'object': obj,
                                'displayId': sanitised_id}

    for obj_name in dict_of_objs:
        obj = dict_of_objs[obj_name]['object']
        doc.add(obj)
    return(doc, dict_of_objs, sht_convert_dict)


class TermClass:
    def __init__(self, row):
        self.row_num = row


def column_parse(to_convert, compiled_sheets, sht_convert_dict, dict_of_objs,
                 col_read_df, doc, file_path_out, sbol_version=3, file_format=None):
    doc_pref_terms = ['rdf', 'rdfs', 'xsd', 'sbol']
    data_source_id_to_update = {}

    for sht in to_convert:
        print(sht)
        sht_lib = compiled_sheets[sht]['library']

        # pulls first column and checks the number of elements in it
        num_rows = len(sht_lib[list(sht_lib.keys())[0]])

        for row_num in range(0, num_rows):

            term_dict = TermClass(row_num)

            disp_id = sht_lib[sht_convert_dict[sht]][row_num]
            obj = dict_of_objs[disp_id]['object']
            obj_uri = dict_of_objs[disp_id]['uri']

            for col in sht_lib.keys():
                cell_val = sht_lib[col][row_num]

                if cell_val != '':
                    # checks that the cell isn't blank
                    col_convert_df = col_read_df.loc[(col_read_df['Sheet Name'] == sht) & (col_read_df['Column Name'] == col)]
                    if col_convert_df.empty:
                        raise ValueError(f"There is an issue with the column definitions sheet missing values. Sheet:'{sht}' with Column:'{col}' cannot be found. Please check for any spaces.")

                    # split method
                    split_on = col_convert_df['Split On'].values[0]
                    split_on = split_on.split('"')
                    split_on = [x for x in split_on if x != '']
                    split_on = '[' + "".join(split_on) + ']'

                    # used as string will always be '[]' at least
                    if len(split_on) > 2:
                        cell_val = re.split(split_on, cell_val)
                    if isinstance(cell_val, list):
                        cell_val = [x.strip() for x in cell_val]

                    # cell value or list of cell values based on lookups
                    if isinstance(cell_val, list):
                        for ind, val in enumerate(cell_val):
                            cell_val[ind] = lk.up(col_convert_df, val,
                                                  compiled_sheets,
                                                  dict_of_objs)
                    else:
                        cell_val = lk.up(col_convert_df, cell_val,
                                         compiled_sheets, dict_of_objs)

                    # if converted to empty cell or
                    # empty string then skip the rest
                    is_nan = False
                    if isinstance(cell_val, float):
                        is_nan = math.isnan(cell_val)
                    if cell_val == "" or is_nan:
                        continue

                    # Ensures that the cell value after possible conversion
                    # matches one of the patterns specified
                    pattern = col_convert_df['Pattern'].values[0]
                    if isinstance(pattern, str) and len(pattern) > 2:
                        pattern = pattern = pattern.split('"')
                        pattern = [x for x in pattern if x != '' and x != ' ']
                        if isinstance(cell_val, list):
                            for val in cell_val:
                                pat_truth = [re.match(pat, val) for pat in pattern]
                                pat_truth = [True for pat in pat_truth if pat is not None]
                                if len(pat_truth) < 1:
                                    raise ValueError(f'The cell value provided did not meet (any of) the pattern criteria, cell value: {val} (in sheet:{sht}, column:{col},  row:{disp_id}), pattern:{pattern}')
                        else:
                            pat_truth = [re.match(pat, cell_val) for pat in pattern]
                            pat_truth = [True for pat in pat_truth if pat is not None]
                            if len(pat_truth) < 1:
                                raise ValueError(f'The cell value provided did not meet (any of) the pattern criteria, cell value: {cell_val} (in sheet:{sht}, column:{col},  row:{disp_id}), pattern:{pattern}')

                    # carry out method of column processing based on
                    # the sbol_term of the column
                    # This creates an object with the converted cell values
                    # hierarchy: sbol term, multicolumn, column name, cell val
                    mcol = col_convert_df['Multicolumn'].values[0]
                    sbol_term = col_convert_df['SBOL Term'].values[0]

                    if hasattr(term_dict, sbol_term):
                        sbol_dict = getattr(term_dict, sbol_term)
                    else:
                        sbol_dict = {}

                    if isinstance(mcol, str):
                        if mcol not in sbol_dict:
                            sbol_dict[mcol] = {}
                        sbol_dict[mcol][col] = cell_val
                    else:
                        sbol_dict[col] = cell_val

                    setattr(term_dict, sbol_term, sbol_dict)


            # print(term_dict.__dict__)
            for term in term_dict.__dict__:
                if term != 'row_num':
                    # print(term, getattr(term_dict, term))
                    col_cell_dict = getattr(term_dict, term)
                    term_coldef_df = col_read_df[(col_read_df['SBOL Term'] == term) & (col_read_df['Sheet Name'] == sht)]
                    rj = cf2.rowobj(obj, obj_uri, dict_of_objs, doc,
                                    col_cell_dict, sht, disp_id,
                                    term_coldef_df, doc_pref_terms, data_source_id_to_update)
                    sw = cf2.switch1()
                    sw.switch(rj, term, sbol_version)
                    doc_pref_terms = rj.doc_pref_terms
                    data_source_id_to_update = rj.data_source_id_to_update
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # this makes sure all references to an object are also updated (as well as any derived terms)
    if len(data_source_id_to_update) > 0:
        doc = hf.update_uri_refs(doc, data_source_id_to_update, use_derived=True, derived_ls = ['_sequence'])

    
    if os.getenv("COUNTER") == "Error found":
        return
    elif file_format is None:
        doc.write(file_path_out)
    else:
        doc.write(file_path_out, file_format = file_format)
    
    return
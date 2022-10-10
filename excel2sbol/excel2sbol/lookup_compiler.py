import tyto
import re
import excel_sbol_utils.helpers as hf


def up(col_def_row, cell_val, compiled_sheets, obj_dict):
    col_def_dict = col_def_row.to_dict(orient='list')
    if col_def_dict['Tyto Lookup'][0] and not col_def_dict['Sheet Lookup'][0]:
        # if the ontology lookup is TRUE and sheet lookup is FALSE
        # For returning the URI, we need the following:
        # ontology_name & cell_val
        er_val = cell_val
        onto_name = col_def_dict['Ontology Name'][0]
        if onto_name == "SO":
            cell_val = re.sub("[^A-Za-z0-9]", "_", cell_val)
        cell_val = tyto.endpoint.Ontobee.get_uri_by_term(getattr(tyto, onto_name), cell_val)
        if cell_val is None:
            raise ValueError(f'The Cell value {er_val} does not appear to be in {onto_name} please check spelling, capitalisation, and for species if it is the most up to date species name')
    if col_def_dict['Sheet Lookup'][0] and not col_def_dict['Replacement Lookup'][0]:
        # pull converted cell value from lookup table
        # created by table class and column class
        # and use the lookup column to get the new cell_value

        lk_dict_name = col_def_dict['Lookup Sheet Name'][0]
        lk_dict = compiled_sheets[lk_dict_name]['library']

        lk_col_from = list(lk_dict.keys())[hf.col_to_num(col_def_dict['From Col'][0]) - 1]
        lk_col_to = list(lk_dict.keys())[hf.col_to_num(col_def_dict['To Col'][0]) - 1]

        try:
            # find the index of cell value in the from column
            # find the item with the same index in the to column
            cell_val = lk_dict[lk_col_to][lk_dict[lk_col_from].index(cell_val)]
        except ValueError:
            raise KeyError(f'cell vlaue: {cell_val} not in the lookup dictionary: {lk_dict_name}')
    elif col_def_dict['Sheet Lookup'][0]:
        # if it is a lookup and a replacement lookup
        # create a url based on the prefix
        # E.g. pubmed:1023 means use pubmed url and value 1023
        cell_val_prefix = cell_val.split(":", 1)[0]
        cell_val_suffix = cell_val.split(":", 1)[1]

        lk_dict_name = col_def_dict['Lookup Sheet Name'][0]
        lk_dict = compiled_sheets[lk_dict_name]['library']

        lk_col_from = list(lk_dict.keys())[hf.col_to_num(col_def_dict['From Col'][0]) - 1]
        lk_col_to = list(lk_dict.keys())[hf.col_to_num(col_def_dict['To Col'][0]) - 1]

        try:
            # find the index of cell value in the from column
            # find the item with the same index in the to column
            cell_val = lk_dict[lk_col_to][lk_dict[lk_col_from].index(cell_val_prefix)].replace("{REPLACE_HERE}", cell_val_suffix)
        except ValueError:
            raise KeyError(f'cell vlaue: {cell_val_prefix} not in the lookup dictionary: {lk_dict_name}')

    elif col_def_dict['Object_ID Lookup'][0] and not col_def_dict['Parent Lookup'][0]:
        # changes part name to the uri to reference (if not a parental lookup)
        # could later add an if statement to only go through conversion
        # if the cell value is not already a uri, this would allow subcomponents
        # to be referenced either by part id if built in sheet or by uri
        # if the component already exists
        try:
            cell_val = obj_dict[cell_val]['uri']
        except KeyError:
            raise KeyError(f'The object "{cell_val}" is referenced in Sheet: "{col_def_dict["Sheet Name"][0]}", Column: "{col_def_dict["Column Name"][0]}" but is never created')
    return cell_val

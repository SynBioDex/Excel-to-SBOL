import tyto
import re


def up(col_row_list, cell_val):
    if col_row_list.tyto_lookup:
        # if the ontology lookup is TRUE and sheet lookup is FALSE
        # For returning the URI, we need the following:
        # ontology_name & cell_val
        er_val = cell_val
        onto_name = col_row_list.onto_name
        if onto_name == "SO":
            cell_val = re.sub("[^A-Za-z0-9]", "_", cell_val)
        cell_val = tyto.endpoint.Ontobee.get_uri_by_term(getattr(tyto, onto_name), cell_val)
        if cell_val is None:
            raise ValueError(f'The Cell value {er_val} does not appear to be in {onto_name} please check spelling, capitalisation, and for species if it is the most up to date species name')
    if col_row_list.lookup and not col_row_list.replacement_lookup:
        # pull converted cell value from lookup table
        # created by table class and column class
        # and use the lookup column to get the new cell_value
        try:
            cell_val = list(col_row_list.lookup_dict[cell_val].values())[0]
        except KeyError:
            raise KeyError(f'cell vlaue: {cell_val} not in the lookup dictionary: {col_row_list.lookup_dict}')
    elif col_row_list.lookup:
        # if it is a lookup and a replacement lookup
        # create a url based on the prefix
        # E.g. pubmed:1023 means use pubmed url and value 1023
        cell_val_prefix = cell_val.split(":", 1)[0]
        cell_val_suffix = cell_val.split(":", 1)[1]
        cell_val = list(col_row_list.lookup_dict[cell_val_prefix].values())[0].replace("{REPLACE_HERE}", cell_val_suffix)
    return cell_val

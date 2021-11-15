# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencie
import re
import tyto
import sbol2
import excel2sbol.helper_functions as hf
import excel2sbol.column_functions as cf
import excel2sbol.initialise_functions as initf


def converter(template_name, file_path_in, file_path_out):
    """This runs a full conversion from an excel template to an sbol file.
    The sbol file is output at the file_path_out location. The conversion is
    based on parameters found in template_constants.txt, accessed based on
    the template name.

    Args:
        template_name (str): Name of the template used in the input file.
                E.g. darpa_template_blank_v006_20210405.xlsx
        file_path_in (str): The full path to the filled in excel file.
                E.g. 'C:/users/user/filled_out.xlsx'
        file_path_out (str): The full path to where the sbol file should be
                saved. E.g. 'C:/users/user/output.xml'
    """
    # read in the sheet and convert it to a dictionary
    (col_read_dict, sheet_dict, descrip_info,
     collection_info) = initf.read_in_sheet(template_name, file_path_in)
    sheet_tbl = initf.table(file_path_in, col_read_dict)

    # initialise the sbol document
    doc = sbol2.Document()
    molecule_type = sbol2.BIOPAX_DNA
    sbol2.Config.setOption('sbol_typed_uris', False)

    # Metadata
    if len(str(descrip_info)) > 0:
        doc.description = str(descrip_info)
    doc.name = list(collection_info['Collection Name'].values())[0]

    for row in sheet_dict.values():
        # set up component
        # ALTER HERE TO ALLOW DIFFERENT OBJECT TYPES
        # ALTER HERE TO ALLOW DIFFERENT OBJECT TYPES
        # ALTER HERE TO ALLOW DIFFERENT OBJECT TYPES
        # ALTER HERE TO ALLOW DIFFERENT OBJECT TYPES
        # ALTER HERE TO ALLOW DIFFERENT OBJECT TYPES
        # ALTER HERE TO ALLOW DIFFERENT OBJECT TYPES# ALTER HERE TO ALLOW DIFFERENT OBJECT TYPES### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        component = sbol2.ComponentDefinition(hf.check_name(row["Part Name"]),
                                              molecule_type)
        print(row["Part Name"])
        for col in row:
            print(col, row[col])
            if row[col] != '':
                # checks that the column isn't blank
                cell_val = row[col]

                split_on = sheet_tbl.column_list[col].split_on
                split_on = split_on.split('"')
                split_on = [x for x in split_on if x != '']
                split_on = '[' + "".join(split_on) + ']'
                if len(split_on) > 2:  # used as string will always be '[]' at least
                    cell_val = re.split(split_on, cell_val)
                    print(cell_val)
                # MOVE THIS TO A SEPERATE LOOK UP FUNCTION #################################################################################################################################################
                # SHOULD CONVERT EVERY ITEM IN LIST IF IS A LIST BASED ON SPLIT
                if sheet_tbl.column_list[col].tyto_lookup:
                    # if the ontology lookup is TRUE and sheet lookup is FALSE
                    # For returning the URI, we need the following:
                    # ontology_name & cell_val
                    er_val = cell_val
                    onto_name = sheet_tbl.column_list[col].onto_name
                    if onto_name == "SO":
                        cell_val = re.sub("[^A-Za-z0-9]", "_", cell_val)
                    cell_val = tyto.endpoint.Ontobee.get_uri_by_term(getattr(tyto, onto_name), cell_val)
                    if cell_val is None:
                        raise ValueError(f'The Cell value {er_val} does not appear to be in {onto_name} please check spelling, capitalisation, and for species if it is the most up to date species name')
                if sheet_tbl.column_list[col].lookup and not sheet_tbl.column_list[col].replacement_lookup:
                    # pull converted cell value from lookup table
                    # created by table class and column class
                    # and use the lookup column to get the new cell_value
                    try:
                        cell_val = list(sheet_tbl.column_list[col].lookup_dict[cell_val].values())[0]
                    except KeyError:
                        raise KeyError(f'cell vlaue: {cell_val} not in the lookup dictionary: {sheet_tbl.column_list[col].lookup_dict}')
                elif sheet_tbl.column_list[col].lookup:
                    # if it is a lookup and a replacement lookup
                    # create a url based on the prefix
                    # E.g. pubmed:1023 means use pubmed url and value 1023
                    cell_val_prefix = cell_val.split(":", 1)[0]
                    cell_val_suffix = cell_val.split(":", 1)[1]
                    cell_val = list(sheet_tbl.column_list[col].lookup_dict[cell_val_prefix].values())[0].replace("{REPLACE_HERE}", cell_val_suffix)
                # MOVE THIS TO A SEPERATE LOOK UP FUNCTION #################################################################################################################################################

                # Ensures that the cell value after possible conversion
                # matches one of the patterns specified
                pattern = sheet_tbl.column_list[col].pattern
                if isinstance(pattern, str):
                    pattern = pattern = pattern.split('"')
                    pattern = [x for x in pattern if x != '' and x != ' ']
                    if isinstance(cell_val, list):
                        # ADD CODE TO DEAL WITH LIST OF VARIABLES
                    else:
                        pat_truth = [re.match(pat, cell_val) for pat in pattern]
                        pat_truth = [True for pat in pat_truth if pat is not None]
                        if len(pat_truth) < 1:
                            raise ValueError(f'The cell value provided did not meet (any of) the pattern criteria, cell value: {cell_val}, pattern:{pattern}')

                # carry out method of column processing based on
                # the sbol_term of the column
                col_meth = cf.sbol_methods(sheet_tbl.column_list[col].namespace_url,
                                           component, doc, cell_val,
                                           sheet_tbl.column_list[col].split_on,
                                           sheet_tbl.column_list[col].col_type,
                                           sheet_tbl.column_list[col].pattern)
                col_meth.switch(sheet_tbl.column_list[col].sbol_term)

        doc.addComponentDefinition(component)
    doc.write(file_path_out)

# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencie
import re
import math
import sbol2
import logging
import excel2sbol.lookup as lk
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
    sbol2.Config.setOption('sbol_typed_uris', False)

    # Metadata
    if len(str(descrip_info)) > 0:
        doc.description = str(descrip_info)
    doc.name = list(collection_info['Collection Name'].values())[0]

    # find column with display id and object type
    sbol_obj_type_col = ""
    display_id_col = ""
    sbol_type_col = ""
    for col in sheet_dict[0]:
        sbol_term = sheet_tbl.column_list[col].sbol_term
        if sbol_term == 'sbol_objectType':
            sbol_obj_type_col = col
        elif sbol_term == "sbol_displayId":
            display_id_col = col
        elif sbol_term == 'sbol_type':
            sbol_type_col = col
    if len(display_id_col) == 0:
        raise IndexError('No column is provided with displayIds. Please specify a column with the sbol term sbol_displayId.')
    if len(sbol_obj_type_col) == 0:
        logging.warning("No object type column was given so all objects are being implemented as component definitions")
        sbol_obj_type = "ComponentDefinition"

    for row in sheet_dict.values():
        # set up object type
        if len(sbol_obj_type_col) != 0:
            sbol_obj_type = row[sbol_obj_type_col]

        # create sbol object based on the sbol object type
        var_func = getattr(sbol2, sbol_obj_type)
        if sbol_obj_type == "ComponentDefinition" and len(sbol_type_col) == 0:
            obj = var_func(hf.check_name(row[display_id_col]), sbol2.BIOPAX_DNA)
            logging.warning("No type column was given so all component definitions are being implemented as DNA")
        else:
            obj = var_func(hf.check_name(row[display_id_col]))

        # print(row[display_id_col])
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

                # cell value or list of cell values based on lookups
                if isinstance(cell_val, list):
                    for ind, val in enumerate(cell_val):
                        cell_val[ind] = lk.up(sheet_tbl.column_list[col], val)
                else:
                    cell_val = lk.up(sheet_tbl.column_list[col], cell_val)

                # if converted to empty cell or empty string then skip the rest
                is_nan = False
                if isinstance(cell_val, float):
                    is_nan = math.isnan(cell_val)
                if cell_val == "" or is_nan:
                    continue

                # Ensures that the cell value after possible conversion
                # matches one of the patterns specified
                pattern = sheet_tbl.column_list[col].pattern
                if isinstance(pattern, str):
                    pattern = pattern = pattern.split('"')
                    pattern = [x for x in pattern if x != '' and x != ' ']
                    if isinstance(cell_val, list):
                        for val in cell_val:
                            pat_truth = [re.match(pat, val) for pat in pattern]
                            pat_truth = [True for pat in pat_truth if pat is not None]
                            if len(pat_truth) < 1:
                                raise ValueError(f'The cell value provided did not meet (any of) the pattern criteria, cell value: {val}, pattern:{pattern}')
                    else:
                        pat_truth = [re.match(pat, cell_val) for pat in pattern]
                        pat_truth = [True for pat in pat_truth if pat is not None]
                        if len(pat_truth) < 1:
                            raise ValueError(f'The cell value provided did not meet (any of) the pattern criteria, cell value: {cell_val}, pattern:{pattern}')

                # carry out method of column processing based on
                # the sbol_term of the column
                col_meth = cf.sbol_methods(sheet_tbl.column_list[col].namespace_url,
                                           obj, doc, cell_val,
                                           sheet_tbl.column_list[col].split_on,
                                           sheet_tbl.column_list[col].col_type,
                                           sheet_tbl.column_list[col].pattern,
                                           sbol_obj_type)
                col_meth.switch(sheet_tbl.column_list[col].sbol_term)

        doc.add(obj)
    doc.write(file_path_out)

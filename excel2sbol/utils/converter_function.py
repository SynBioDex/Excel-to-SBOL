import sbol2
import utils.helper_functions as hf
import utils.column_functions as cf
import utils.initialise_functions as initf


def converter(template_name, file_path_in, file_path_out):
    """[summary]

    Args:
        template_name ([type]): [description]
        file_path_in ([type]): [description]
        file_path_out ([type]): [description]
    """
    (col_read_dict, sheet_dict, descrip_info,
     collection_info) = initf.read_in_sheet(template_name, file_path_in)
    sheet_tbl = initf.table(file_path_in, col_read_dict)
    doc = sbol2.Document()
    molecule_type = sbol2.BIOPAX_DNA
    sbol2.Config.setOption('sbol_typed_uris', False)

    # Metadata
    if len(str(descrip_info)) > 0:
        doc.description = str(descrip_info)
    doc.name = list(collection_info['Collection Name'].values())[0]

    for row in sheet_dict.values():
        # set up component
        component = sbol2.ComponentDefinition(hf.check_name(row["Part Name"]),
                                              molecule_type)

        for col in row:
            if row[col] != '':
                cell_val = row[col]
                if sheet_tbl.column_list[col].lookup and not sheet_tbl.column_list[col].replacement_lookup:
                    # pull converted cell value from lookup table
                    # created by table class and column class
                    cell_val = list(sheet_tbl.column_list[col].lookup_dict[cell_val].values())[0]
                elif sheet_tbl.column_list[col].lookup:
                    # create a url based on the prefix
                    cell_val_prefix = cell_val.split(":", 1)[0]
                    cell_val_suffix = cell_val.split(":", 1)[1]
                    cell_val = list(sheet_tbl.column_list[col].lookup_dict[cell_val_prefix].values())[0].replace("{REPLACE_HERE}", cell_val_suffix)

                # carry out method of column processing based on
                # the sbol_term of the column
                col_meth = cf.sbol_methods(sheet_tbl.column_list[col].namespace_url,
                                           component, doc, cell_val)
                col_meth.switch(sheet_tbl.column_list[col].sbol_term)

        doc.addComponentDefinition(component)
    # print(doc)
    doc.write(file_path_out)

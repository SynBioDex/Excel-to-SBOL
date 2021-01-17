#download so-simple.json from https://github.com/The-Sequence-Ontology/SO-Ontologies/tree/master/Ontology_Files
#or pull from https://github.com/SynBioDex/SBOLExplorer/blob/master/flask/so-simplified.json

import os
import json
import csv

cwd = os.getcwd()
path_in = os.path.join(cwd, "excel2sbol","resources","taxonomy_scrapers","so-simplified.json")
path_out = os.path.join(cwd, "excel2sbol","resources","taxonomy_scrapers","SO.csv")

with open(path_in, 'r') as f:
    data = f.read()

json_data = json.loads(data)

with open(path_out, 'wt') as so_csv:
    writer = csv.writer(so_csv)
    writer.writerow(["ID", "Name", "Alternate_Names"])

    for item in json_data:
        writer.writerow([item['id'], item['lbl'], item['synonyms']]) 


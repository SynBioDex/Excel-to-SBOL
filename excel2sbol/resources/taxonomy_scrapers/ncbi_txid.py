# pull taxdmp.zip from https://ftp.ncbi.nih.gov/pub/taxonomy/ and put names.dmp in the same folder as the scraper

import csv
import os

cwd = os.getcwd()
path_in = os.path.join(cwd, "excel2sbol", "resources", "taxonomy_scrapers",
                       "names.dmp")
path_out = os.path.join(cwd, "excel2sbol", "resources", "taxonomy_scrapers",
                        "names.csv")

id_to_name = {}

with open(path_in, 'rt') as names:
    line = names.readline()
    while line:
        id, name, u_name, n_class, blank = [field.strip() for field in line.split('|')]

        if n_class == "scientific name":
            if id in id_to_name:
                raise ValueError(f"Duplicate id {id} ({name} vs {id_to_name[id]})")

            id_to_name[id] = name

        line = names.readline()

with open(path_out, 'wt') as names_csv:
    writer = csv.writer(names_csv)
    writer.writerow(["ID", "Name"])

    for id, name in id_to_name.items():
        writer.writerow([id, name])

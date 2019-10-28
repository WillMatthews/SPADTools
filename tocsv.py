#!/usr/bin/python3

import pickle
import csv


with open("./.spadcompare.pickle", "rb") as f:
    spads = pickle.load(f)



with open("./csv_out.csv", "w") as f:
    titlerow = list(spads[0].keys())
    writer = csv.writer(f)
    writer.writerow(titlerow)
    for spad in spads:
        row_out = []
        for key in spad.keys():
            row_out.append(spad[key])
        writer.writerow(row_out)

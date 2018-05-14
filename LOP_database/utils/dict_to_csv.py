#!/usr/bin/env python
# -*- coding: utf8 -*-

import csv


def dict_to_csv(dico, path_csv):
    with open(path_csv, 'w') as csvfile:
        fieldnames = dico.keys()
        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(dico)

#!/usr/bin/env python
# -*- coding: utf8 -*-

import csv


def dict_to_csv(dict, path_csv):
    with open(path_csv, 'wb') as csvfile:
        fieldnames = dict.keys()
        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(dict)

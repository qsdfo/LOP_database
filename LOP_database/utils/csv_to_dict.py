#!/usr/bin/env python
# -*- coding: utf8 -*-

import csv


def csv_to_dict(csv_path):
    with open(csv_path, 'r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        return reader.next()

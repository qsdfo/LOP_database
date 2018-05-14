#!/usr/bin/env python
# -*- coding: utf8 -*-

import csv
import numpy as np


def map_instrument(pr, csv_file):
    with open(csv_file, 'r') as f0:
        r0 = csv.DictReader(f0, delimiter=';')
        instru_map = next(r0)

    pr_new = {}
    for source, dest in instru_map.items():
        if dest in pr_new.keys():
            pr_new[dest] = np.maximum(pr_new[dest], pr[source])
        else:
            pr_new[dest] = pr[source]

    return pr_new

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from LOP_database.utils.pianoroll_processing import sum_along_instru_dim
from LOP_database.visualization.numpy_array.write_numpy_array_html import write_numpy_array_html
from LOP_database.visualization.numpy_array.dumped_numpy_to_csv import dump_to_csv


def visualize_dict(pr, path, file_name_no_extension, time_indices=None):
    AAA = sum_along_instru_dim(pr)
    if time_indices:
        start_time, end_time = time_indices
        AAA = AAA[start_time:end_time, :]
    temp_csv = path + '/' + file_name_no_extension + '.csv'
    np.savetxt(temp_csv, AAA, delimiter=',')
    dump_to_csv(temp_csv, temp_csv)
    write_numpy_array_html(path + '/' + file_name_no_extension + ".html", file_name_no_extension, d3js_source_path='/Users/leo/Recherche/GitHub_Aciditeam/acidano/acidano/visualization/d3.v3.min.js')


def visualize_mat(pr, path, file_name_no_extension, time_indices=None):
    if time_indices:
        start_time, end_time = time_indices
        pr = pr[start_time:end_time, :]
    temp_csv = path + '/' + file_name_no_extension + '.csv'
    np.savetxt(temp_csv, pr, delimiter=',')
    dump_to_csv(temp_csv, temp_csv)
    write_numpy_array_html(path + '/' + file_name_no_extension + ".html", file_name_no_extension, 'rainbow', d3js_source_path='/Users/leo/Recherche/GitHub_Aciditeam/acidano/acidano/visualization/d3.v3.min.js')


def visualize_mat_proba(pr, path, file_name_no_extension, time_indices=None):
    if time_indices:
        start_time, end_time = time_indices
        pr = pr[start_time:end_time, :]
    temp_csv = path + '/' + file_name_no_extension + '.csv'
    np.savetxt(temp_csv, pr, delimiter=',')
    dump_to_csv(temp_csv, temp_csv)
    write_numpy_array_html(path + '/' + file_name_no_extension + ".html", file_name_no_extension, 'rainbow', (0, 1), d3js_source_path='/Users/leo/Recherche/GitHub_Aciditeam/acidano/acidano/visualization/d3.v3.min.js')

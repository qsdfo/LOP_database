#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
from LOP_database.utils.pianoroll_processing import sum_along_instru_dim


def remove_unused_pitch(pr, mapping):
    mapping_reduced = {}
    start_index = 0
    # First build the mapping
    for instru, pitch_range in mapping.iteritems():
        # Extract the pianoroll of this instrument
        start_index_pr = pitch_range[0]
        end_index_pr = pitch_range[1]
        pr_instru = pr[:, start_index_pr:end_index_pr]
        # Get lowest/highest used pitch
        existing_pitches = np.nonzero(pr_instru)[1]
        if np.shape(existing_pitches)[0] > 0:
            start_pitch = np.amin(existing_pitches)
            end_pitch = np.amax(existing_pitches) + 1
            end_index = start_index + end_pitch - start_pitch
            mapping_reduced[instru] = {'start_pitch': start_pitch,
                                       'end_pitch': end_pitch,
                                       'start_index': start_index,
                                       'end_index': end_index,
                                       # Indexex in the full matrix for reconstruction
                                       'start_index_rec': start_index_pr,
                                       'end_index_rec': end_index_pr}
            if 'pr_reduced' not in locals():
                pr_reduced = pr_instru[:, start_pitch:end_pitch]
            else:
                pr_reduced = np.concatenate((pr_reduced, pr_instru[:, start_pitch:end_pitch]), axis=1)

            start_index = end_index
    return pr_reduced, mapping_reduced


def remove_unmatched_silence(pr0, pr1):
    # Detect problems
    flat_0 = sum_along_instru_dim(pr0).sum(axis=1)
    flat_1 = sum_along_instru_dim(pr1).sum(axis=1)
    ind_clean = np.where(np.logical_not((flat_0 == 0) ^ (flat_1 == 0)))[0]

    def keep_clean(pr, ind_clean):
        pr_out = {}
        for k, v in pr.iteritems():
            pr_out[k] = v[ind_clean]
        return pr_out

    pr0_clean = keep_clean(pr0, ind_clean)
    pr1_clean = keep_clean(pr1, ind_clean)
    duration = len(ind_clean)

    return pr0_clean, pr1_clean, duration


def remove_silence(pr):
    # Detect silences
    flat = sum_along_instru_dim(pr).sum(axis=1)
    ind_clean = np.where(np.logical_not(flat == 0))[0]

    def keep_clean(pr, ind_clean):
        pr_out = {}
        for k, v in pr.iteritems():
            pr_out[k] = v[ind_clean]
        return pr_out
    pr_clean = keep_clean(pr, ind_clean)

    mapping = np.zeros((flat.shape[0]), dtype=np.int) - 1
    counter = 0
    for elem in ind_clean:
        mapping[elem] = counter
        counter += 1

    return pr_clean, mapping


def remove_match_silence(pr0, pr1):
    # Detect problems
    flat_0 = sum_along_instru_dim(pr0).sum(axis=1)
    flat_1 = sum_along_instru_dim(pr1).sum(axis=1)
    ind_clean = np.where(np.logical_not((flat_0 == 0) & (flat_1 == 0)))[0]

    def keep_clean(pr, ind_clean):
        pr_out = {}
        for k, v in pr.iteritems():
            pr_out[k] = v[ind_clean]
        return pr_out

    pr0_clean = keep_clean(pr0, ind_clean)
    pr1_clean = keep_clean(pr1, ind_clean)
    duration = len(ind_clean)

    return pr0_clean, pr1_clean, duration


def reconstruct_full_pr(pr_reduced, mapping_reduced):
    # Catch full size pr pitch dimension
    max_index = 0
    for value in mapping_reduced.itervalues():
        max_index = max(max_index, value['end_index_rec'])
    pitch_dimension = max_index
    time_dimension = pr_reduced.shape[0]
    pr = np.zeros((time_dimension, pitch_dimension))
    mapping = {}
    for instru_name, value in mapping_reduced.iteritems():
        mapping[instru_name] = (value['start_index_rec'], value['end_index_rec'])
        start_index = value['start_index_rec'] + value['start_pitch']
        end_index = value['start_index_rec'] + value['end_pitch']
        # Small verification
        if end_index > value['end_index_rec']:
            raise NameError('Conflicting indices during reconstruction')
        pr[:, start_index: end_index] = pr_reduced[:, value['start_index']: value['end_index']]
    return pr, mapping

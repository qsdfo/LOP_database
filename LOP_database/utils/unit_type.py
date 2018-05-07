#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# Convert the matrices for binary, categorical or real units
import numpy as np
import re
import math


def from_rawpr_to_type(dico_matrix, unit_type):
    result = {}
    # Binary unit ?
    if unit_type == 'binary':
        for k, matrix in dico_matrix.items():
            matrix[np.nonzero(matrix)] = 1
            result[k] = matrix
    elif unit_type == 'continuous':
        # Much easier to work with unit between 0 and 1, for several reason :
        #       - 'normalized' values
        #       - same reconstruction as for binary units when building midi files
        for k, matrix in dico_matrix.items():
            res_mat = matrix / 127.0
            result[k] = res_mat
    elif re.search('categorical', unit_type):
        # Categorical
        for k, matrix in dico_matrix.items():
            m = re.search(r'[0-9]+$', unit_type)
            N_category = int(m.group(0))
            matrix = matrix / 127.0
            matrix = from_continuous_to_categorical(matrix, N_category)
            result[k] = matrix
    else:
        raise Error(unit_type + 'is not a unit type')
    return result


def from_type_to_binary(pr, unit_type):
    result = {}
    if unit_type == 'binary':
        return pr
    elif unit_type == 'continuous':
        for k, matrix in pr.items():
            res_mat = np.copy(matrix)
            res_mat[np.nonzero(res_mat)] = 1
            result[k] = res_mat
    elif re.search('categorical', unit_type):
        m = re.search(r'[0-9]+$', unit_type)
        N_category = int(m.group(0))
        # Group by N_category
        for k, m in pr.items():
            T = m.shape[0]
            N_in = m.shape[1]
            N_out = N_in / N_category
            m_out = np.zeros((T, N_out))
            for n in range(N_out):
                start_pitch = n * N_category
                end_pitch = start_pitch + N_category
                # Dot product :
                intensity = np.dot(m[:, start_pitch:end_pitch], np.asarray(range(N_category)))
                m_out[:, n] = (intensity > 0)  #  Binaries activations
            result[k] = m_out
    return result


def from_continuous_to_categorical(pr_continuous, C):
    # pr_continuous = matrix, values between 0 1
    # C = number of category
    #
    # Output a pr with size (Time, Pitch * N_category)
    # For example, pitch = 2, Cat = 3 and T = 1, we have in this order the pairs (Pitch,Cat)
    # ((1,1), (1,2), (1,3), (2,1), (2,2), (2,3))
    #
    # Hence, units in the model have to be softmax over N_category (here 3) since one category can be on at each time

    pr_cat = np.zeros((pr_continuous.shape[0], pr_continuous.shape[1]*C))

    T = pr_continuous.shape[0]
    P = pr_continuous.shape[1]

    # Mutliply pr_continuous by the number of category
    for t in range(T):
        for p in range(P):
            if pr_continuous[t, p] == 0.0:
                cat_intensity = 0
            elif pr_continuous[t, p] == 1.0:
                cat_intensity = C-1
            else:
                cat_intensity = int(math.floor(pr_continuous[t, p] * (C-1)) + 1)
            ind_cat = p * C + cat_intensity
            pr_cat[t, ind_cat] = 1

    ########## DEBUG ######################
    # from acidano.visualization.numpy_array.visualize_numpy import visualize_mat
    # visualize_mat(pr_continuous, 'DEBUG', 'continuous')
    # visualize_mat(pr_cat, 'DEBUG', 'categorical')
    # import pdb; pdb.set_trace()
    #######################################
    return pr_cat

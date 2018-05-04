#!/usr/bin/env python
# -*- coding: utf8 -*-

import math
import numpy as np
from LOP_database.utils.pianoroll_processing import pitch_class, get_pianoroll_time #, sum_along_instru_dim
#from fastdtw import fastdtw
#from scipy.spatial.distance import euclidean

import LOP_database.utils.needleman_chord


def linear_warp_pr(pianoroll, T_target):
    # Ensure we actually read a pianoroll
    # T_target is a scalar
    out = {}
    T_source = get_pianoroll_time(pianoroll)
    ratio = T_source / float(T_target)
    index_mask = [int(math.floor(x * ratio)) for x in range(0, T_target)]
    for k, v in pianoroll.items():
        out[k] = pianoroll[k][index_mask, :]
    return out


# Must convert this to a list of integer
def conversion_to_integer_list(pr, lenght):
    nb_class = pr.shape[1]
    mask = np.zeros((nb_class), dtype=np.int)
    for x in range(nb_class):
        mask[x] = int(2**x)
    output = np.sum(pr * mask, axis=1)
    return output.tolist()


def needleman_chord_wrapper(pr1, pr2, gapopen, gapextend):
    # pr1 and pr2 are numpy matrices
    # For dictionnaries pianorolls, first apply sum_along_instru_dim
    # to obtain a matrix.
    # To warp the pr dictionnary on the returned warped time path,
    # use the next function : warp_dictionnary_trace()
    pr1_pitch_class = pitch_class(pr1)
    pr2_pitch_class = pitch_class(pr2)
    len1 = pr1_pitch_class.shape[0]
    len2 = pr2_pitch_class.shape[0]

    # Compute the trace
    pr1_list = conversion_to_integer_list(pr1_pitch_class, len1)
    pr2_list = conversion_to_integer_list(pr2_pitch_class, len2)
    # Traces are backward
    trace_0, trace_1, sum_score, nbId, nbGaps = needleman_chord.needleman_chord(pr1_list, pr2_list, gapopen, gapextend)

    return trace_0[::-1], trace_1[::-1], sum_score, nbId, nbGaps


def warp_dictionnary_trace(dico, trace):
    dico_out = {}
    # dico is a pianoroll dictionary
    time_len = len(trace)
    # Warp each numpy matrix in the dictionary
    for key, value in dico.items():
        time_value = value.shape[0]
        pr_temp = np.zeros((time_len, value.shape[1]))
        counter = 0
        for (i, bool_note) in enumerate(trace):
            if counter >= time_value:
                break
            if bool_note:
                pr_temp[i] = value[counter]
                counter += 1

        dico_out[key] = pr_temp

    return dico_out


def remove_zero_in_trace(dico, trace):
    # Trace is a binary list indicating if a gap is inserted or not in a matrix
    dico_out = {}
    time_len = sum(trace)
    for k, v in dico.items():
        pr_temp = np.zeros((time_len, v.shape[1]))
        counter = 0
        for (i, bool_note) in enumerate(trace):
            if bool_note:
                pr_temp[counter] = v[i]
                counter += 1

        dico_out[k] = pr_temp

    return dico_out


def warp_pr_aux(pr, path):
    pr_warp = {}
    for k, v in pr.items():
        pr_warp[k] = v[path]
    return pr_warp


#def dtw_pr(pr0, pr1):
#    # Flatten pr to compute the path
#    pr0_flat = sum_along_instru_dim(pr0)
#    pr1_flat = sum_along_instru_dim(pr1)
#
#    def fun_thresh(y):
#        return np.minimum(y, 1).astype(int)
#
#    distance, path = fastdtw(pr0_flat, pr1_flat, dist=lambda a, b: euclidean(fun_thresh(a), fun_thresh(b)))
#    # Get paths
#    path0 = [e[0] for e in path]
#    path1 = [e[1] for e in path]
#
#    pr0_warp = warp_pr_aux(pr0, path0)
#    pr1_warp = warp_pr_aux(pr1, path1)
#
#    return pr0_warp, pr1_warp


if __name__ == '__main__':
    l0 = [1, 1, 2, 4, 4, 4, 4, 4, 9, 9, 9, 9, 9]
    l1 = [1, 1, 2, 4, 4, 0, 0, 9]

    gapopen = 3
    gapextend = 1
    trace_0, trace_1, sum_score, nbId, nbGaps = needleman_chord.needleman_chord(l0, l1, gapopen, gapextend)

    print("Sum score : %d\n" % sum_score)

    def list_proc_aux(l):
        # l = [l[0]] + l
        # # Repeat first element
        # l.append(l[-1])
        # # Reverse
        # ll = l[::-1]
        # ll = [l[-1]] + l[1:-1] + [l[0]]
        return l[::-1]

    trace_0 = list_proc_aux(trace_0)
    trace_1 = list_proc_aux(trace_1)

    print(l0)
    print(trace_0)
    ll0 = []
    counter = 0
    for a in trace_0:
        if a:
            ll0.append(str(l0[counter]))
            counter += 1
        else:
            ll0.append("#")

    print(l1)
    print(trace_1)
    ll1 = []
    counter = 0
    for a in trace_1:
        if a:
            ll1.append(str(l1[counter]))
            counter += 1
        else:
            ll1.append("#")

    for i in range(len(trace_0)):
        print('{}         {}'.format(ll0[i], ll1[i]))

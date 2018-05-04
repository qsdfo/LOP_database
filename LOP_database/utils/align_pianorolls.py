#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

import glob
import re
import csv
from unidecode import unidecode
import numpy as np
from LOP_database.utils.time_warping import needleman_chord_wrapper, warp_dictionnary_trace, remove_zero_in_trace 
from LOP_database.utils.pianoroll_processing import sum_along_instru_dim
import LOP_database.utils.unit_type as Unit_type


def align_pianorolls(pr0, pr1, gapopen, gapextend):
    # Get trace from needleman_wunsch algorithm
    # Gapopen an gapextend are parameters of the needleman-wunsch algo

    # First extract binary representation, whatever unit_type is
    pr0_binary = Unit_type.from_type_to_binary(pr0, 'continuous')
    pr1_binary = Unit_type.from_type_to_binary(pr1, 'continuous')  
    pr0_trace = sum_along_instru_dim(pr0_binary)
    pr1_trace = sum_along_instru_dim(pr1_binary)

    # Traces are computed from binaries matrices
    # Traces are binary lists, 0 meaning a gap is inserted
    trace_0, trace_1, this_sum_score, this_nbId, this_nbDiffs = needleman_chord_wrapper(pr0_trace, pr1_trace, gapopen, gapextend)

    ####################################
    # Wrap dictionnaries according to the traces
    assert(len(trace_0) == len(trace_1)), "size mismatch"
    pr0_warp = warp_dictionnary_trace(pr0, trace_0)
    pr1_warp = warp_dictionnary_trace(pr1, trace_1)

    ####################################
    # Trace product
    trace_prod = [e1 * e2 for (e1, e2) in zip(trace_0, trace_1)]
    duration = sum(trace_prod)
    if duration == 0:
        return [None]*6
    # Remove gaps
    pr0_aligned = remove_zero_in_trace(pr0_warp, trace_prod)
    pr1_aligned = remove_zero_in_trace(pr1_warp, trace_prod)

    return pr0_aligned, trace_0, pr1_aligned, trace_1, trace_prod, duration

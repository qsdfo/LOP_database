#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import LOP_database.utils.pianoroll_processing as pianoroll_processing


# Data augmentation
def pitch_transposition(pr, pitch_shift):
    # pr is a dictionary pianoroll, before mapping to instruments
    # so dimensions are N_instru*128
    if pitch_shift == 0:
        return pr
    T = pianoroll_processing.get_pianoroll_time(pr)
    N = pianoroll_processing.get_pitch_dim(pr)
    pr_shifted = {}
    for k, normal in pr.iteritems():
        shift = np.zeros((T, N))
        if pitch_shift > 0:
            shift[:, pitch_shift:] = normal[:, 0:N-pitch_shift]
        else:
            shift[:, :N+pitch_shift] = normal[:, -pitch_shift:]
        pr_shifted[k] = shift

    return pr_shifted

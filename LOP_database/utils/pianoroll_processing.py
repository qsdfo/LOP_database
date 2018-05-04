#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# get_pianoroll_time
# sum_along_instru_dim
# get_first_last_non_zero
# clip_pr
# pitch_class
# binary_pr

import numpy as np


def get_pianoroll_time(pianoroll):
    T_pr_list = []
    for k, v in pianoroll.items():
        T_pr_list.append(v.shape[0])
    if not len(set(T_pr_list)) == 1:
        print("Inconsistent dimensions in the new PR")
        return None
    return T_pr_list[0]


def get_pitch_dim(pianoroll):
    N_pr_list = []
    for k, v in pianoroll.items():
        N_pr_list.append(v.shape[1])
    if not len(set(N_pr_list)) == 1:
        print("Inconsistent dimensions in the new PR")
        raise NameError("Pr dimension")
    return N_pr_list[0]


def sum_along_instru_dim(pianoroll):
    T_pr = get_pianoroll_time(pianoroll)
    N_pr = get_pitch_dim(pianoroll)
    rp = np.zeros((T_pr, N_pr), dtype=np.int16)
    for k, v in pianoroll.items():
        rp = np.maximum(rp, v)
    return rp


def get_first_last_non_zero(pianoroll):
    PR = sum_along_instru_dim(pianoroll)
    first = min(np.nonzero(np.sum(PR, axis=1))[0])
    last = max(np.nonzero(np.sum(PR, axis=1))[0])
    return first, last


def clip_pr(pianoroll):
    # Remove zero at the beginning and end of prs
    out = {}
    start_time, end_time = get_first_last_non_zero(pianoroll)
    for k, v in pianoroll.items():
        out[k] = v[start_time:end_time, :]
    return out


def pitch_class(pr):
    nb_class = 12
    nb_pitch = pr.shape[1]
    if not nb_pitch == 128:
        raise Exception('Pitch dimension should be equal to 128')
    pr_red = np.zeros((pr.shape[0], nb_class))
    for p in range(nb_pitch):
        c = p % nb_class
        pr_red[:, c] += pr[:, p]
    # Binary
    pr_red_bin = (pr_red > 0).astype(int)
    return pr_red_bin

def extract_pianoroll_part(pianoroll, start_time, end_time):
    new_pr = {}
    # Start and end time are given in discrete frames
    for k,v in pianoroll.items():
        new_pr[k] = v[start_time:end_time]
    return new_pr


if __name__ == "__main__":
    from acidano.data_processing.midi.read_midi import Read_midi

    song_path = 'test.mid'
    midifile = Read_midi(song_path, 8)
    midifile.read_file()
    pr = midifile.pianoroll
    pr_class = pitch_class(pr)

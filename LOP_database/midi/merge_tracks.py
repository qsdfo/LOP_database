#!/usr/bin/env python
# -*- coding: utf8 -*-

## Merge along time dimension

import numpy as np
from LOP_database.midi.read_midi import read_midi, get_time
from LOP_database.midi.write_midi import write_midi


def merge_tracks(tracks, dest_path):
    # Merging is easier with pianorollls
    quantization = 64
    T = 0
    for track in tracks:
        # Add a 4 quarter silence
        T += get_time(track, quantization) + quantization * 4

    t = 0
    flag_time_increment = True
    pr = {}
    for track in tracks:
        a = read_midi(track, quantization)
        for k in a.keys():
            if flag_time_increment:
                tt = t + a[k].shape[0]
                flag_time_increment = False
            if k not in pr.keys():
                pr[k] = np.zeros((T, 128))
            pr[k][t:tt] = a[k]
        t = tt + quantization * 4
        flag_time_increment = True

    write_midi(pr, quantization, dest_path, tempo=80)
    return


if __name__ == '__main__':
    tracks = [
        '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration_checked/liszt_classical_archives/19/symphony_5_4_solo.mid',
        '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration_checked/liszt_classical_archives/19/symphony_5_3_solo.mid'
    ]
    dest_path = '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration_checked/liszt_classical_archives/19/symphony_5_3-4.mid'
    merge_tracks(tracks, dest_path)

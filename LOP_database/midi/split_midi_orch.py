#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import unicodecsv as csv
from mido import MidiFile


def split_midi_orch(f, c, list_instru):
    # Read a midi file and return a dictionnary {track_name : pianoroll}
    mid_in = MidiFile(f)
    mid_orch = MidiFile()
    mid_solo = MidiFile()
    # The two files need to have the same ticks per beat
    ticks_per_beat = mid_in.ticks_per_beat
    mid_orch.ticks_per_beat = ticks_per_beat
    mid_solo.ticks_per_beat = ticks_per_beat

    # get instrumentation
    with open(c, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        instrumentation = next(reader)

    # Parse track by track
    for i, track_in in enumerate(mid_in.tracks):
        if track_in.name not in instrumentation.keys():
            # probably a metadata track, usefull for both files
            mid_solo.tracks.append(track_in)
            mid_orch.tracks.append(track_in)
        elif instrumentation[track_in.name] in list_instru:
            mid_solo.tracks.append(track_in)
        else:
            mid_orch.tracks.append(track_in)

    # Create the files
    path_orch = re.sub(ur'\.mid$', ur'_orch.mid', f, flags=re.I|re.U)
    path_solo = re.sub(ur'\.mid$', ur'_solo.mid', f, flags=re.I|re.U)
    mid_orch.save(path_orch)
    mid_solo.save(path_solo)

    return path_orch, path_solo

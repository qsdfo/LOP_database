#!/usr/bin/env python
# -*- coding: utf8 -*-

# Read a midi file in the event level representation

from mido import MidiFile
from unidecode import unidecode
import math


def read_midi_event(file, time_granularity=4):
    # events is a numpy array of dimension number_events * pitch containing the intensity of each pitch
    # times are the real time when the events occur

    # Read the midi file and return a dictionnary {track_name : pianoroll}
    mid = MidiFile(file)
    # Tick per beat
    ticks_per_beat = mid.ticks_per_beat
    # Time quantization
    quantization_factor = int(ticks_per_beat / time_granularity)
    
    # Pitch dimension
    N_pr = 128
    event_list = []

    # Build a list of events
    counter_unnamed_track = 0
    for i, track in enumerate(mid.tracks):
        # Parse all tracks, and build a list
        # (time, track_name, notes_on={pitches -> velocities})
        # Two successive events ??
        time_counter = 0
        notes_on = {}
        event_list_track = []
        track_name = unidecode(track.name).decode('utf8')
        if track_name == u'':
            track_name = 'unnamed' + str(counter_unnamed_track)
            counter_unnamed_track += 1
        for message in track:
            ########################################## 
            # Time
            # Must be incremented, whether it is a note on/off or not
            time_counter += float(message.time)
            ##########################################
            
            ##########################################
            # Pitch and velocity
            # Note on
            if message.type == 'note_on':
                # Get pitch
                pitch = message.note
                # Get velocity
                velocity = message.velocity
                if velocity > 0:
                    notes_on[pitch] = velocity
                elif velocity == 0:
                    del notes_on[pitch]
            # Note off
            elif message.type == 'note_off':
                # Get pitch
                pitch = message.note
                # Get velocity
                velocity = message.velocity
                del notes_on[pitch]
            else:
                continue
            ##########################################

            ########################################## 
            event_list_track.append((time_counter, track_name, dict(notes_on)))
            ########################################## 

        if len(event_list_track) == 0:
            continue

        first_event = event_list_track.pop(0)
        event_list_track_merge = [first_event]
        time = first_event[0]
        for next_event in event_list_track:
            if not(next_event[0] - time < quantization_factor):
                event_list_track_merge.append(next_event)
                time = next_event[0]

        event_list += event_list_track

    # Sort by time
    event_list.sort(key=lambda tup: tup[0])

    counter = 0
    for e in event_list:
        if e[1]=='Viole':
            counter += 1
            print(e)
        if counter == 100:
            import pdb; pdb.set_trace()
    
    return event_list, ticks_per_beat

if __name__=='__main__':
    read_midi_event("/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration/LOP_database_06_09_17/liszt_classical_archives/18/symphony_7_4_orch.mid")

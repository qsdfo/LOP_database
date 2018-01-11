#!/usr/bin/env python
# -*- coding: utf8 -*-

from mido import MidiFile
from unidecode import unidecode
from write_midi import write_midi
from LOP_database.utils.pianoroll_processing import sum_along_instru_dim
from LOP_database.utils.pianoroll_processing import get_pianoroll_time

from LOP_database.utils.event_level import get_event_ind_dict, from_event_to_frame
from LOP_database.utils.time_warping import warp_pr_aux

import numpy as np

from LOP_database.utils.time_warping import needleman_chord_wrapper, warp_dictionnary_trace, remove_zero_in_trace
import LOP_database.utils.unit_type as Unit_type

#######
# Pianorolls dims are  :   TIME  *  PITCH


class Read_midi(object):
    def __init__(self, song_path, quantization):
        ## Metadata
        self.__song_path = song_path
        self.__quantization = quantization

        ## Pianoroll
        self.__T_pr = None

        ## Private misc
        self.__num_ticks = None
        self.__T_file = None

    @property
    def quantization(self):
        return self.__quantization

    @property
    def T_pr(self):
        return self.__T_pr

    @property
    def T_file(self):
        return self.__T_file

    def get_total_num_tick(self):
        # Midi length should be written in a meta message at the beginning of the file,
        # but in many cases, lazy motherfuckers didn't write it...

        # Read a midi file and return a dictionnary {track_name : pianoroll}
        mid = MidiFile(self.__song_path)

        # Parse track by track
        num_ticks = 0
        for i, track in enumerate(mid.tracks):
            tick_counter = 0
            for message in track:
                # Note on
                time = float(message.time)
                tick_counter += time
            num_ticks = max(num_ticks, tick_counter)
        self.__num_ticks = num_ticks

    def get_pitch_range(self):
        mid = MidiFile(self.__song_path)
        min_pitch = 200
        max_pitch = 0
        for i, track in enumerate(mid.tracks):
            for message in track:
                if message.type in ['note_on', 'note_off']:
                    pitch = message.note
                    if pitch > max_pitch:
                        max_pitch = pitch
                    if pitch < min_pitch:
                        min_pitch = pitch
        return min_pitch, max_pitch

    def get_time_file(self):
        # Get the time dimension for a pianoroll given a certain quantization
        mid = MidiFile(self.__song_path)
        # Tick per beat
        ticks_per_beat = mid.ticks_per_beat
        # Total number of ticks
        self.get_total_num_tick()
        # Dimensions of the pianoroll for each track
        self.__T_file = int((self.__num_ticks / ticks_per_beat) * self.__quantization)
        return self.__T_file

    def read_file(self):
        # Read the midi file and return a dictionnary {track_name : pianoroll}
        mid = MidiFile(self.__song_path)
        # Tick per beat
        ticks_per_beat = mid.ticks_per_beat

        # Get total time
        self.get_time_file()
        T_pr = self.__T_file
        # Pitch dimension
        N_pr = 128
        pianoroll = {}

        def add_note_to_pr(note_off, notes_on, pr):
            pitch_off, _, time_off = note_off
            # Note off : search for the note in the list of note on,
            # get the start and end time
            # write it in th pr
            match_list = [(ind, item) for (ind, item) in enumerate(notes_on) if item[0] == pitch_off]
            if len(match_list) == 0:
                print("Try to note off a note that has never been turned on")
                # Do nothing
                return

            # Add note to the pr
            pitch, velocity, time_on = match_list[0][1]
            pr[time_on:time_off, pitch] = velocity
            # Remove the note from notes_on
            ind_match = match_list[0][0]
            del notes_on[ind_match]
            return

        # Parse track by track
        counter_unnamed_track = 0
        for i, track in enumerate(mid.tracks):
            # Instanciate the pianoroll
            pr = np.zeros([T_pr, N_pr])
            time_counter = 0
            notes_on = []
            for message in track:

                ##########################################
                ##########################################
                ##########################################
                # TODO : keep track of tempo information
                # import re
                # if re.search("tempo", message.type):
                #     import pdb; pdb.set_trace()
                ##########################################
                ##########################################
                ##########################################


                # print message
                # Time. Must be incremented, whether it is a note on/off or not
                time = float(message.time)
                time_counter += time / ticks_per_beat * self.__quantization
                # Time in pr (mapping)
                time_pr = int(round(time_counter))
                # Note on
                if message.type == 'note_on':
                    # Get pitch
                    pitch = message.note
                    # Get velocity
                    velocity = message.velocity
                    if velocity > 0:
                        notes_on.append((pitch, velocity, time_pr))
                    elif velocity == 0:
                        add_note_to_pr((pitch, velocity, time_pr), notes_on, pr)
                # Note off
                elif message.type == 'note_off':
                    pitch = message.note
                    velocity = message.velocity
                    add_note_to_pr((pitch, velocity, time_pr), notes_on, pr)

            # We deal with discrete values ranged between 0 and 127
            #     -> convert to int
            pr = pr.astype(np.int16)
            if np.sum(np.sum(pr)) > 0:
                name = unidecode(track.name).decode('utf8')
                name = name.rstrip('\x00')
                if name == u'':
                    name = 'unnamed' + str(counter_unnamed_track)
                    counter_unnamed_track += 1
                if name in pianoroll.keys():
                    # Take max of the to pianorolls
                    pianoroll[name] = np.maximum(pr, pianoroll[name])
                else:
                    pianoroll[name] = pr
        return pianoroll


if __name__ == '__main__':
    from LOP_database.visualization.numpy_array.visualize_numpy import visualize_dict, visualize_dict_concat, visualize_mat
    from LOP.Database.build_data_aux import process_folder, get_instru_and_pr_from_folder_path, simplify_instrumentation
    import LOP_database.utils.pianoroll_processing as pianoroll_processing

    orch_path = '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration/LOP_database_06_09_17/bouliane/3/Moussorgsky_TableauxProm(24 mes)_ORCH+REDUC+piano_orch.mid'
    # piano_path = '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration/LOP_database_06_09_17/liszt_classical_archives/18/_beet7_4_solo.mid'
    quantization = 8
    start_ind = 0
    end_ind = 173
    
    pr_orch = Read_midi(orch_path, quantization).read_file()
    for k, v in pr_orch.iteritems():
        visualize_mat(v, "DEBUG", k, (start_ind, end_ind))

    # ########################################################
    # orch = sum_along_instru_dim(pr)[start_ind:end_ind] 
    # # orch[np.nonzero(orch)] = 1
    # orch[0, 30] = 1
    # orch[0, 92] = 1
    # #######################################################

    # #######################################################
    # pr_piano = Read_midi(piano_path, quantization).read_file()
    # #######################################################

    # #######################################################
    # # Event level representation
    # event_piano = get_event_ind_dict(pr_piano)
    # event_orch = get_event_ind_dict(pr_orch)
    # pr_piano = warp_pr_aux(pr_piano, event_piano)
    # pr_orch = warp_pr_aux(pr_orch, event_orch)
    # ########################################################

    # def align_tracks(pr0, pr1, unit_type, gapopen, gapextend):
    #     # Get trace from needleman_wunsch algorithm

    #     # First extract binary representation, whatever unit_type is
    #     pr0_binary = Unit_type.from_type_to_binary(pr0, unit_type)
    #     pr1_binary = Unit_type.from_type_to_binary(pr1, unit_type)  
    #     pr0_trace = sum_along_instru_dim(pr0_binary)
    #     pr1_trace = sum_along_instru_dim(pr1_binary)

    #     # Traces are computed from binaries matrices
    #     # Traces are binary lists, 0 meaning a gap is inserted
    #     trace_0, trace_1, this_sum_score, this_nbId, this_nbDiffs = needleman_chord_wrapper(pr0_trace, pr1_trace, gapopen, gapextend)

    #     ####################################
    #     # Wrap dictionnaries according to the traces
    #     assert(len(trace_0) == len(trace_1)), "size mismatch"
    #     pr0_warp = warp_dictionnary_trace(pr0, trace_0)
    #     pr1_warp = warp_dictionnary_trace(pr1, trace_1)

    #     ####################################
    #     # Trace product
    #     trace_prod = [e1 * e2 for (e1, e2) in zip(trace_0, trace_1)]
    #     duration = sum(trace_prod)
    #     if duration == 0:
    #         return [None]*6
    #     # Remove gaps
    #     pr0_aligned = remove_zero_in_trace(pr0_warp, trace_prod)
    #     pr1_aligned = remove_zero_in_trace(pr1_warp, trace_prod)

    #     return pr0_aligned, trace_0, pr1_aligned, trace_1, trace_prod, duration

    # pr_piano, trace_0, pr_orch, trace_1, trace_prod, duration = align_tracks(pr_piano, pr_orch, 'binary', 3, 2)

    # ########################################################
    # horn = sum_along_instru_dim({k: pr_orch[k][start_ind:end_ind] for k in [u'Horn 1', u'Horn 3']})
    # tuba = sum_along_instru_dim({k: pr_orch[k][start_ind:end_ind] for k in [u'Tuba 1']})
    # trumpet = sum_along_instru_dim({k: pr_orch[k][start_ind:end_ind] for k in [u'Trumpet 2', u'Trumpet 1']})
    # trombone = sum_along_instru_dim({k: pr_orch[k][start_ind:end_ind] for k in [u'Trombone Bass', u'Trombone 1']})
    # orch = np.concatenate([horn, tuba, trumpet, trombone], axis=1)
    # ########################################################

    # piano = sum_along_instru_dim(pr_piano)[start_ind:end_ind]
    # piano[np.nonzero(piano)] = 1
    # # piano[0, 30] = 1
    # # piano[0, 92] = 1

    # orch[np.nonzero(orch)] = 1
    # piano[np.nonzero(piano)] = 1

    # visualize_mat(orch, 'DEBUG', 'orch', time_indices=None)
    # visualize_mat(piano, 'DEBUG', 'piano', time_indices=None)
    
    # # call(["open", "DEBUG/numpy_vis.html"])

    # # pr_clip = clip_pr(pr)
    # # pr_warped = linear_warp_pr(pr_clip, int(midifile.T_pr * 0.6))

    # # write_midi(pr_warped, midifile.quantization, 'DEBUG/out.mid')
    # # write_midi(midifile.pianoroll, midifile.quantization, 'DEBUG/out2.mid')
    # # for name_instru in midifile.pianoroll.keys():
    # #     np.savetxt('DEBUG/' + name_instru + '.csv', midifile.pianoroll[name_instru], delimiter=',')
    # #     dump_to_csv('DEBUG/' + name_instru + '.csv', 'DEBUG/' + name_instru + '.csv')

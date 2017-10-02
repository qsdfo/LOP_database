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
        self.pianoroll = None
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

    @property
    def pianoroll(self):
        return self.__pianoroll

    @pianoroll.setter
    def pianoroll(self, pr):
        # Ensure that the dimensions are always correct
        if pr is None:
            self.__pianoroll = None
            return
        T_pr = get_pianoroll_time(pr)
        if T_pr:
            self.__T_pr = T_pr
            self.__pianoroll = pr
        else:
            self.__pianoroll = None

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
                if name == u'':
                    name = 'unnamed' + str(counter_unnamed_track)
                    counter_unnamed_track += 1
                if name in pianoroll.keys():
                    # Take max of the to self.pianorolls (lame solution;...)
                    pianoroll[name] = np.maximum(pr, pianoroll[name])
                else:
                    pianoroll[name] = pr
        self.pianoroll = pianoroll
        return pianoroll


if __name__ == '__main__':
    from LOP_database.visualization.numpy_array.visualize_numpy import visualize_dict, visualize_mat
    from LOP.Database.Frame_level.build_data_aux import process_folder, get_instru_and_pr_from_folder_path, simplify_instrumentation
    import LOP_database.utils.pianoroll_processing as pianoroll_processing

    folder_path = '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration/LOP_database_06_09_17/liszt_classical_archives/18'
    quantization = 8
    temporal_granularity = 'event_level'

    # PR
    pr0, instru0, _, name0, pr_orch, instru_orch, _, name1 = get_instru_and_pr_from_folder_path(folder_path, quantization)
    event_orch = get_event_ind_dict(pr_orch)
    pr_orch = warp_pr_aux(pr_orch, event_orch)

    pr_simplified = {}
    for k, v in pr_orch.iteritems():
        new_k = instru_orch[k]
        if new_k != 'Remove':
            if new_k in pr_simplified.keys():
                pr_simplified[new_k] = np.maximum(pr_simplified[new_k], v)
            else:
                pr_simplified[new_k] = v

    # # align
    # # Align tracks
    # from LOP_database.utils.align_pianorolls import align_pianorolls
    # from LOP.Database.Frame_level.build_data_aux import clean_event
    # pr0_aligned, trace_0, pr_orch_aligned, trace_1, trace_prod, duration = align_pianorolls(pr0, pr_orch, 3, 1)
    # import pdb; pdb.set_trace()
    # event1_aligned = clean_event(event_orch, trace_1, trace_prod)
    
    # back to frame
    pr_frame = {k : from_event_to_frame(v, event_orch) for k, v in pr_simplified.iteritems()}

    # WRITE
    write_midi(pr_frame, quantization, "DEBUG/orch.mid", tempo=120)






    # ##### Import 
    # import cPickle as pkl
    # metadata = pkl.load(open("/Users/leo/Recherche/GitHub_Aciditeam/lop/Data/Data_DEBUG__event_level100__0/metadata.pkl", 'rb'))
    # instru_mapping = metadata["instru_mapping"]
    # N_orch = metadata["N_orchestra"]
    # N_piano = metadata["N_piano"]
    
    # pr_piano, event_piano, _, _, pr_orch, event_orch, instru_orch, _, duration = process_folder(folder_path, quantization, temporal_granularity, gapopen=5, gapextend=2)
    # write_midi(new_orch_rec, 1, "DEBUG/pr_orch.mid", tempo=200)

    # # Cut in pieces
    # def plot_pieces(pr, num_steps, name):
    #     duration = pr.shape[0]
    #     step = duration / num_steps
    #     parts = [pr[e*step:(e+1)*step] for e in range(num_steps)]
    #     for i, part in enumerate(parts):
    #         visualize_mat(part, 'DEBUG', name + str(i), time_indices=None)

    # #############
    
    # new_orch = np.zeros((duration, N_orch))
    # new_piano = np.zeros((duration, N_piano))

    # from LOP.Database.build_data import cast_pr
    # cast_pr(pr_orch, instru_orch, pr_piano, 0,
    #     duration, instru_mapping, new_orch, new_piano, None)

    # plot_np = np.concatenate([new_piano, np.zeros((duration, 20)), new_orch], axis=1)

    # # Plot of training matrices
    # plot_pieces(plot_np, 10, "orch_timewarped")

    # # Midi their reconstructions
    # from LOP_database.utils.reconstruct_pr import instrument_reconstruction
    # new_orch_rec = instrument_reconstruction(new_orch, instru_mapping)
    # write_midi(new_orch_rec, 1, "DEBUG/orch_reconstructed_notime_aligned.mid", tempo=200)

    # A = from_event_to_frame(new_orch, event_piano)
    # plot_pieces(A[24997:24997+5000], 10, "orch_reconstructed")
    # B = A
    # orchestra_reconstructed = instrument_reconstruction(B, instru_mapping)
    # write_midi(orchestra_reconstructed, quantization, "DEBUG/orch_reconstructed.mid", tempo=80)




    # orch_path = '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration/LOP_database_06_09_17/liszt_classical_archives/18/symphony_7_4_orch.mid'
    # piano_path = '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration/LOP_database_06_09_17/liszt_classical_archives/18/_beet7_4_solo.mid'
    # quantization = 100
    # # start_ind = 0
    # # end_ind = 88
    
    # pr_orch = Read_midi(orch_path, quantization).read_file()

    # ########################################################
    # # orch = sum_along_instru_dim(pr)[start_ind:end_ind] 
    # # orch[np.nonzero(orch)] = 1
    # # orch[0, 30] = 1
    # # orch[0, 92] = 1
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

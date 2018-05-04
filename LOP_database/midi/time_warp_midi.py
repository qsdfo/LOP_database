# #!/usr/bin/env python
# # -*- coding: utf8 -*-

# from mido import MidiFile, MidiTrack

# #######
# # Pianorolls dims are  :   TIME  *  PITCH


# def time_warp(source_path, dest_path, ratio):
#     # Read a midi file and return a dictionnary {track_name : pianoroll}
#     mid_in = MidiFile(source_path)
#     mid_out = MidiFile()
#     # The two files need to have the same ticks per beat
#     ticks_per_beat = mid_in.ticks_per_beat
#     mid_out.ticks_per_beat = ticks_per_beat

#     # Parse track by track
#     for i, track_in in enumerate(mid_in.tracks):
#         track_out = MidiTrack()
#         mid_out.tracks.append(track_out)
#         for message_in in track_in:
#             time_in = message_in.time
#             time_out = int(round(time_in * ratio))
#             # For absolutely every message, just mutliply the time by the ratio
#             message_out = message_in.copy(time=time_out)
#             track_out.append(message_out)
#     mid_out.save(dest_path)
#     return


# if __name__ == '__main__':
#     source = 'test.mid'
#     dest = 'out.mid'
#     time_warp(source, dest, 2)

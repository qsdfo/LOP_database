#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import glob
import os
import re
import shutil
from LOP_database.midi.read_midi import Read_midi
from LOP_database.midi.write_midi import write_midi
from LOP_database.utils.align_pianorolls import align_pianorolls


if __name__ == '__main__':
    
    # args = sys.argv
    args = ['', '/Users/leo/Recherche/GitHub_Aciditeam/database/Orchestration/LOP_database_06_09_17/bouliane']

    # Parameters should be set arbitrarily high, greater than 100
    quantization = 100

    IN_DB = args[1]

    if len(args) > 2:
        OUT_DB = args[2]
    else:
        OUT_DB = IN_DB + '_aligned'
    
    # Mkdir the new database
    if not os.path.exists(OUT_DB):
        os.makedirs(OUT_DB)
    else:
        answer = raw_input("Aligned DB seems to be already existing. Tape yes to continue : ")
        if answer != 'yes':
            quit()
        else:
            shutil.rmtree(OUT_DB)
            os.makedirs(OUT_DB)

    # Parse the database
    list_dir = os.listdir(IN_DB)
    for pair in list_dir:
        
        # Avoid hidden folders
        if pair[0] == '.':
            continue

        print('# ' + pair)

        # Get midi file names
        pair_folder = IN_DB + '/' + pair
        mid_files = glob.glob(pair_folder + '/*.mid')
        csv_files = glob.glob(pair_folder + '/*.csv')
        if len(mid_files) != 2:
            raise Error(pair_folder + " contains more than 2 midi files")
        
        # Read midi files
        prs = [Read_midi(e, quantization).read_file() for e in mid_files]

        # Align them
        pr0_aligned, _, pr1_aligned, _, _, _ = align_pianorolls(prs[0], prs[1], gapopen=3, gapextend=1)
        prs_out = [pr0_aligned, pr1_aligned]

        # Output file names
        mid_files_outS = [re.sub(IN_DB, OUT_DB, e) for e in mid_files]
        out_folder = re.sub(IN_DB, OUT_DB, pair_folder)

        # Create directory
        os.makedirs(out_folder)
        
        # Write aligned midi in it
        [write_midi(e[0], quantization, e[1]) for e in zip(prs_out, mid_files_outS)]
        # Copy csv files
        [shutil.copy(e, re.sub(IN_DB, OUT_DB, e)) for e in csv_files]
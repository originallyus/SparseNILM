#!/bin/bash
#
# USAGE: ./disagg_EMU2.py [modeldb] [precision] [measure] [algo name] [device]
# 
#        [modeldb]       - filename of model (omit file ext)
#        [precision]     - number; e.g. 10 would convert A to dA - just set to 1
#        [measure]       - the measurement, e.g. A for current - for display only
#        [algo name]     - specifiy the disaggregation algorithm to use - SparseViterbi / Viterbi
#        [filename]      - filename of data
# 

python disagg_file.py RAE_blk1 1 W SparseViterbi kitchen_power.txt

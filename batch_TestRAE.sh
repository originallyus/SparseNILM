#!/bin/bash
#
python train_SSHMM.py RAE_blk1 RAE_house1_power_blk1 1 24000 denoised 8 1 15+16,5+6,11+13+14,3+4+7+12+17+18+19+20+23,1+2,8,9,10,24
python test_Algorithm.py test_RAE_blk2 RAE_blk1 RAE_house1_power_blk2 1 W denoised all SparseViterbi

python train_SSHMM.py RAE_blk1_noisy RAE_house1_power_blk1 0.1 24000 noisy 5 1 5+6,11,13+14,1+2,8,10
python test_Algorithm.py test_RAE_blk2_noisy RAE_blk1_noisy RAE_house1_power_blk2 0.1 daW noisy all SparseViterbi

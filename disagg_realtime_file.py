#!/usr/bin/env python3
#
# Disaggregate smart meter reading from the EMU2 (disagg_EMU2.py)
# Copyright (C) 2016 Stephen Makonin. All Right Reserved.
#

import sys, json, serial
from statistics import mean
from time import *
from datetime import datetime
from libDataLoaders import dataset_loader
from libFolding import Folding
from libSSHMM import SuperStateHMM
from libAccuracy import Accuracy
import xml.etree.ElementTree as ElementTree


print()
print('-----------------------------------------------------------------------------------------')
print('Test running NILM and report stats each time  --  Copyright (C) 2016, by Stephen Makonin.')
print('-----------------------------------------------------------------------------------------')
print()
print('Start Time = ', datetime.now(), '(local time)')
print()

if len(sys.argv) != 6:
    print()
    print('USAGE: %s [modeldb] [precision] [measure] [algo name] [device]' % (sys.argv[0]))
    print()
    print('       [modeldb]       - filename of model (omit file ext).')
    print('       [precision]     - number; e.g. 10 would convert A to dA.')
    print('       [measure]       - the measurement, e.g. A for current')    
    print('       [algo name]     - specifiy the disaggregation algorithm to use.')
    print('       [filename]      - filename of data')
    print()
    exit(1)

print()
print('Parameters:', sys.argv[1:])
(modeldb, precision, measure, algo_name, filename) = sys.argv[1:]
precision = float(precision)
disagg_algo = getattr(__import__('algo_' + algo_name, fromlist=['disagg_algo']), 'disagg_algo')
print('Using disaggregation algorithm disagg_algo() from %s.' % ('algo_' + algo_name + '.py'))

datasets_dir = './datasets/%s.csv'
logs_dir = './logs/%s.log'
models_dir = './models/%s.json'

print()
print('Loading saved model %s from JSON storage (%s)...' % (modeldb, models_dir % modeldb))
fp = open(models_dir % modeldb, 'r')
jdata = json.load(fp)
fp.close()

# support single fold data model only
folds = len(jdata)
if folds != 1:
    print('ERROR: please use only single fold models.')
    exit(1)

print('\tLoading JSON data into SSHMM object...')
sshmms = []
for data in jdata:
    sshmm = SuperStateHMM()
    sshmm._fromdict(data)
    sshmms.append(sshmm)
del jdata
fold = 0
sshmm = sshmms[fold]

labels = sshmms[0].labels
print('\tModel lables are: ', labels)

print()
print('Testing %s algorithm load disagg...' % algo_name)
acc = Accuracy(len(labels), folds)

print()
print('Opening file %s...' % (filename))
file = open(filename, 'r') 
line_count = 0

y0 = -1
y1 = -1

while True:
    line_count += 1
    line = file.readline() 

    ts = int(time())
    dt = datetime.fromtimestamp(ts)
    
    # end of file
    if not line: 
        break

    # power reading, must be integer
    power = line
    power = int(int(power) * precision)
        
    # some kind of indexing on the data
    y0 = y1
    y1 = power
    if y0 == -1:
        y0 = y1
    
    # disaggregation algo, measure time in seconds
    start = time() 
    (p, k, Pt, cdone, ctotal) = disagg_algo(sshmm, [y0, y1])
    elapsed = (time() - start)

    s_est = sshmm.detangle_k(k)
    y_est = sshmm.y_estimate(s_est, breakdown=True)
    
    #where does this come from?
    hidden = [i for i in testing[labels].to_records(index=False)]
    y_true = hidden[i]                      #eg. (0, 0, 192, 136, 1, 122, 0, 0, 160)

    s_true = sshmm.obs_to_bins(y_true)      #eg. [0, 0, 6, 6, 1, 0, 0, 0, 1]

    acc.classification_result(fold, s_est, s_true, sshmm.Km)
    acc.measurement_result(fold, y_est, y_true)
    
    unseen = 'no'
    if p == 0.0:
        unseen = 'yes'
            
    y_noise = round(y1 - sum(y_true), 1)
        
    fscore = acc.fs_fscore()
    estacc = acc.estacc()
    scp = sum([i != j for (i, j) in list(zip(hidden[i - 1], hidden[i]))])
    print('Obs %5d%s Δ %4d%s | SCP %2d | FS-fscore %.4f | Est.Acc. %.4f | Time %7.3fms' % (y1, measure, y1 - y0, measure, scp, fscore, estacc, elapsed * 1000))

    sleep(1)


# Refer to this fork for better code https://github.com/acominola/SparseNILM/blob/master/test_Algorithm.py

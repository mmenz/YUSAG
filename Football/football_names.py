from __future__ import absolute_import, division, print_function

import os
from six import moves
import ssl
import csv
from random import sample

import tflearn
from tflearn.data_utils import *

path = "/Users/menz/Dropbox/YUSAG/2016-17/" \
       "NFL Timeouts/nfl_00-15/csv/PLAYER.csv"

maxlen = 100

names = []
with open(path) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        names.append(row['fname'] + ' ' + row['lname'])

print(len(names))
names = sample(names, 1000)

string_utf8 = "\n".join(names).decode('utf-8')
X, Y, char_idx = \
    string_to_semi_redundant_sequences(string_utf8,
                                       seq_maxlen=maxlen,
                                       redun_step=3)

g = tflearn.input_data(shape=[None, maxlen, len(char_idx)])
g = tflearn.lstm(g, 512, return_seq=True)
g = tflearn.dropout(g, 0.5)
g = tflearn.lstm(g, 512)
g = tflearn.dropout(g, 0.5)
g = tflearn.fully_connected(g, len(char_idx), activation='softmax')
g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                       learning_rate=0.001)

m = tflearn.SequenceGenerator(g, dictionary=char_idx,
                              seq_maxlen=maxlen,
                              clip_gradients=5.0,
                              checkpoint_path='model_football_names')

for i in range(40):
    seed = random_sequence_from_string(string_utf8, maxlen)
    m.fit(X, Y, validation_set=0.1, batch_size=1024,
          n_epoch=1, run_id='football_names')
    print("-- TESTING...")
    print("-- Test with temperature of 1.2 --")
    print(m.generate(30, temperature=1.2, seq_seed=seed).encode('utf-8'))
    print("-- Test with temperature of 1.0 --")
    print(m.generate(30, temperature=1.0, seq_seed=seed).encode('utf-8'))
    print("-- Test with temperature of 0.5 --")
    print(m.generate(30, temperature=0.5, seq_seed=seed).encode('utf-8'))

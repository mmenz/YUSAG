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

maxlen = 35

names = []
with open(path) as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        names.append(row['fname'] + ' ' + row['lname'])

# print(len(names))
# names = sample(names, 1000)

names_string = "\n".join(names).decode("utf-8")
print(names_string[-100:])
exit()
X, Y, char_idx = \
    string_to_semi_redundant_sequences(names_string,
                                       seq_maxlen=maxlen,
                                       redun_step=3)

g = tflearn.input_data(shape=[None, maxlen, len(char_idx)])
g = tflearn.lstm(g, 256, return_seq=True)
g = tflearn.dropout(g, 0.5)
g = tflearn.lstm(g, 256)
g = tflearn.dropout(g, 0.5)
g = tflearn.fully_connected(g, len(char_idx), activation='softmax')
g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                       learning_rate=0.001)

m = tflearn.SequenceGenerator(g, dictionary=char_idx,
                              seq_maxlen=maxlen,
                              clip_gradients=5.0,
                              checkpoint_path='model_football_names')

for i in range(40):
    seed = "Michael Menz"
    m.fit(X, Y, validation_set=0.1, batch_size=1024,
          n_epoch=5, run_id='football_names')
    print("-- TESTING...")
    print("-- Test with temperature of 1.2 --")
    print(m.generate(30, temperature=1.2, seq_seed=seed).encode('utf-8'))
    print("-- Test with temperature of 1.0 --")
    print(m.generate(30, temperature=1.0, seq_seed=seed).encode('utf-8'))
    print("-- Test with temperature of 0.5 --")
    print(m.generate(30, temperature=0.5, seq_seed=seed).encode('utf-8'))

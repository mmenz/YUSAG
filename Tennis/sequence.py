
import tflearn
import csv
from random import shuffle, seed, random, choice

idx = {
    "_": 0,
    "S": 1,
    "R": 2,
    "A": 3,
    "D": 4,
    ";": 5,
    ".": 6,
    "/": 7
}

labels = {
    "1": [1, 0],
    "2": [0, 1]
}

PAD_LENGTH = 100
SPLIT = 0.9

xtrain = []
ytrain = []

xtest = []
ytest = []
test_ids = []
games = {}

with open('tennis_archive_matches_ATP.csv', 'rU') as infile:
    reader = csv.DictReader(infile)
    for line in reader:
        match_id = line['pbp_id']
        games[match_id] = line['pbp'][:PAD_LENGTH]
        r = random()
        if not line['winner']:
            continue
        pbp = line['pbp']
        winner = labels[line['winner']]
        indices = [idx[p] for p in pbp]
        for k in range(1, min(len(indices), PAD_LENGTH)):
            if r < SPLIT:
                xtrain.append(indices[:k] + [0] * (PAD_LENGTH - k))
                ytrain.append(winner)
            else:
                xtest.append(indices[:k] + [0] * (PAD_LENGTH - k))
                ytest.append(line['winner'])
                test_ids.append(match_id)

# Build neural network
net = tflearn.input_data(shape=[None, PAD_LENGTH])
net = tflearn.embedding(net, len(idx), 1)
net = tflearn.lstm(net, 128, activation='relu')
net = tflearn.fully_connected(net, 2, activation='softmax')
net = tflearn.regression(net, optimizer='adam')

# train the model
TRAIN_SIZE = 50000
model = tflearn.DNN(net)
model.fit(xtrain[:TRAIN_SIZE], ytrain[:TRAIN_SIZE],
          n_epoch=1, batch_size=128, show_metric=True)

# evaluate model
correct = 0
for prediction, label in zip(model.predict(xtest), ytest):
    if prediction[0] > prediction[1] and label == '1':
        correct += 1
    elif prediction[0] < prediction[1] and label == '2':
        correct += 1

print(float(correct) / len(ytest))

# look at a match
import matplotlib.pyplot as plt

predictions = model.predict(xtest)
while 1:
    match_id = choice(test_ids)
    probs = []
    for i, an_id in enumerate(test_ids):
        if an_id == match_id:
            probs.append(predictions[i][0])
    plt.plot(probs)
    for i, prob in enumerate(probs):
        plt.text(x=i, y=prob, s=games[match_id][i])
    plt.title(match_id)
    plt.show()
    r = raw_input()
    if r == 'q':
        exit()

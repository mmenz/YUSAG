import csv
import argparse
from sklearn import ensemble
from sklearn import neural_network
import numpy as np
import pickle
import fileinput
import json
from collections import OrderedDict
import os


def get_filename(game_id, names_file):
    with open(names_file) as infile:
        for line in infile:
            if game_id in line:
                return line


def compute_seconds_remaining(row):
    period = int(row['period'])
    hours, minutes, seconds = row['remaining_time'].split(':')
    seconds = int(minutes) * 60 + int(seconds) + (4 - period) * 720
    return seconds


def make_lines_lookup_table(lines_file):
    lookup_table = {}
    with open(lines_file) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            key = (row['date'], row['team'])
            if row['line'] != '-':
                lookup_table[key] = float(row['line'])
    return lookup_table


def make_home_team_lookup_table(names_file):
    lookup_table = {}
    with open(names_file) as infile:
        for line in infile:
            year, day, month, game_id, rest = line.split('-')
            home = rest.split('.')[0].split('@')[1]
            lookup_table[game_id] = home
    return lookup_table


def make_result_lookup_table(train_file):
    lookup_table = {}
    current_game_id = None
    current_diff = 0
    with open(train_file) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            game_id = row['game_id'].strip("'").strip('=').strip('"')
            if current_game_id and current_game_id != game_id:
                lookup_table[current_game_id] = current_diff
            current_game_id = game_id
            current_diff = int(row['home_score']) - int(row['away_score'])
    lookup_table[current_game_id] = current_diff
    return lookup_table


def validate(team, play):
    if not team:
        return False
    if play not in ['shot', 'rebound', 'turnover', 'free throw']:
        return False
    return True


def decide_possesion(home_team, row):
    play = row['event_type']
    extended_play = row['type']
    team = row['team']
    # on shots or turnovers, possession goes to other team
    last_free_throws = ['Free Throw Technical', 'Free Throw 2 of 2',
                        'Free Throw 3 of 3', 'Free Throw 1 of 1']
    if play in ['shot', 'turnover'] or extended_play in last_free_throws:
        return 0 if home_team == team else 1
    # on rebounds, possession goes to current team
    else:
        return 1 if home_team == team else 0


def extract_features(train_file, lines_file, names_file):
    lines_lookup_table = make_lines_lookup_table(lines_file)
    home_lookup_table = make_home_team_lookup_table(names_file)
    result_lookup_table = make_result_lookup_table(train_file)
    for_output = OrderedDict()
    features = []
    labels = []
    with open(train_file) as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader):
            team = row['team']
            play = row['event_type']
            date = row['date']
            if not validate(team, play):
                continue
            year, month, day = date.split('-')
            date = month + '/' + day + '/' + year[2:]
            game_id = row['game_id'].strip("'").strip('=').strip('"')
            home_team = home_lookup_table[game_id]
            result = result_lookup_table[game_id]
            point_difference = int(row['home_score']) - int(row['away_score'])
            time_remaining = compute_seconds_remaining(row)
            possession = decide_possesion(home_team, row)
            total_points_scored = int(row['home_score']) \
                + int(row['away_score'])
            line = lines_lookup_table[(date, home_team)]
            features.append([point_difference, time_remaining,
                             line, total_points_scored])
            labels.append(1 if result > 0 else 0)
            for_output_info = [time_remaining, row['description']]
            if game_id in for_output:
                for_output[game_id].append(for_output_info)
            else:
                for_output[game_id] = [for_output_info]
    return np.array(features), np.array(labels), for_output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str,
                        default="[10-20-2013]-[06-30-2014]-combined-stats.csv")
    parser.add_argument('--lines_file', type=str,
                        default="lines.csv")
    parser.add_argument('--names_file', type=str,
                        default="names.txt")
    parser.add_argument('--model_file', type=str, default="model.mdl")
    parser.add_argument('--evaluate', action="store_true")
    parser.add_argument('--console', action="store_true")
    parser.add_argument('--output_directory', type=str, default="output/")
    args = parser.parse_args()

    features, labels, for_output = extract_features(args.input_file,
                                                    args.lines_file,
                                                    args.names_file)

    if args.console:
        # CURRENTLY NOT WORKING
        with open(args.model_file) as serialized:
            model = pickle.loads(serialized.read())
        while 1:
            time = input("time: ")
            point_diff = input("point differential: ")
            line = input("line: ")
            possession = input("possession: ")
            prediction = model.predict([[point_diff, time, possession, line]])
            print(prediction)
    elif args.evaluate:
        with open(args.model_file) as serialized:
            model = pickle.loads(serialized.read())
        predictions = model.predict(features).tolist()
        features = features.tolist()
        game_metadata = {}
        for game_id in for_output:
            game_metadata[game_id] = {
                "filename": get_filename(game_id, args.names_file)
            }
            last = 0
            game_output = []
            for i, (tr, desc) in enumerate(for_output[game_id]):
                current = predictions.pop(0)
                cfeatures = features.pop(0)
                game_output.append({"time": 2880 - tr + i / 10000.,
                                    "desc": desc,
                                    "value": current,
                                    "id": "prediction"})
                game_output.append({"time": 2880 - tr + i / 10000.,
                                    "desc": desc,
                                    "value": cfeatures[0],
                                    "id": "point differential"})
                last = current
            outpath = os.path.join(args.output_directory, game_id + '.json')
            with open(outpath, 'w') as outf:
                outf.write(json.dumps(game_output))
        outpath = os.path.join(args.output_directory, "metadata.json")
        with open(outpath, "w") as outf:
            outf.write(json.dumps(game_metadata))
        assert not predictions
        assert not features
    else:
        classifier = neural_network.MLPClassifier(hidden_layer_sizes=(10, 10,))
        classifier.fit(features, labels)
        print(classifier.score(features, labels))
        with open(args.model_file, 'w') as serialized:
            serialized.write(pickle.dumps(classifier))

import pandas as pd
import itertools
import collections
import csv

lineups = pd.read_csv('lineups.csv')


def hash_lineup(row):
    players = []
    for i in range(0, 5):
        players.append(row[1]['Yale P%d' % (i + 1)])
    return tuple(sorted(players))


def time_difference(row1, row2):
    row1min, row1sec = row1[1]['Time'].split(':')
    row2min, row2sec = row2[1]['Time'].split(':')
    if row2[1]['Date'] != row1[1]['Date']:
        return int(row1min) * 60 + int(row1sec)
    elif int(row1[1]['Half']) != int(row2[1]['Half']):
        return int(row1min) * 60 + int(row1sec) \
            - (int(row2min) * 60 + int(row2sec)) + \
            1200 if row2[1]['Half'] == 2 else 300
        # 1200 for a normal half, 300 for OT
    else:
        return (int(row1min) * 60 + int(row1sec)) - \
            (int(row2min) * 60 + int(row2sec))


class LineupStatistics:

    def add_lineup(self, first_row, last_row):
        time_played = time_difference(first_row, last_row)
        if time_played < 0:
            print('shit')
            print(first_row, last_row)
        if time_played == 0:
            return
        points_scored = last_row[1]['Yale Score'] \
            - first_row[1]['Yale Score']
        points_allowed = last_row[1]['Opponent Score'] \
            - first_row[1]['Opponent Score']
        full_lineup = hash_lineup(first_row)
        # look at 1 to 5 man lineups
        for r in range(1, 6):
            sub_lineups = itertools.combinations(full_lineup, r)
            for sub_lineup in sub_lineups:
                self.time_played[sub_lineup] += time_played / 60.0
                self.points_scored[sub_lineup] += points_scored
                self.points_allowed[sub_lineup] += points_allowed

    def tofile(self, outname):
        fieldnames = ['Lineup', 'Size',
                      'Minutes Played',
                      'PF', 'PA',
                      'PFPM', 'PAPM', 'PDPM']
        with open(outname, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(fieldnames)
            for key in self.time_played:
                row = []
                row.append(key)
                row.append(len(key))
                minutes = self.time_played[key]
                row.append(minutes)
                row.append(self.points_scored[key])
                row.append(self.points_allowed[key])
                row.append(self.points_scored[key] / minutes)
                row.append(self.points_allowed[key] / minutes)
                row.append(row[-2] - row[-1])
                writer.writerow(row)

    def __init__(self):
        self.time_played = collections.defaultdict(float)
        self.points_scored = collections.defaultdict(float)
        self.points_allowed = collections.defaultdict(float)

first_hash = None
first_row = None
first_date = None
lineup_stats = LineupStatistics()
last_row = None
for row in lineups.iterrows():
    row_hash = hash_lineup(row)
    if not first_row:
        first_row = row
        first_hash = row_hash
        first_date = row[1]['Date']
    elif row[1]['Date'] != first_date:
        last_row[1]['Time'] = '00:00'
        lineup_stats.add_lineup(first_row, last_row)
        first_row = row
        first_hash = row_hash
        first_date = row[1]['Date']
    elif row_hash != first_hash:
        lineup_stats.add_lineup(first_row, row)
        first_row = row
        first_hash = row_hash
        first_date = row[1]['Date']
    last_row = row

print(len(lineup_stats.time_played))
lineup_stats.tofile('lineup_stats.csv')

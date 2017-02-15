from pandas import read_html
from numpy import isnan, nan
import requests
import re
import csv


def check_valid_time(time):
    return re.match('[0-9][0-9]:[0-9][0-9]', time) is not None


def extract_player(event):
    matches = re.findall('[A-Z]*,[A-Z]*', event)
    if len(matches) == 0 or 'TEAM' in event or 'TIMEOUT' in event:
        return None
    return matches[0]


class Game:

    def add_row(self, time, yale_event, score, opp_event, yale_first):

        # only add a row if the time is valid
        if not check_valid_time(time):
            # if the time is invalid and rows have been added, then switch
            # to second half
            if time == '2nd  Half':
                self.half = 2
                self.lineup = []
            elif time.endswith('OT'):
                self.half += 1
                self.lineup = []
            return

        row = dict(zip(self.column_names,
                       ['N/A' for column_name in self.column_names]))
        # put in known values
        row['Date'] = self.date
        row['Opponent'] = self.opponent
        row['Half'] = self.half
        row['Time'] = time

        # only one team has an event
        if type(yale_event) == float:
            row['Team'] = self.opponent
            row['Event'] = opp_event
        else:
            row['Team'] = 'Yale'
            row['Event'] = yale_event
            player = extract_player(yale_event)
            if player:
                # if a player enters the game, put him in the lineup
                if 'enters the game' in yale_event:
                    if player not in self.lineup:
                        self.lineup.append(player)
                # if a player did not just enter the game, but is not in the
                # lineup put him in previous rows
                if player not in self.lineup:
                    self.lineup.append(player)
                    self.backfill(player)
                # if a player goes to the bench, take him out of the lineup
                if 'goes to the bench' in yale_event:
                    self.lineup.remove(player)
                # otherwise move him to the front of the lineup
                else:
                    self.lineup.remove(player)
                    self.lineup.insert(0, player)

        # update the current score if applicable
        if score != '-' and type(score) != float:
            if yale_first:
                self.yale_score, self.opp_score = score.split('-')
            else:
                self.opp_score, self.yale_score = score.split('-')
        row['Yale Score'] = self.yale_score
        row['Opponent Score'] = self.opp_score

        # put in current players
        key = 'Yale P%d'
        for i, player in enumerate(self.lineup):
            if i == 5:
                break
            row[key % (i + 1)] = player

        self.rows.append(row)

    def backfill(self, player):
        for row in reversed(self.rows):
            key = 'Yale P%d'
            did_add = False
            for i in range(5):
                if row[key % (i + 1)] == player:
                    break
                elif row[key % (i + 1)] == 'N/A':
                    did_add = True
                    row[key % (i + 1)] = player
                    break
            if not did_add:
                break

    def tofile(self, fname):
        with open(fname, 'w') as outfile:
            writer = csv.DictWriter(outfile, self.column_names)
            writer.writeheader()
            for row in self.rows:
                writer.writerow(row)

    def __init__(self, url):
        self.column_names = ['Date', 'Opponent', 'Half', 'Time',
                             'Yale P1', 'Yale P2', 'Yale P3', 'Yale P4',
                             'Yale P5', 'Yale Score', 'Opponent Score', 'Team',
                             'Event']
        self.yale_score = 0
        self.opp_score = 0
        self.half = 1
        self.lineup = []
        self.rows = []

        date = re.search('boxscores/([0-9]*)', url)
        self.date = date.group(1)

        try:
            tables = read_html(url)
        except ValueError:
            return

        final = tables[0]
        team1 = ' '.join(final[0].tolist()[0].split(' ')[:-1]).strip()
        team2 = ' '.join(final[1].tolist()[0].split(' ')[:-1]).strip()
        if team1 == 'Yale':
            self.opponent = team2
        else:
            self.opponent = team1

        play_by_play = tables[2]
        times = play_by_play[0].tolist()[3:]
        team1_events = play_by_play[1].tolist()
        scores = play_by_play[2].tolist()[3:]
        team2_events = play_by_play[3].tolist()

        if team1_events[2] == "Yale":
            yale_events = team1_events[3:]
            opp_events = team2_events[3:]
            yale_first = True
        else:
            yale_events = team2_events[3:]
            opp_events = team1_events[3:]
            yale_first = False

        while times:
            self.add_row(times.pop(0),
                         yale_events.pop(0),
                         scores.pop(0),
                         opp_events.pop(0),
                         yale_first)


class GameSet:

    def add_game(self, url):
        if url in self.urls:
            return
        self.urls.append(url)
        game = Game(url)
        if not game.rows:
            self.over = True
            return
        self.columns = game.column_names
        self.rows.extend(game.rows)

    def tofile(self, fname):
        with open(fname, 'w') as outfile:
            writer = csv.DictWriter(outfile, self.columns)
            writer.writeheader()
            for row in self.rows:
                writer.writerow(row)

    def __init__(self):
        self.columns = []
        self.rows = []
        self.urls = []
        self.over = False

if __name__ == '__main__':
    base_url = "http://www.yalebulldogs.com/"
    schedule_url = base_url + "sports/m-baskbl/2016-17/schedule"

    response = requests.get(schedule_url)
    html = response.text
    boxscore_urls = re.findall("sports/\S*/boxscores/\S*.xml", html)

    gameset = GameSet()
    for extension in boxscore_urls:
        url = base_url + extension + "?view=plays"
        gameset.add_game(url)
        if gameset.over:
            break
    gameset.tofile("lineups.csv")

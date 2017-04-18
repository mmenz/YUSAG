from pandas import read_html
import requests
import pickle
import re

with open('no_possession_model.mdl') as serialized:
    model = pickle.loads(serialized.read())


def compute_seconds_remaining(period, time):
    minutes, seconds = time.split(':')
    if period == 5:
        return int(minutes) * 60 + int(seconds)
    return int(minutes) * 60 + int(seconds) + (4 - period) * 720


def compute_point_features(score):
    away, home = map(int, score.split(' - '))
    return home - away, home + away


def parse_quarter_table(quarter, period, game_output, line):
    data_points = []
    for key in quarter['SCORE']:
        score = quarter['SCORE'][key]
        time = quarter['time'][key]
        seconds = compute_seconds_remaining(period, time)
        # print(period, seconds, time, quarter['PLAY'][key])
        diff, total = compute_point_features(score)
        data_points.append([diff, seconds, line, total])
        if period == 5:
            game_output.append({"time": 3120 - seconds -
                                len(game_output) / 10000.,
                                "desc": score + ', ' + quarter['PLAY'][key],
                                "id": "prediction"})
            print(game_output[-1])
        else:
            game_output.append({"time": 2880 - seconds -
                                len(game_output) / 10000.,
                                "desc": score + ', ' + quarter['PLAY'][key],
                                "id": "prediction"})
    predictions = model.predict_proba(data_points)
    for i, p in enumerate(predictions):
        game_output[-len(data_points) + i]["Win Percentage"] = p[1]


def make_data_for_game_id(game_id, line, over=False):
    url = "http://www.espn.com/nba/playbyplay?gameId=%s" % (game_id)
    game_output = []
    tables = read_html(url)
    # ignore first table
    if over:
        quarters = tables[1:]
    else:
        quarters = tables[1:][::-1]
    quarter_count = 0
    for i, quarter in enumerate(quarters):
        try:
            parse_quarter_table(quarter.to_dict(), i + 1, game_output, line)
            quarter_count += 1
        except KeyError:
            print("was key error, continuing")
            continue
    return game_output, quarter_count > 4


def lookup_line_for_history(game_id):
    url = "http://www.espn.com/nba/playbyplay?gameId=%s" % (game_id)
    r = requests.get(url)
    html = r.text
    match = re.findall("<meta property=\"og:title\" content=\"(.*) - Play-By-Play - (.*) - ESPN\"/>", html)[0]
    teams, date = match
    description = teams + ' on ' + date
    team1, team2 = teams.split(' vs. ')
    month, day, year = date.split()
    months = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12"
    }
    date_num = year + months[month] + day[:-1]
    url = "http://sportsdatabase.com/nba/query?output=json&sdql=line%2Cteam%40date%3D" + date_num
    r = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    lines, teams = re.findall('\[.*\]', r.text)[-2:]
    line = 0
    for i, team in enumerate(eval(teams)):
        if team2 == team:
            line = float(eval(lines)[i])
            return line, description
    print("Line not found")
    return 0, description


if __name__ == '__main__':
    print(lookup_line_for_history("400950394"))

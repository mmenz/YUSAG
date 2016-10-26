from pandas import read_html
import pickle

with open('no_possession_model.mdl') as serialized:
    model = pickle.loads(serialized.read())


def compute_seconds_remaining(period, time):
    minutes, seconds = time.split(':')
    seconds = int(minutes) * 60 + int(seconds) + (4 - period) * 720
    return seconds


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
        game_output.append({"time": 2880 - seconds - len(game_output) / 10000.,
                            "desc": score + ', ' + quarter['PLAY'][key],
                            "id": "prediction"})
    predictions = model.predict_proba(data_points)
    for i, p in enumerate(predictions[0]):
        game_output[-len(data_points) + i]["Win Percentage"] = p


def make_data_for_game_id(game_id, line):
    url = "http://www.espn.com/nba/playbyplay?gameId=%s" % (game_id)
    game_output = []
    tables = read_html(url)
    # ignore first table
    quarters = tables[1:][::-1]
    for i, quarter in enumerate(quarters):
        parse_quarter_table(quarter.to_dict(), i + 1, game_output, line)
    return game_output


if __name__ == '__main__':
    print(make_data_for_game_id("400897115")[5])

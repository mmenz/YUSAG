from pandas import read_html
import pickle

with open('no_possession_model.mdl') as serialized:
    model = pickle.loads(serialized.read())


def compute_seconds_remaining(period, time):
    minutes, seconds = time.split(':')
    seconds = int(minutes) * 60 + int(seconds) + (4 - period) * 720
    return seconds


def compute_point_features(score):
    home, away = map(int, score.split(' - '))
    return home - away, home + away


def parse_quarter_table(quarter, period, game_output):
    for key in quarter['SCORE']:
        score = quarter['SCORE'][key]
        time = quarter['time'][key]
        seconds = compute_seconds_remaining(period, time)
        diff, total = compute_point_features(score)
        p = model.predict_proba([[diff, seconds, 0, total]])
        game_output.append({"time": 2880 - seconds - len(game_output) / 10000.,
                            "desc": quarter['PLAY'][key],
                            "value": p[1],
                            "id": "prediction"})


def make_data_for_game_id(game_id):
    url = "http://www.espn.com/nba/playbyplay?gameId=%s" % (game_id)
    game_output = []
    tables = read_html(url)
    # ignore first table
    quarters = tables[1:]
    for i, quarter in enumerate(quarters):
        parse_quarter_table(quarter.to_dict(), i + 1, game_output)
    return game_output


if __name__ == '__main__':
    print(make_data_for_game_id("400897115")[5])

import sys
from sklearn import neural_network
import pickle
import re
import requests
from urlparse import parse_qs
import os
import json
from flask import Flask, send_from_directory
from retrieve_game import make_data_for_game_id


app = Flask(__name__)

with open('no_possession_model.mdl') as serialized:
    model = pickle.loads(serialized.read())


def compute_seconds_remaining(timerem, qtr):
    period = int(qtr)
    minutes, seconds = timerem.split(':')
    seconds = int(minutes) * 60 + int(seconds) + (4 - period) * 720
    return seconds


def format_game(game_desc, game_id):
    # pre-game or post-game
    html = "<div>"
    html += "<a href=\"/%s\"> %s </a>" % (game_id, game_desc)
    if " at " in game_desc or '^' in game_desc:
        pass
    else:
        match = re.match(r"([a-zA-Z ]+)\s+(\d+)\s+\^?([a-zA-Z ]+)"
                         "\s+(\d+)\s+\((\d+:\d+) IN (\w)\w\w\)",
                         game_desc)
        team1, score1, team2, score2, timerem, qtr = \
            match.group(1, 2, 3, 4, 5, 6)
        total_seconds = compute_seconds_remaining(timerem, qtr)
        point_diff = int(score2) - int(score1)  # home team is second team
        total_points = int(score1) + int(score2)
        line = 0
        p = model.predict([[point_diff, total_seconds, line, total_points]])
        if p > 0:
            html += "<p> Live Projection: %s by %.02f </p>" % (team2, p)
        else:
            html += "<p> Live Projection: %s by %.02f </p>" % (team1, -p)
    html += "</div>"
    return html


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route("/<string:game_id>")
def display_game(game_id):
    data = make_data_for_game_id(game_id)
    html = open('plot.html').read()
    return html.replace("INSERT_DATA_HERE", json.dumps(data))


@app.route("/games")
def list_games_today():
    html = ''
    r = requests.get('http://www.espn.com/nba/bottomline/scores')
    qs = parse_qs(r.text)
    for i in range(1, 17):
        url_key = 'nba_s_url%d' % (i)
        desc_key = 'nba_s_left%d' % (i)

        if url_key not in qs:
            break

        game_id = qs[url_key][0].split('gameId=')[1]
        game_desc = qs[desc_key][0]

        html += format_game(game_desc, game_id)

    return html


if __name__ == "__main__":
    app.run()

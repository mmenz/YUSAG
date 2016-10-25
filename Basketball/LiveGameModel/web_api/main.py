import sys
from sklearn import neural_network
import pickle
import re
import requests
from urlparse import parse_qs
import os
import json
import time
from string import lower
from flask import (
    Flask,
    send_from_directory,
    make_response,
    request,
    current_app)
from retrieve_game import make_data_for_game_id
from functools import update_wrapper
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)

games_today = None
last_updated = 0
PAUSE = 10000  # 10000 seconds ~ 3 hours

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
    line = 0
    for game in games_today:
        if game['game_id'] == game_id:
            line = game['line']
            break
    data = make_data_for_game_id(game_id, line)
    return json.dumps({"data": data, "gameid": game_id})


def parse_odds(odds_text):
    found = re.findall("<span class=\"odds\"> [\+\-]\d+\.?\d?"
                       " \([\-\+]?\d+\) </span>",
                       odds_text)
    # if none found then line is even
    if not found:
        return 0
    # there should be two matches in found
    # the first one for the away team and the second for the home team
    # thus negate the line for the away team and average
    away = found[0]
    home = found[1]
    away_match = re.findall("([\+\-]\d+\.?\d?) \(.*", away)[0]
    home_match = re.findall("([\+\-]\d+\.?\d?) \(.*", home)[0]
    return (-float(away_match) + float(home_match)) / 2


def link_matches_game_desc(game_desc, link):
    team_words = link.split('nba/')[1].split('-odds')[0].split('-')
    game_desc = lower(game_desc)
    for team_word in team_words:
        if team_word not in game_desc:
            return False
    return True


@app.route("/games")
def list_games_today():
    html = ''
    if time.time() > last_updated + PAUSE:
        r = requests.get('http://www.espn.com/nba/bottomline/scores')
        odds = requests.get('http://www.oddsshark.com/nba/odds')
        qs = parse_qs(r.text)
        game_ids = []
        for i in range(1, 17):
            url_key = 'nba_s_url%d' % (i)
            desc_key = 'nba_s_left%d' % (i)

            if url_key not in qs:
                break

            game_id = qs[url_key][0].split('gameId=')[1]
            game_desc = qs[desc_key][0]
            game_ids.append({"gameid": game_id, "desc": game_desc})

        # get odds
        links = re.findall("\"/nba/[a-z\-]+\-odds\-[a-z]+\-\d+\-\d+-\d+",
                           odds.text)

        matching_links = []
        for game in game_ids:
            for link in links:
                if link_matches_game_desc(game['desc'], link):
                    link = 'http://www.oddsshark.com/' + link.strip('"')
                    matching_links.append(link)
                    break

        text = [requests.get(link).text for link in matching_links]
        odds = map(parse_odds, text)
        for game, line in zip(game_ids, odds):
            game['line'] = line

        games_today = game_ids
        # html += format_game(game_desc, game_id)

    return json.dumps(games_today)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import sys
from sklearn import neural_network
import cPickle
import re
import requests
from urlparse import parse_qs
import os
import ujson
import time
from string import lower
from flask import (
    Flask,
    send_from_directory,
    make_response,
    request,
    current_app
)
from retrieve_game import make_data_for_game_id
from functools import update_wrapper
from flask_cors import CORS, cross_origin
from helpers import infer_state


app = Flask(__name__)
CORS(app)

games_today = None
last_updated = 0
PAUSE = 10000  # 10000 seconds ~ 3 hours

cached_games = {}
GAMES_PAUSE = 30  # 30 seconds

with open('no_possession_model.mdl') as serialized:
    model = cPickle.load(serialized)


@app.route('/')
def main():
    return open('plot.html').read()


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route("/<string:game_id>")
def display_game(game_id):
    if game_id in cached_games:
        if time.time() - cached_games[game_id]["last_updated"] < PAUSE:
            return cached_games[game_id]["json"]
    line = 0
    for game in games_today:
        if game['gameid'] == game_id:
            line = game['line']
            break
    data = make_data_for_game_id(game_id, line)
    string = ujson.dumps({"data": data, "gameid": game_id})
    cached_games[game_id] = {"last_updated": time.time(), "json": string}
    return string


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
    global games_today, last_updated
    html = ''
    if time.time() > last_updated + GAMES_PAUSE:
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
            game_ids.append({"gameid": game_id,
                             "desc": game_desc,
                             "state": infer_state(game_desc)})

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
        last_updated = time.time()

    return ujson.dumps(games_today)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

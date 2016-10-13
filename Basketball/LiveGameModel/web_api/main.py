from flask import Flask
# import rpy2.robjects as robjects
from sklearn import neural_network
import pickle
import subprocess
import os


app = Flask(__name__)

with open('no_possession_model.mdl') as serialized:
    model = pickle.loads(serialized.read())
    

def format_game(team1, team2, score1, score2, timerem, qtr):
    team1 = clean(team1)
    team2 = clean(team2)
    html = "<div>"
    html += "<p>%s @ %s</p>" % (team1, team2)
    html += "<p> %d - %d " % (int(score1), int(score2))
    if 'NA' not in qtr:
        minutes = int(timerem) / 60
        seconds = int(timerem) % 60
        html += " Q%d %02d:%02d </p>" % (int(qtr), minutes, seconds)
    else:
        html += " FINAL </p>"
    if 'NA' not in qtr:
        total_seconds = int(timerem) + (4 - int(qtr)) * 720
        point_diff = int(score2) - int(score1)  # home team comes first
        total_points = int(score1) + int(score2)
        line = 0  # have to get line
        p = model.predict([[point_diff, total_seconds, line, total_points]])
        if p > 0:
            html += "<p> Live Projection: %s by %.02f </p>" % (team2, p)
        else:
            html += "<p> Live Projection: %s by %.02f </p>" % (team1, -p)
    html += "</div>"
    return html


def clean(string):
    string = string.strip('\n').strip('"').strip('^')
    return string


@app.route("/")
def main():
    html = ""
    output = subprocess.check_output(["Rscript", "--vanilla", "../get_live_scores.R"])
    for line in output.split('\n')[1:]:
        if not line:
            continue
        n, gameid, team1, team2, score1, score2, timerem, qtr = line.split(',')
        html += format_game(team1, team2, score1, score2, timerem, qtr)
    return html
    # for i, row in enumerate(scores.iter_row()):
    #     row = map(clean, row)
    #     game_id, team1, team2, score1, score2, timerem, qtr = row
    #     html += format_game(team1, team2, score1, score2,
    #                         timerem, qtr)
    # return html


if __name__ == "__main__":
    app.run(debug=True)

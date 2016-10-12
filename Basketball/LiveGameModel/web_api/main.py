from flask import Flask
import rpy2.robjects as robjects
from sklearn import neural_network
import pickle


app = Flask(__name__)

with open('no_possession_model.mdl') as serialized:
    model = pickle.loads(serialized.read())

RCode = """
# Parse for live scores: http://www.espn.com/nba/bottomline/scores

y <- readLines('http://www.espn.com/nba/bottomline/scores')
y <- strsplit(y,"&nba_s_left")
y <- y[[1]]
y <- gsub("%20", " ", y)
y <- y[grep("^[0-9]", y)]


gameid <- as.numeric(gsub(".*=([0-9][0-9]+).*", "\\\\1", y))
team1 <- gsub(".*=([A-z ]+[A-z]) [0-9a].*", "\\\\1", y)
team2 <- gsub("^[0-9]+=[A-z ]+ (at|[0-9]+) ([ ]*)([A-z ]+) [(0-9].*",
              "\\\\3", y)
score1 <- as.numeric(gsub(".*=[A-z ]+ ([0-9]+).*", "\\\\1", y))
score2 <- as.numeric(gsub(".* ([0-9]+) [(].*", "\\\\1", y))
minrem <- as.numeric(gsub(".*[(]([0-9]+):[0-9]+ I.*", "\\\\1", y))
secrem <- as.numeric(gsub(".*[(][0-9]+:([0-9]+) I.*", "\\\\1", y))
timerem <- minrem*60+secrem
qtr <- as.numeric(gsub(".*[(][0-9]+:[0-9]+ IN ([1-4]).*", "\\\\1", y))

z <- data.frame(gameid=gameid, team1=team1, team2=team2, score1=score1,
                score2=score2, timerem=timerem, qtr=qtr,
                stringsAsFactors=FALSE)

z
"""


def format_game(team1, team2, score1, score2, timerem, qtr):
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
    string = str(string).split(" ")[1].strip('\n').strip('"').strip('^')
    return string


@app.route("/")
def main():
    html = ""
    scores = robjects.r(RCode)
    for i, row in enumerate(scores.iter_row()):
        row = map(clean, row)
        game_id, team1, team2, score1, score2, timerem, qtr = row
        html += format_game(team1, team2, score1, score2,
                            timerem, qtr)
    return html


if __name__ == "__main__":
    app.run(debug=True)

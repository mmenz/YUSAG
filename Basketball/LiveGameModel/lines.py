import pandas as pd
import requests

abbrevs = {
    "Warriors": "GSW",
    "Thunder": "OKC",
    "Spurs": "SAS",
    "Rockets": "HOU",
    "Pacers": "IND",
    "Clippers": "LAC",
    "Hawks": "ATL",
    "Kings": "SAC",
    "Lakers": "LAL",
    "Mavericks": "DAL",
    "Nuggets": "DEN",
    "Pistons": "DET",
    "Seventysixers": "PHI",
    "Trailblazers": "POR",
    "Wizards": "WAS",
    "Bucks": "MIL",
    "Celtics": "BOS",
    "Heat": "MIA",
    "Jazz": "UTA",
    "Grizzlies": "MEM",
    "Magic": "ORL",
    "Raptors": "TOR",
    "Suns": "PHX",
    "Knicks": "NYK",
    "Nets": "BKN",
    "Cavaliers": "CLE",
    "Timberwolves": "MIN",
    "Pelicans": "NOP",
    "Bulls": "CHI",
    "Hornets": "CHA"
}

url = "http://sportsdatabase.com/nba/query?output=default&sdql=date%2C" \
      "+team%2C+line%40date+%3E+20130000&submit=++S+D+Q+L+%21++"

r = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
html = r.text
table = html.split('\n</tr></thead>\n<tr bgcolor=FFFFFF>')[1]
table = table.replace('\n</td>\n</tr>', '</tr>\n<tr >')
rows = table.split('</tr>\n<tr >')[:-2]

outpath = "lines.csv"
outfile = open(outpath, 'w')
outfile.write('date,team,line\n')


def get_line(entries):
    date = entries[0]
    date = date[4:6] + '/' + date[6:] + '/' + date[2:4]
    team = abbrevs[entries[1]]
    line = entries[2]
    if line == "None":
        line = "0"
    outfile.write('%s,%s,%s\n' % (date, team, line))

for row in rows:
    row = row.strip('\n<td valign=top bgcolor=ffffff>\n')
    row = row.strip('FFFFFF>\n<td valign=top bgcolor=ffffff>\n')
    row = row.strip('</td>\n')
    entries = row.split('</td>\n<td valign=top bgcolor=ffffff>')
    entries = map(lambda x: x.decode('ascii', 'ignore').strip(), entries)
    get_line(entries)

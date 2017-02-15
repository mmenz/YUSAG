import requests
from HTMLParser import HTMLParser


class PlayByPlayParser(HTMLParser):

    def handle_starttag()

url = "http://www.yalebulldogs.com/sports/m-baskbl/2016-17/boxscores/" \
      "20161117_a3rs.xml?view=plays"

r = requests.get(url)
html = r.text

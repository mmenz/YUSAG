import csv
import requests
import sys
import os
from bs4 import BeautifulSoup
import urllib
import re

SEARCH_URL = "http://www.nfl.com/players/search"
PLAYER_URL = "http://www.nfl.com/player/{name}/{pid}/draft"
CSV_FILE = "2014-NFL-Census-Shared.csv"
OUT_FILE = "2014-NFL-Census-Shared-With-Profile.csv"


def scrape_with_name(name):
    params = {
        "category": "name",
        "playerType": "current",
        "filter": name,
    }

    search_url = SEARCH_URL + '?' + urllib.urlencode(params)
    r = requests.get(search_url)
    match = re.search("/player/(\w+)/(\d+)/profile", r.text)
    name, pid = match.groups()

    player_url = PLAYER_URL.format(name=name, pid=pid)
    r = requests.get(player_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    paras = soup.find_all("p")
    for para in paras:
        if para.strong:
            if "Pick" in para.strong.text:
                return para.text[len(para.strong.text):].strip()
    return ""


if __name__ == '__main__':
    with open(CSV_FILE) as infile, open(OUT_FILE, 'w') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, reader.fieldnames + ['Profile'])
        writer.writeheader()

        for i, line in enumerate(reader):
            name = line["Name"]
            print i, name
            # change from Menz, Michael to Michael Menz
            name = ' '.join(name.split(',')[::-1]).strip()
            try:
                profile = scrape_with_name(name)
            except:
                continue
            # remove paragraphs breaks
            line['Profile'] = ' '.join(profile.encode("utf8").split())
            if len(profile) > 0:
                writer.writerow(line)

import csv
import requests
import sys
import os
from bs4 import BeautifulSoup

HTML_FOLDER = "html"
CSV_FILE = "profiles.csv"
BASE_URL = "http://www.nfl.com/draft/2017/profiles?id={pid}"
FIELDNAMES = ["Name", "Position", "Strengths", "Weaknesses",
              "Draft Projection", "NFL Comparison", "Bottom Line"]


def retrieve_name(soup):
    candidates = soup.find_all("h2")
    name = candidates[0].text
    return name.strip()


def retrieve_position(soup):
    candidates = soup.find_all("h3")
    position = candidates[0]
    return position.a.text.strip()


def retrieve_articles(soup):
    articles = soup.find_all("article", class_="")
    for article in articles:
        article_name = article.h4.text.strip()
        if article_name not in FIELDNAMES:
            continue
        article_text = article.text.strip()[len(article_name):]
        yield article_name, article_text


if sys.argv[1] == '-d':
    for k in range(2557834, 2558844 + 1):
        print(k)
        url = BASE_URL.format(pid=k)
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            continue
        fpath = os.path.join(HTML_FOLDER, "%d.html" % (k))
        with open(fpath, 'w') as outfile:
            outfile.write(r.text.encode('utf8'))


if sys.argv[1] == '-s':
    fnames = os.listdir(HTML_FOLDER)
    fpaths = [os.path.join(HTML_FOLDER, name) for name in fnames]

    writer = csv.DictWriter(open(CSV_FILE, "w"), FIELDNAMES)
    writer.writeheader()

    for path in fpaths:
        print(path)
        with open(path) as infile:
            row_dict = {}
            soup = BeautifulSoup(infile.read(), "html.parser")
            row_dict["Name"] = retrieve_name(soup)
            row_dict["Position"] = retrieve_position(soup)
            for key, value in retrieve_articles(soup):
                row_dict[key] = value.encode("utf8")
            if row_dict["Name"]:
                writer.writerow(row_dict)

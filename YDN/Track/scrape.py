import requests
import ujson
from bs4 import BeautifulSoup

filename1 = "track_april16.html"
filename2 = "indoor.html"
html = open(filename1).read() + open(filename2).read()

events = ['100m', '200m', '400m', '800m', '1,500m', '5,000m', '10,000m']
events += ['60m', '500m', '1,000m', '1 Mile', '3,000m', '5,000m']

# get names of athletes
soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all(class_="pLinks")
athletes = {}
for link in links:
    href = str(link['href'])
    text = link.text
    if 'athletes' in href:
        athletes[text] = {'url': href, 'races': [], 'gender': ''}

# for each athlete scrape results
for i, name in enumerate(athletes):
    print(i, name)
    href = athletes[name]['url']
    ra = requests.get(href)
    htmla = ra.text
    if "Men's" in htmla:
        athletes[name]['gender'] = 'm'
    if "Women's" in htmla:
        # assert athletes[name]['gender'] == ''
        athletes[name]['gender'] = 'f'
    # assert athletes[name]['gender'] != ''
    soupa = BeautifulSoup(htmla, 'html.parser')
    for tr in soupa.find_all('tr'):
        tds = tr.find_all('td')
        # filter out irrelevant rows
        if len(tds) != 5:
            continue
        date = tds[0].text.strip()
        # only take results from 2017
        year = date.split('/')[-1]
        if year == '17' or year == '16':
            event = tds[2].text.strip()
            # ignore events that are not solo races
            if event not in events:
                continue
            race_type = tds[3].text.strip()
            # ignore races that are prelims
            if race_type == 'P':
                continue
            time = tds[4].text.strip()
            athletes[name]['races'].append((event, time))

print(athletes)
with open('athletes.json', 'w') as outfile:
    ujson.dump(athletes, outfile)

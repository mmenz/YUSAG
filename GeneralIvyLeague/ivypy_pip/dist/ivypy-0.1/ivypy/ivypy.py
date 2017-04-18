import requests
from pandas import read_html
from urllib2 import HTTPError

BASE_URL = "http://www.ivyleaguesports.com/sports/{SPORT}/{ENDPOINT}"

SPORT_URLS = {
    "baseball": "bsb",
    "basketball": "{GENDER}bkb",
    "swimming": "{GENDER}swimdive",
    "squash": "{GENDER}squash",
    "wrestling": "wrest"
}

GENDERS = {
    "baseball": ["m"],
    "basketball": ["m", "w"],
    "swimming": ["m", "w"],
    "squash": ["m", "w"],
    "wrestling": ["m"]
}

ENDPOINTS = {
    "standings": "{YEAR}/standings",
    "game results": "{YEAR}/stats/html/confstat.htm"
}

FUNCTIONS = {
    "standings": lambda x: get_standings(x),
    "game results": lambda x: get_game_results(x)
}

IVYS = ['Yale', 'Harvard', 'Cornell',
        'Princeton', 'Brown', 'Columbia',
        'Penn', 'Dartmouth']


def retrieve(sport, endpoint, gender="m", year="current"):

    if sport not in SPORT_URLS:
        print("{sport} not in list of sports".format(sport=sport))
        return

    if endpoint not in ENDPOINTS:
        print("{endpoint} not in list of endpoints".format(endpoint=endpoint))
        return

    if gender not in GENDERS[sport]:
        print("Gender {gender} not appropo for {sport}".format(
              gender=gender, sport=sport))
        return

    if year == "current":
        # CHANGE THIS LATER
        year = "2016-17"
    elif type(year) == int:
        year = str(year) + "-" + str(year % 100 + 1)
    else:
        print("year argument must be \"current\" or an integer")

    url = BASE_URL.format(
            SPORT=SPORT_URLS[sport],
            ENDPOINT=ENDPOINTS[endpoint]).format(GENDER=gender,
                                                 YEAR=year)

    print(url)
    try:
        dataframes = read_html(url)
    except HTTPError:
        print "Failed to retrieve data from url: ", url
        exit(1)

    return FUNCTIONS[endpoint](dataframes[0])


def __get_name(row):
    for value in row:
        value = str(value).strip().strip("*")
        if value in IVYS:
            return value
    raise ValueError("No name found in row")


def get_standings(dataframe):
    table = dataframe.values.tolist()
    indices = {}
    start_index = 1
    # check if there are two types of standings
    if 'Ivy League' in table[0] and 'Overall' in table[0]:
        indices['ivy'] = table[1].index('Record')
        indices['overall'] = table[1].index('Record', indices['ivy'] + 1)
        start_index = 2
    else:
        indices['ivy'] = table[0].index('Record')

    standings = []
    for row in table[start_index:]:
        team_data = {}
        team_data["team"] = __get_name(row)
        for name, ix in indices.items():
            team_data[name] = row[ix]
        standings.append(team_data)
    return standings


def get_game_results(dataframe):
    table = dataframe.values.tolist()
    keys = table[0][:3]  # Data, Location, Result
    game_results = []
    for row in table[1:]:
        game = {}
        for key, value in zip(keys, row[:3]):
            game[key] = value
        game_results.append(game)
    return game_results

if __name__ == '__main__':
    result = retrieve("basketball", "standings", "m", 2013)
    for row in result: print(row)

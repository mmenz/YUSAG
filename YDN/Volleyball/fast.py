import requests
from pandas import read_html
import matplotlib.pyplot as plt
import numpy as np

IVY = ['Harvard', 'Penn', 'Cornell', 'Yale', 'Brown',
       'Dartmouth', 'Columbia', 'Princeton']

total_wins = {}

def make_url(year):
    nyear = year % 100 + 1
    return "http://www.ivyleague.com/sports/wvball/%d-%d/standings" % (year, nyear)

if __name__ == '__main__':
    for year in range(2012, 2017):
        url = make_url(year)
        table = read_html(url)[0]
        teams = table[1].values.tolist()[2:]
        records = table[3].values.tolist()[2:]
        for team, record in zip(teams, records):
            wins = int(record.split('-')[0])
            total_wins[team] = total_wins.get(team, 0) + wins

    print(total_wins)
    ind = np.arange(8)
    plt.bar(ind, total_wins.values())
    plt.xticks(ind + 1/2., total_wins.keys())
    plt.show()

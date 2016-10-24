import requests
from pandas import read_html
import re
import matplotlib.pyplot as plt
import json
from collections import defaultdict, OrderedDict
from sklearn.linear_model import LinearRegression
import numpy as np

IVY = ['Harvard', 'Penn', 'Cornell', 'Yale', 'Brown',
       'Dartmouth', 'Columbia', 'Princeton']


def make_url(year):
    nyear = year % 100 + 1
    return "http://www.ivyleague.com/sports/wvball/" \
           "%d-%d/stats/html/confstat.htm" % (year, nyear)


def parse_set(aset):
    if not aset:
        return None
    s1, s2 = aset.split('-')
    return (int(s1), int(s2))

ycount = 0
ytotal = 0

def parse_result(result, ivy_results):
    global ycount
    global ytotal
    teams_pattern = "([a-zA-Z\.\(\)\'\&\- ]+) (\d), ([a-zA-Z\.\(\)\'\&\- ]+) (\d)"
    sets_pattern = "\((\d+-\d+),(\d+-\d+),(\d+-\d+),?(\d+-\d+)?,?(\d+-\d+)?\)"
    pattern = teams_pattern + ' ' + sets_pattern
    m = re.match(pattern, result)
    team1, score1, team2, score2 = m.groups()[:4]
    score1, score2 = int(score1), int(score2)
    sets = map(parse_set, m.groups()[4:])
    # sets
    set_count = score1 + score2  # note that score1 is always 3
    # difference in points in first set
    point_diff = sets[0][0] - sets[0][1]
    if team1 in IVY and team2 in IVY:
        ivy_results.append((team1, point_diff, 'win', result))
        ivy_results.append((team2, point_diff, 'loss', result))
        if team1 == 'Yale' and point_diff > 0 or team2 == 'Yale' and point_diff < 0:
            ycount += 1
            ytotal += 1
        elif team1 == 'Yale' or team2 == 'Yale':
            ytotal += 1
    return point_diff, set_count


def make_plot(keys, **kwargs):
    counts = defaultdict(int)
    negcounts = defaultdict(int)
    for key in data.keys():
        for result in data[key]:
            if key in keys:
                counts[result] += 1
            else:
                negcounts[result] += 1
    xs = []
    wps = []
    sizes = []
    for i in range(0, 26):
        total = counts[i] + counts[-i] + negcounts[i] + negcounts[-i]
        if total > 0:
            xs.append(i)
            wps.append(counts[i] / float(total))
            sizes.append(2 * total)
    plt.scatter(xs, wps, s=sizes, **kwargs)
    plt.xlim(0, 20)
    plt.ylim(max(plt.ylim()[0], 0.0), min(plt.ylim()[1], 1.0))
    plt.xlabel("Point Differential in First Set")
    plt.title("Linear Regression of Win Percentage against First Set Margin")
    if len(keys) == 1:
        plt.ylabel("Percentage Won in %s Sets" % (keys[0]))
    else:
        plt.ylabel("Win Percentage")

    regress = LinearRegression()
    xs = np.array(xs).reshape(-1, 1)
    wps = np.array(wps)
    regress.fit(xs, wps, sizes)
    print(regress.score(xs, wps, sizes))
    plt.plot(xs, regress.predict(xs))
    return regress

if __name__ == '__main__':
    # data = {3: [], 4: [], 5: []}
    # ivy_results = []
    # for year in range(2012, 2017):
    #     url = make_url(year)
    #     table = read_html(url)[0]
    #     results = table[2].values.tolist()[1:]
    #
    #     for result in results:
    #         pd, sc = parse_result(result, ivy_results)
    #         data[sc].append(pd)
    #
    # with open('output.csv', 'w') as outfile:
    #     outfile.write(json.dumps({'data': data, 'ivy': ivy_results}))

    with open('output.csv') as infile:
        deserialized = json.loads(infile.read())
        data = deserialized['data']
        ivy = deserialized['ivy']

    # Percent of wins after winning first sets
    count = 0
    total = 0
    for key in data.keys():
        for result in data[key]:
            if result > 0:
                count += 1
            total += 1
    print count, total, count / float(total)

    accumulated_win_prob = {}
    counts = {}
    regress = make_plot(data.keys())
    for result in ivy:
        team, diff, end, full = result
        if end == 'win':
            if diff > 0:
                added_prob = 1 - regress.predict([[diff]])
            else:
                added_prob = regress.predict([[abs(diff)]])
        elif end == 'loss':
            if diff > 0:
                added_prob = regress.predict([[diff]]) - 1
            else:
                added_prob = -regress.predict([[abs(diff)]])
        if team in accumulated_win_prob:
            accumulated_win_prob[team] += added_prob
            counts[team] += 1
            if added_prob > 0.85:
                print(full, added_prob)
        else:
            accumulated_win_prob[team] = added_prob
            counts[team] = 1

    averages = {}
    for team in accumulated_win_prob:
        averages[team] = float(accumulated_win_prob[team] / counts[team])

    sorted_values = sorted(averages.values())
    sorted_keys = sorted(averages.keys(), key=lambda x: averages[x])

    plt.figure()
    ind = np.arange(8)
    plt.bar(ind, sorted_values, width=1.0, color=(
        '#b31b1b', '#00693e', '#59260B', '#9bddff', '#004785', '#ff8f00',
        '#A41034', '#0f4d92'

    ))
    plt.xticks(ind + 1/2., sorted_keys)
    plt.title("Performance Relative to Expectation by Team")
    plt.xlabel("")
    plt.ylabel("Average Win Probability Added")

    plt.show()


    #
    # # Histogram of results 1
    # bins = OrderedDict([('Win in 3', 0), ('Win in 4', 0), ('Win in 5', 0),
    #                     ('Lost in 5', 0), ('Lost in 4', 0)])
    #
    # for key in data.keys():
    #     for result in data[key]:
    #         if result > 0:
    #             binkey = 'Win in ' + key
    #         else:
    #             binkey = 'Lost in ' + key
    #         bins[binkey] += 1
    #
    #

    print(ycount, ytotal)

    # Histograms of results 2
    # plt.hist(data['3'], 10, normed=1, alpha=0.5)
    # plt.hist(data['4'], 10, normed=1, alpha=0.5)
    # plt.hist(data['5'], 10, normed=1, alpha=0.5)
    # plt.show()

    # Plot of win probabilities
    # plt.figure()
    # plt.title("Win Percentage vs. Margin of First Set Victory")
    #
    #
    # plt.figure()
    # plt.title("Probability of Sweep vs. Margin of First Set Victory")
    # make_plot(['3'], c='green')
    # plt.show()
    # colors = ['b', 'r', 'g']
    # for c, key in zip(colors, data.keys()):
    #     make_plot([key], c=c)
    # plt.show()

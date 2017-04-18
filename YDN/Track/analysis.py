import ujson
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import collections

athletes = ujson.load(open('athletes.json'))

events = ['100m', '200m', '400m', '800m', '1,500m', '5,000m', '10,000m']
events += ['60m', '500m', '1,000m', '1 Mile', '3,000m']

schools = {
    "Volker, Charles": "Princeton",
    "Vaughns, Vincent": "Yale",
    "Akosa, Carrington": "Princeton",
    "Alexandre, Marc-Andre": "Yale",
    "Wiseman, Jeff": "Penn",
    "Napolitano, Rob": "Columbia",
    "Hatler, Chris ": "Penn",
    "Randon, James": "Yale",
    "Thomas, Ryan": "Columbia",
    "Shearn, Brendan ": "Penn",
    "Thomas, Gabrielle": "Harvard",
    "Obeng-Akrofi, Akua": "Columbia",
    "Akins, Nia": "Penn",
    "Schlachtenhaufen, Helen": "Dartmouth",
    "Schmiede, Frances": "Yale",
    "Schudrowitz, Natalie": "Brown",
    "Pendergast, Judy": "Harvard",
    "Whiting, Cleo": "Penn"
}

school_colors = {
    "Princeton": "orange",
    "Yale": "blue",
    "Columbia": "lightblue",
    "Penn": "turquoise",
}


def length_of_event(event):
    if 'Mile' in event:
        return 1609
    else:
        event = ''.join([a for a in event if a.isdigit()])
        return float(event)


events = sorted(events, key=length_of_event)


def str2time(string):
    if ':' in string:
        minutes, seconds = string.split(':')
        return 60 * int(minutes) + float(seconds)
    return float(string)


# compute mean, variance for athletes
for athlete in athletes:
    races = athletes[athlete]['races']
    times = {}
    for event, time in races:
        if time == 'NT':
            continue
        if event in times:
            times[event].append(str2time(time))
        else:
            times[event] = [str2time(time)]
    dists = {}
    for event in times:
        mean = np.mean(times[event])
        variance = np.var(times[event])
        dists[event] = (mean, variance ** 0.5)
    athletes[athlete]['dists'] = dists

# print athletes['Chapey, Lauren']


def simulate(event, gender):
    results = []
    for athlete in athletes:
        # ignore of wrong gender
        if athletes[athlete]['gender'] != gender:
            continue
        # ignore if does not do event
        if event not in athletes[athlete]['dists']:
            continue
        mean, variance = athletes[athlete]['dists'][event]
        # ignore athletes who have only ran the race once
        if variance == 0:
            variance = mean / 40
        result = np.random.normal(mean, variance)
        results.append((athlete, result))
    results = sorted(results, key=lambda x: x[1])
    return results


def score_event(event, gender, sims=1000):
    scores = collections.defaultdict(float)
    values = [10, 8, 6, 5, 4, 3, 2, 1]
    for i in range(sims):
        results = simulate(event, gender)
        for k in range(min(len(values), len(results))):
            player = results[k][0]
            scores[player] += float(values[k]) / sims
    return scores


def make_charts_for_gender(gender):
    scores = [score_event(event, gender) for event in events]
    distances = [length_of_event(event) for event in events]

    # # make a chart by distance
    xs = distances
    ys = []
    labels = []
    for results in scores:
        ys.append(max(results.values()))
        for key in results:
            if results[key] == ys[-1]:
                labels.append(key)

    for i, event in enumerate(events):
        print "\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\"".format(event, ys[i], labels[i],
                                           gender, schools[labels[i]])

    fig, ax = plt.subplots()

    colors = ['red', 'green', 'orange', 'purple', 'brown', 'blue', 'gray',
              'yellow', 'beige', 'cyan', 'magenta', 'turquoise', 'lightgreen']

    width = 1.0

    locations = np.arange(len(xs))
    current_label = None
    current_color = None
    indices = []
    index = 0
    iterate_over = labels + ['dummy']
    bars = []
    matching_labels = []
    while iterate_over:
        if iterate_over[0] != current_label:
            if indices:
                bar = ax.bar(locations[indices[0]: indices[-1] + 1],
                             ys[indices[0]: indices[-1] + 1], width,
                             color=current_color, edgecolor='none')[0]
                bars.append(bar)
                matching_labels.append(current_label)
                indices = []
            current_color = colors.pop(0)
        current_label = iterate_over.pop(0)
        indices.append(index)
        index += 1

    ax.set_xticks(np.arange(len(xs)) + width / 2)
    ax.set_xticklabels(events)
    ax.set_xlim(0, len(events))
    ax.set_ylim(2, 12)
    ax.legend(bars, matching_labels)
    ax.set_ylabel("Average Score")
    ax.set_title("Highest Scoring Invidual Performers by Event")

    # plt.savefig(gender + "1.png")
    plt.show()

    # density plot
    if gender == 'm':
        main_athlete = 'Randon, James'
    else:
        main_athlete = 'Schmiede, Frances'

    # find best race for main athlete
    best_event = None
    best_index = 0
    best_score = 0
    for i, label in enumerate(labels):
        if label == main_athlete:
            score = ys[i]
            if score > best_score:
                best_score = score
                best_event = events[i]
                best_index = i
    print(best_event)

    # make a density plot of the results for top 5 in that event
    fig, ax = plt.subplots()
    results = scores[best_index]
    top_ten = sorted(results.keys(), key=lambda x: results[x], reverse=True)[:3]
    colors = ['blue', 'green', 'orange', 'purple', 'brown', 'red', 'gray',
              'yellow', 'beige', 'cyan', 'magenta', 'turquoise', 'lightgreen']
    maximum = 0
    minimum = 100000
    for i, athlete in enumerate(top_ten):
        mean, variance = athletes[athlete]['dists'][best_event]
        maximum = max(mean + 3 * variance**0.5, maximum)
        minimum = min(mean - 3 * variance**0.5, minimum)

    plots = []
    for i, athlete in enumerate(top_ten):
        mean, variance = athletes[athlete]['dists'][best_event]
        if variance == 0:
            variance = mean / (15 + 50 * random.random())
        x = np.linspace(minimum, maximum, 500)
        plots.append(
            ax.plot(x, mlab.normpdf(x, mean, variance**0.5), color=colors[i])[0]
        )
        ax.fill_between(x, 0, mlab.normpdf(x, mean, variance**0.5),
                        facecolor=colors[i], alpha=0.5)
        print athlete, mean, variance

    # compare to yale's athlete
    ymean, yvariance = athletes[top_ten[0]]['dists'][best_event]
    for i in range(1, len(top_ten)):
        mean, variance = athletes[top_ten[i]]['dists'][best_event]
        count = 0
        for k in range(10000):
            if np.random.normal(mean, variance) > np.random.normal(ymean, yvariance):
                count += 1
        print top_ten[i], count


    ax.set_xlim(minimum, maximum)
    ax.invert_xaxis()
    ax.set_xlabel("Seconds")
    ax.set_ylabel("Probability")
    ax.set_title("Distributions of Top Three Runners for %s" % (best_event))
    plt.legend(plots, top_ten)
    plt.show()
    #plt.savefig(gender + "2.png")

    # make the bubble chart
    # fig, ax = plt.subplots()
    #
    # # make data for scattering
    # special_labels = []
    # xs = []
    # ys = []
    # sizes = []
    # for athlete in athletes:
    #     if athletes[athlete]['gender'] != gender:
    #         continue
    #     top_three = []
    #     for results in scores:
    #         for key in results:
    #             if key == athlete:
    #                 top_three.append(results[key])
    #     if len(top_three) < 3:
    #         continue
    #     top_three = sorted(top_three, reverse=True)
    #     xs.append(top_three[0])
    #     ys.append(top_three[1])
    #     sizes.append(5 * sum(top_three))
    #     if athlete in labels and athlete not in special_labels:
    #         special_labels.append(athlete)
    #         ax.annotate(athlete, xy=(top_three[0], top_three[1]),
    #                     xytext=(-10, 10),
    #                     textcoords='offset points', ha='right', va='bottom',
    #                     bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
    #                     arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    # ax.scatter(xs, ys, s=sizes)
    # plt.show()


if __name__ == '__main__':
    make_charts_for_gender('f')
    make_charts_for_gender('m')

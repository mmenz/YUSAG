import csv
from collections import defaultdict

schedule_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

genders = {
    'A Hoops': 'M',
    'W Hoops': 'W',
    'B Hoops': 'M',
    'C Hoops': 'M',
    'M Volleyball': 'M',
    'W Volleyball': 'W',
    'M and W Squash': 'MW',
    'Water Polo': 'MW',
    'Indoor Soccer': 'MW',
    'Broomball': 'MW',
    'Bowling': 'MW',
    'Coed Soccer': 'MW',
    "Men's Soccer": 'M',
    "Women's Soccer": 'W',
    'Football': 'MW',
    'Volleyball': 'MW',
    'Tennis': 'MW',
    'Table Tennis': 'MW'
}

fname = "fall_2016.csv"
with open(fname) as infile:
    reader = csv.reader(infile)
    # fill in sports rows
    sports = reader.next()
    current = ''
    for i in range(len(sports)):
        if sports[i] == '':
            sports[i] = current
        else:
            current = sports[i]
    # get times
    times = reader.next()
    current_month = ''
    current_date = ''
    for line in reader:
        # fill in date
        if line[0] == '':
            line[0] = current_date

        # format date with month
        date = line[0]
        if len(date) < 3:  # date is only a number
            date = current_month + '. ' + date
        else:              # date includes a month
            current_month = date.split('.')[0]
        current_date = date

        # figure out when teams have games
        for i, entry in enumerate(line):
            # ignore first two entries
            if i < 2:
                continue
            elif entry == '':
                continue
            elif ' v ' not in entry:
                continue
            else:
                time = times[i].split(':')[0]
                sport = sports[i]
                team1, team2 = entry.split(' v ')
                schedule_map[team1][date][time].append(sport)
                schedule_map[team2][date][time].append(sport)

overlaps = defaultdict(lambda: defaultdict(int))
for team in schedule_map:
    for date in schedule_map[team]:
        for time in schedule_map[team][date]:
            counts = defaultdict(int)
            for game in schedule_map[team][date][time]:
                counts[genders[game]] += 1
            overlaps[team]['M'] += ((counts['M'] - 1) * counts['M']) / 2
            overlaps[team]['W'] += ((counts['W'] - 1) * counts['W']) / 2
            overlaps[team]['MW'] += ((counts['MW'] - 1) * counts['MW']) / 2 + \
                counts['M'] * counts['MW'] + counts['W'] * counts['MW']

for team in overlaps:
    print(team, overlaps[team])

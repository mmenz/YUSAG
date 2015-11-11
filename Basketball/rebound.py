# rebound.py

FILENAME = "[10-20-2013]-[06-30-2014]-combined-stats.csv"

def convert_to_dict(l1, l2):
	d = {}
	for i in range(len(l1)):
		if i >= len(l2):
			d[l1[i]] = ''
		else:
			d[l1[i]] = l2[i]
	return d

regular_counter = 0
post_counter = 0
regular_games = 0
post_games = 0

regular_opps = 0
post_opps = 0

games_read = []
with open(FILENAME) as infile:
	first_line = infile.readline().split(',')
	for line in infile:
		line = convert_to_dict(first_line, line.split(','))
		if line['data_set'] == '2013-2014 Regular Season':
			if not(line['game_id'] in games_read):
				games_read.append(line['game_id'])
				regular_games += 1
			if line['type'] == 'rebound offensive':
				regular_counter += 1
			if line['event_type'] == 'rebound':
				regular_opps += 1
		else:
			if not(line['game_id'] in games_read):
				games_read.append(line['game_id'])
				post_games += 1
			if line['type'] == 'rebound offensive':
				post_counter += 1
			if line['event_type'] == 'rebound':
				post_opps += 1

print regular_opps / float(regular_games), post_opps / float(post_games)
print regular_counter / float(regular_opps), post_counter / float(post_opps)
print regular_counter / float(regular_games), post_counter / float(post_games)
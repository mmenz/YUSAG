# homeAwayLookup.py

NAMESNAME = "names.txt"
names = open(NAMESNAME).readlines()

def lookup(game_id):
	for name in names:
		if game_id[2:-1] in name:
			at_index = name.index("@")
			home = name[at_index+1:at_index+4]
			away = name[at_index-3:at_index]
			return {'home': home, 'away': away}
			
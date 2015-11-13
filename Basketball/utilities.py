
def empty(row_entry):
	return row_entry == None or row_entry.strip() == ''

NAMESNAME = "names.txt"
names = open(NAMESNAME).readlines()

def lookup(game_id):
	" Look up home or away for NBAStuffer files"
	for name in names:
		if game_id[2:-1] in name:
			at_index = name.index("@")
			home = name[at_index+1:at_index+4]
			away = name[at_index-3:at_index]
			return {'home': home, 'away': away}
			

def colorsForTeam(team):
	" Returns the HEX color codes for the given team "
	{
		'ATL': ['#E03A3E', '#C3D600', '#FFFFFF', '#000000'],
		'BOS': ['#008348', '#000000', '#000000', '#FFD700','#C0C0C0'],
		# http://teamcolorcodes.com/category/nba-team-color-codes/
		# MORE TODO
	}

def nameOfTeam(team):
	" Returns the full name of a team given an abbreviation (i.e. PHI)"
	lookup = {
		"ATL" 	:	"Atlanta Hawks",
		"BKN"	:	"Brooklyn Nets",
		"BOS"	:	"Boston Celtics",
		"CHA"	:	"Charlotte Hornets",
		"CHI"	:	"Chicago Bulls",
		"CLE"	:	"Cleveland Cavaliers",
		"DAL"	:	"Dallas Mavericks",
		"DEN"	:	"Denver Nuggets",
		"DET"	:	"Detroit Pistons",
		"GS"	:	"Golden State Warriors",
		"HOU"	:	"Houston Rockets",
		"IND"	:	"Indiana Pacers",
		"LAC"	:	"Los Angeles Clippers",
		"LAL"	:	"Los Angeles Lakers",
		"MEM"	:	"Memphis Grizzlies",
		"MIA"	:	"Miami Heat",
		"MIL"	:	"Milwaukee Bucks",
		"MIN"	:	"Minnesota Timberwolves",
		"NOP"	:	"New Orleans Pelicans",
		"NYK"	:	"New York Knicks",
		"OKC"	:	"Oklahoma City Thunder",
		"ORL"	:	"Orlando Magic",
		"PHI"	:	"Philadelphia 76ers",
		"PHX"	:	"Phoenix Suns",
		"POR"	:	"Portland Trailblazers",
		"SAC"	:	"Sacramento Kings",
		"SA"	:	"San Antonio Spurs",
		"TOR"	:	"Toronto Raptors",
		"UTA"	:	"Utah Jazz",
		"WAS"	:	"Washington Wizards"
	}
	return lookup[team]
	
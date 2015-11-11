import csv

class PossessionTracker:
	def get_possession_number_for_row(self, row):
		if row['game_id'] != self.current_game:
			self.possession_number = 0
			self.current_game = row['game_id']
			for name in self.names:
				if row['game_id'][2:-1] in name:
					at_index = name.index("@")
					self.home = name[at_index+1:at_index+4]
					self.away = name[at_index-3:at_index]
			self.current = ''
		# deal with turnovers, made shots (in these cases we count the team commiting the turnover
		#	or taking the shot as having possession)
		if row['event_type'] == ['turnover', 'shot']:
			self.possession_number += 1
			# switch possesion
			if self.current == self.home:
				self.current = self.away
				return self.possession_number - 1, self.home
			else:
				self.current = self.home
				return self.possession_number - 1, self.away
		# deal with defenstive rebounds
		elif row['type'] == 'rebound defensive':
			self.possession_number += 1
			# switch possesion
			if self.current == self.home:
				self.current = self.away
			else:
				self.current = self.home
		elif row['event_type'] == 'jump ball':
			# if not at start of game
			if row['remaining_time'] != '00:12:00':
				winning_player = row['player']
				# if the away team wins the jump
				for header in ['a1', 'a2', 'a3', 'a4', 'a5']:
					if winning_player == row[header]:
						if self.current == self.home:
							self.current = self.away
							self.possession_number += 1
				# if the home team wins the jump
				for header in ['h1', 'h2', 'h3', 'h4', 'h5']:
					if winning_player == row[header]:
						if self.current == self.away:
							self.current = self.home
							self.possession_number += 1
			# jump ball to start the game
			else:
				winning_player = row['player']
				# if the away team wins the jump
				for header in ['a1', 'a2', 'a3', 'a4', 'a5']:
					if winning_player == row[header]:
						self.current = self.away
						self.possession_number += 1
						self.jump_winner = self.away
				# if the home team wins the jump
				for header in ['h1', 'h2', 'h3', 'h4', 'h5']:
					if winning_player == row[header]:
						self.current = self.home
						self.possession_number += 1
						self.jump_winner = self.home
		# deal with start of period
		elif row['event_type'] == 'start of period' and row['period'] != '1':
			if row['period'] == 2 or row['period'] == 3:
				if self.home == self.jump_winner:
					self.current = self.away
				else:
					self.current = self.home
			else: # for period 4
				if self.home == self.jump_winner:
					self.current = self.home
				else:
					self.current = self.away
			self.possession_number += 1
		return self.possession_number, self.current

	def __init__(self, names_file):
		# get all the filenames so we can look up home and away
		self.names = open(names_file).readlines()
		self.current_game = ''
		# the twos teams
		self.home = ''
		self.away = ''
		# who currently has the ball
		self.current = ''
		# who got the jump ball
		self.jump_winner = ''
		# possesion number
		self.possession_number = 0

if __name__ == '__main__':
	FILENAME = "[10-20-2013]-[06-30-2014]-combined-stats.csv"
	NAMESNAME = "names.txt"
	PT = PossessionTracker(NAMESNAME)
	pos_numbers = ['possession_number']
	currents = ['possession_team']
	with open(FILENAME) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			pos_number, current = PT.get_possession_number_for_row(row)
			pos_numbers.append(pos_number)
			currents.append(current)
	
	# now append the lines to the file
	NEWFILENAME = "[10-20-2013]-[06-30-2014]-combined-stats-with-possessions.csv"
	with open(FILENAME) as csvfile:
		with open(NEWFILENAME, 'w') as outfile:
			for i, line in enumerate(csvfile):
				line = line.strip().strip(',')
				outfile.write("%s,%s,%s\n"%(line, str(currents[i]), str(pos_numbers[i])))




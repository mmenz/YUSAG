# PostEventTracker.py

import csv
import homeAwayLookup as HAL
from utilities import empty

CAN_PLOT = True
try:
	import matplotlib.pyplot as plt
except:
	CAN_PLOT = False


class PostEventTracker:

	def __init__(self, csvfile, event_function, possession_evaluator, possessions_to_track):
		'''
		PostEventTracker class
			Given a csvfile with events, an event_function to evaluate whether a row contains a specific event, 
			a possession_evaluator to assign a numerical score to a possession, and a number of possessions to track
			after the specific event, PostEventTracker implements several functions to compare those possessions
			to the rest of the possessions in the game
		'''
		self.csvfile = csvfile
		self.ef = event_function
		self.pe = possession_evaluator
		self.ptt = possessions_to_track

	def scorePerPossessionFullGame(self):
		'''
		Returns a dictionary where keys are game_ids and values are dictionaries of the form:
			{
				'home':{'team': TEAM_NAME, 'spp': SCORE_PER_POSSESSION},
				'away':{'team': TEAM_NAME, 'spp': SCORE_PER_POSSESSION}
			}
		'''
		returnDict = {}

		# game variables
		current_game = None
		game_counter = -1
		total_scores = None

		# possession variables
		current_possession_number = -1
		totaler = None
		current_possession = []

		with open(self.csvfile) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:

				# check if we are looking at a new game
				if row['game_id'] != current_game:

					# evaluate the last possession from the previous game
					if current_possession_number != -1:
						totaler['total'] += self.pe(current_possession)
						totaler['possessions'] += 1

					# add the game to the return dictionary
					if current_game != None:
						avg_scores = {'home':{}, 'away':{}}
						avg_scores['home']['team'] = total_scores['home']['team']
						avg_scores['away']['team'] = total_scores['away']['team']
						avg_scores['home']['spp'] = total_scores['home']['total'] / float(total_scores['home']['possessions'])
						avg_scores['away']['spp'] = total_scores['away']['total'] / float(total_scores['away']['possessions'])

						returnDict[current_game] = avg_scores

					# reset vars for new game
					current_game = row['game_id']
					game_counter += 1
					total_scores = {
							'home': {'team': None, 'total': 0, 'possessions': 0},
							'away': {'team': None, 'total': 0, 'possessions': 0}
						}
					teams = HAL.lookup(current_game)
					total_scores['home']['team'] = teams['home']
					total_scores['away']['team'] = teams['away']
					current_possession_number = -1
					totaler = None
					current_possession = []

				# ignore lines without a possession
				if empty(row['possession_number']):
					continue

				# check if we have a new possession
				if row['possession_number'] != current_possession_number:
					# add score for the possession
					if current_possession_number != -1:
						totaler['total'] += self.pe(current_possession)
						totaler['possessions'] += 1

					# reset possession variables
					if total_scores['home']['team'] == row['possession_team']:
						totaler = total_scores['home']
					else:
						totaler = total_scores['away']
					current_possession_number = row['possession_number']
					current_possession = []

				current_possession.append(row)

		return returnDict

	def scorePerPossessionAfterEvent(self):
		'''
		Returns a dictionary where keys are game_ids and values are dictionaries of the form:
			{
				'home':{'team': TEAM_NAME, 'spp': SCORE_PER_POSSESSION},
				'away':{'team': TEAM_NAME, 'spp': SCORE_PER_POSSESSION}
			}
		'''
		returnDict = {}

		# game variables
		current_game = None
		game_counter = -1
		total_scores = None

		# possession variables
		current_possession_number = -1
		totaler = None
		current_possession = []
		event_counter = 0

		with open(self.csvfile) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:

				# check if we are looking at a new game
				if row['game_id'] != current_game:

					# evaluate the last possession from the previous game
					if current_possession_number != -1 and event_counter > 0:
						totaler['total'] += self.pe(current_possession)
						totaler['possessions'] += 1
						event_counter -= 1

					# add the game to the return dictionary
					if current_game != None:
						avg_scores = {'home':{}, 'away':{}}
						avg_scores['home']['team'] = total_scores['home']['team']
						avg_scores['away']['team'] = total_scores['away']['team']
						if total_scores['home']['possessions'] != 0:
							avg_scores['home']['spp'] = total_scores['home']['total'] / float(total_scores['home']['possessions'])
						else:
							avg_scores['home']['spp'] = None
						if total_scores['away']['possessions'] != 0:
							avg_scores['away']['spp'] = total_scores['away']['total'] / float(total_scores['away']['possessions'])
						else:
							avg_scores['away']['spp'] = None

						returnDict[current_game] = avg_scores

					# reset vars for new game
					current_game = row['game_id']
					game_counter += 1
					total_scores = {
							'home': {'team': None, 'total': 0, 'possessions': 0},
							'away': {'team': None, 'total': 0, 'possessions': 0}
						}
					teams = HAL.lookup(current_game)
					total_scores['home']['team'] = teams['home']
					total_scores['away']['team'] = teams['away']
					current_possession_number = -1
					totaler = None
					event_counter = 0
					current_possession = []

				# check if we have an event:
				if self.ef(row):
					event_counter = self.ptt

				# ignore lines without a possession
				if empty(row['possession_number']):
					continue

				# check if we have a new possession
				if row['possession_number'] != current_possession_number:
					# add score for the possession
					if current_possession_number != -1 and event_counter > 0:
						totaler['total'] += self.pe(current_possession)
						totaler['possessions'] += 1
						event_counter -= 1

					# reset possession variables
					if total_scores['home']['team'] == row['possession_team']:
						totaler = total_scores['home']
					else:
						totaler = total_scores['away']
					current_possession_number = row['possession_number']
					current_possession = []

				current_possession.append(row)

		return returnDict

	def plotDifferences(self):
		'''
		Show a scatter plot of games colored by team of the spp after events
			and in general
		'''
		if not CAN_PLOT:
			raise ImportError("Could not import matplotlib for plotting")
		fullgame = self.scorePerPossessionFullGame()
		afterevent = self.scorePerPossessionAfterEvent()
		xs = []
		ys = []
		teams = []
		for key in fullgame:
			game_spp = fullgame[key]
			after_spp = afterevent[key]
			if after_spp['home']['spp'] != None:
				xs.append( after_spp['home']['spp'] )
				ys.append( game_spp['home']['spp'] )
				teams.append( game_spp['home']['team'] )

		# make a colormap
		color_map = {}
		counter = 0
		colors = []
		for team in teams:
			if not team in color_map:
				color_map[team] = counter / 30.0
				counter += 1
			colors.append(color_map[team])

		plt.scatter(xs, ys, c=colors)
		plt.show()





# PostEventTracker.py

import csv
import homeAwayLookup as HAL
from utilities import empty

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

		current_game = None
		game_counter = -1
		home_team = None
		away_team = None

		current_possession_number = -1
		total_score = 0
		current_possession = []

		with open(self.csvfile) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:

				# check if we are looking at a new game
				if row['game_id'] != current_game:

					# evaluate the last possession from the previous game
					if current_possession_number != -1:
						total_score += self.pe(current_possession)

					# add the game to the return dictionary
					returnDict[current_game] = total_score / float(current_possession_number)

					# reset vars for new game
					current_game = row['game_id']
					game_counter += 1
					teams = HAL.lookup(current_game)
					home_team = teams['home']
					away_team = teams['away']
					current_possession_number = -1
					total_score = 0
					current_possession = []

				# ignore lines without a possession
				if empty(row['possession_number']):
					continue

				# check if we have a new possession
				if row['possession_number'] != current_possession_number:
					# add score for the possession
					if current_possession_number != -1:
						total_score += self.pe(current_possession)

					# reset possession variables
					current_possession_number = row['possession_number']
					current_possession = []

				current_possession.append(row)

		return returnDict


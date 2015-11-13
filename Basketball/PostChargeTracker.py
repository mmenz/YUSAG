# PostChargeTracker.py

import PostEventTracker as PET
from utilities import empty

csvfile = "[10-20-2013]-[06-30-2014]-combined-stats-with-possessions.csv"

def charge_function(row):
	return row['type'].strip() == "offensive charge foul"

def points_evaluator(rows):
	total_points = 0
	for row in rows:
		if not empty(row['points']):
			total_points += int(row['points'])
	return total_points

PCT = PET.PostEventTracker(csvfile, charge_function, points_evaluator, 6)
PCT.plotDifferences()
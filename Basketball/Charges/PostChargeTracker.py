# PostChargeTracker.py

import PostEventTracker as PET
from utilities.utilities import empty
from scipy.stats import ttest_ind

csvfile = "[10-20-2013]-[06-30-2014]-combined-stats-with-possessions.csv"

def charge_function(row):
	return row['type'].strip() == "offensive charge foul"

def points_evaluator(rows):
	total_points = 0
	for row in rows:
		if not empty(row['points']):
			total_points += int(row['points'])
	return total_points

PCT = PET.PostEventTracker(csvfile, charge_function, points_evaluator, 2)
aftercharge = PCT.scorePerPossessionAfterEvent()
baseline = PCT.scorePerPossessionFullGame()

away_after_charge_spps = []
away_spps = []
for game in aftercharge:
	if aftercharge[game]['away']['spp']['own'] != None:
		for i in range(aftercharge[game]['away']['spp']['own'][1]):
			print aftercharge[game]['away']['spp']['own'][0]
			away_after_charge_spps.append( aftercharge[game]['away']['spp']['own'][0] / float(aftercharge[game]['away']['spp']['own'][1]))
	away_spps.append( baseline[game]['away']['spp'][0] / float(baseline[game]['away']['spp'][1]))

print len(away_after_charge_spps)
print sum(away_after_charge_spps) / len(away_after_charge_spps)
print len(away_spps)
print sum(away_spps) / len(away_spps)

print ttest_ind(away_spps, away_after_charge_spps, equal_var=False)
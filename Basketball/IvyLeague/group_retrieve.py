import os

low = 400845000
high = 400846000

for i in range(low, high + 1):
    os.system('python retrieve_shot_data.py %d' % (i))

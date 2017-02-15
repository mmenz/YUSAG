from pandas import read_html
from collections import defaultdict
from string import lower
import requests

matches_url = "https://www.collegeswimming.com/team/376/results/?status=latest"

r = requests.get(matches_url)

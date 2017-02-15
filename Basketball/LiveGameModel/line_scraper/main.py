# import time
# from pandas import read_html
# from selenium import webdriver
#
# url = "https://sports.bovada.lv/basketball/nba"
# phantom_path = 'phantomjs-2.1.1-macosx/bin/phantomjs'
# alt_url = "http://www.google.com/"
#
# browser = webdriver.Firefox()
# while 1:
#     browser.get(url)
#     time.sleep(10)
#     html = browser.page_source
#     print(html)
#     tables = read_html(html)
#     print(tables)

import requests
from bs4 import BeautifulSoup
import json
import pprint

url = "https://www.betfair.com/sport/basketball"
matching_action = "register-market-data"

while 1:
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    config = None
    for script in scripts:
        if script.text.startswith('\nplatformC'):
            json_str = script.text.split('Config =')[1].split(';\n')[0].strip()
            config = json.loads(json_str)
            break
    if not config:
        continue
    instructions = config['page']['config']['instructions']
    markets = None
    for instruction in instructions:
        if instruction['action'] == matching_action:
            markets = instruction['arguments']
    print(markets)
    exit()

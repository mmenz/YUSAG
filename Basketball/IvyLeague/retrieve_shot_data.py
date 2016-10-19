import requests
import argparse
import re
import os
import csv
from HTMLParser import HTMLParser


def parse_description(description, made_or_missed):
    sentences = description.split('.')[:-1]
    # figure out who assisted
    if len(sentences) == 1:
        assisted_by = ''
    else:
        assisted_by = sentences[1][len(' Assisted by '):]
    # figure out who shot
    shooter, shot_type = sentences[0].split(made_or_missed)
    return {
        'assisted_by': assisted_by.strip(),
        'shooter': shooter.strip(),
        'shot_type': shot_type.strip()
    }


def parse_style(style):
    end = style.strip(';').split('left:')[1]
    left, top = end.split(';top:')
    return {
        'x': int(left.strip('%')) * 94 / 100,
        'y': int(top.strip('%')) * 50 / 100
    }


class Parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'li' and 'id' in attrs and attrs['id'][:4] == 'shot':
            description = attrs['data-text']
            style = attrs['style']
            made_or_missed = attrs['class']
            team = attrs['data-homeaway']
            period = attrs['data-period']
            data_point = {
                'team': team,
                'period': period,
                'result': made_or_missed
            }
            data_point.update(parse_style(style))
            data_point.update(parse_description(description, made_or_missed))
            self.output_list.append(data_point)

    def get_shots(self, html):
        self.output_list = []
        self.feed(html)
        return self.output_list


def get_url(gameid):
    url = "http://www.espn.com/mens-college-basketball/playbyplay?gameId="
    return url + str(gameid)


def get_data(gameid):
    url = get_url(gameid)
    r = requests.get(url)
    parser = Parser()
    return parser.get_shots(r.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('gameid', metavar='GAMEID', type=int)
    parser.add_argument('--output_directory', type=str, default="output/")
    args = parser.parse_args()

    # write data to csv
    filename = os.path.join(args.output_directory, str(args.gameid) + '.csv')
    with open(filename, 'w') as outfile:
        data = get_data(args.gameid)
        fieldnames = data[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

'''
 Created on Sat Feb 15 2020:14:58:22
 Created by Ratnadeep Bhattacharya
'''

import json
import sys


def get_data(filename):
    """load data for analysis"""
    data = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            data.append(json.loads(line))
        return data


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError as e:
        sys.stderr.write(str(e))
        sys.stderr.write("\n")
        sys.exit(-1)

    data = get_data(filename)
    for k, _ in data[0].items():
        for k1, v in data[0]['compose_backend'].items():
            print(k1, v)

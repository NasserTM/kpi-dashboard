#!/usr/bin/env python3

import argparse
import json
import requests
from requests import HTTPError
from urllib.parse import quote


def join_series(data):
    results = []
    if isinstance(data, dict):
        for key in iter(data.keys()):
            results += ['{}({})'.format(key, join_series(data[key]))]
    if isinstance(data, list):
        for item in data:
            results += [join_series(item)]
    if isinstance(data, bytes):
        return data.decode('utf-8')
    if isinstance(data, str):
        return data
    return ','.join(results)


def build_url(config):
    url = "{}/render/?from={}&format=json".format(config['graphite'],
                                                  config['time'])
    for target in config['targets']:
        url += "&target={}".format(quote(join_series(target)))
    return url


def _total_datapoints(datapoints):
    value = 0.0
    for (dp, ts) in datapoints:
        if dp:
            value += dp
    return value


def calculate_percentage(data):
    assert len(data) == 2, ('Two sets of datapoints are required to calculate '
                           'percentage')
    values = [_total_datapoints(target['datapoints']) for pos, target
              in enumerate(data)]
    if values[1] == 0.0:
        return 0.0
    return '{:.3f}%'.format(values[0] / values[1] * 100)


def calculate_count(data):
    assert len(data) == 1, ('One set of datapoints required when calculating '
                            'counts')
    return _total_datapoints(data[0]['datapoints'])


def calculate_average(data):
    assert len(data) == 1, ('One set of datapoints required when calculating '
                            'averages')
    datapoints = data[0]['datapoints']
    raw = _total_datapoints(datapoints) / len(datapoints)
    return '{:.3f}'.format(raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Path to config')
    args = parser.parse_args()

    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
        url = build_url(config)
        req = requests.get(url)
        req.raise_for_status()
        data = req.json()
        value = 0
        if config['type'] == "sum":
            value = calculate_count(data)
        elif config['type'] == "percent":
            if len(data) < 2:
                print("metric {} 0.0".format(config['metric']))
                exit(0)
            value = calculate_percentage(data)
        elif config['type'] == "average":
            value = calculate_average(data)
        else:
            raise SyntaxError('Invalid calculation type')
    except (IOError, HTTPError, AssertionError) as e:
        print('{}'.format(repr(e)))
        exit(1)

    print("metric {} {}".format(config['metric'], value))


if __name__ == "__main__":
    main()

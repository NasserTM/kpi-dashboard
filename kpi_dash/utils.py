import re
import requests
from urllib import quote
from kpi_dash import app
from flask import flash
from requests.exceptions import HTTPError


def join_series(data):
    results = []
    if isinstance(data, dict):
        for key in iter(data.keys()):
            results += ['{}({})'.format(key, join_series(data[key]))]
    if isinstance(data, list):
        for item in data:
            results += [join_series(item)]
    if isinstance(data, str) or isinstance(data, unicode):
        return data
    return ','.join(results)


def translate_span(span):
    match = re.match('-([0-9]+)(min|hour|day|week|month|year)', span)
    if match is None:
        return None
    count = int(match.group(1))
    unit = match.group(2)
    if unit == 'min':
        return count * 2
    if unit == 'hour':
        return count * 120
    if unit == 'day':
        return count * 120 * 24
    if unit == 'week':
        return count * 120 * 24 * 7
    if unit == 'month':
        return count * 120 * 24 * 30
    if unit == 'year':
        return count * 120 * 24 * 365


def build_graphite_request(graphite, span, targets, region):
    url = "{}/render/?from={}".format(graphite, span)
    for target in targets:
        url += "&target={}".format(quote(join_series(target)))
    return url.replace('%7Bregion%7D', region)


def sum_datapoints(datapoints):
    value = 0.0
    for (dp, ts) in datapoints:
        if dp:
            value += dp
    return value


def count_datapoints(datapoints):
    count = 0
    for (dp, ts) in datapoints:
        if dp:
            count += 1
    return count


def calculate_percentage(data):
    assert len(data) == 2, ('Two sets of datapoints are required to calculate '
                            'percentage')
    values = [sum_datapoints(target['datapoints']) for pos, target
              in enumerate(data)]
    if values[1] == 0.0:
        return 0.0
    return '{:.3f}%'.format(values[0] / values[1] * 100)


def calculate_sum(data):
    assert len(data) == 1, ('One set of datapoints required when calculating '
                            'counts')
    return sum_datapoints(data[0]['datapoints'])


def calculate_average(data):
    assert len(data) == 1, ('One set of datapoints required when calculating '
                            'averages')
    datapoints = data[0]['datapoints']
    total = sum_datapoints(datapoints)
    total_dp = count_datapoints(datapoints)
    raw = 0.0
    if total_dp > 0:
        raw = total / total_dp
    return '{:.3f}'.format(raw)


def calculate_uptime(data, span):
    expected_hits = translate_span(span)
    datapoints = data[0]['datapoints']
    uptime_hits = count_datapoints(datapoints)
    diff = float(expected_hits - uptime_hits)
    percent_down = diff / expected_hits * 100
    uptime = 100 - percent_down
    return '{:.3f}'.format(uptime)


def process_metrics(metrics, span, region):
    results = list()
    for metric in metrics:
        graphite = app.config['GRAPHITE_SERVER']
        base_url = build_graphite_request(graphite, span, metric['targets'],
                                          region)
        metric['base_url'] = base_url
        url = base_url + '&format=json'
        try:
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
        except HTTPError, e:
            flash('Failed to get statistics for {}: {}'.format(
                  metric['display_name'], repr(e)))
            continue

        value = 0
        if metric['type'] == 'sum':
            value = calculate_count(data)
        elif metric['type'] == 'percent':
            value = calculate_percentage(data)
        elif metric['type'] == 'average':
            value = calculate_average(data)
        elif metric['type'] == 'uptime':
            value = calculate_uptime(data, span)
        else:
            raise SyntaxError('Invalid calculation type')

        metric['value'] = value
        results.append(metric)

    return results

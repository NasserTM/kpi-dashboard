import re
import requests
from datetime import date, datetime
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


def translate_span(start, end):
    if type(start) is date:
        start = datetime.combine(start, datetime.min.time())
    if type(end) is date:
        end = datetime.combine(end, datetime.min.time())
    now = datetime.now()
    days_since_start = now - start
    diff = end - start
    if days_since_start.days < 21:
        return int(diff.total_seconds() / 60)
    else:
        return int(diff.total_seconds() / 900)


def build_graphite_request(graphite, targets, region, start, end=None):
    url = "{}/render/?from={}".format(graphite, start.strftime('%H:%M_%Y%m%d'))
    if end:
        url += '&until={}'.format(end.strftime('%H:%M_%Y%m%d'))
    for target in targets:
        url += "&target={}".format(quote(join_series(target)))
    print url
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
    if len(data) < 2:
        flash('Only one data set returned for percentage calculation')
        return 0.0

    values = [sum_datapoints(target['datapoints']) for pos, target
              in enumerate(data)]
    if values[1] == 0.0:
        return 0.0

    return '{:.3f}%'.format(values[0] / values[1] * 100)


def calculate_sum(data):
    if len(data) == 0:
        flash('Zero data returned')
        return 0

    return sum_datapoints(data[0]['datapoints'])


def calculate_average(data):
    if len(data) == 0:
        flash('Zero data returned')
        return 0.0

    datapoints = data[0]['datapoints']
    total = sum_datapoints(datapoints)
    total_dp = count_datapoints(datapoints)
    raw = 0.0
    if total_dp > 0:
        raw = total / total_dp
    return '{:.3f}'.format(raw)


def calculate_uptime(data, start, end):
    if len(data) == 0:
        flash('Zero uptime statistics')
        return 0.000

    expected_hits = translate_span(start, end)
    datapoints = data[0]['datapoints']
    uptime_hits = count_datapoints(datapoints)
    diff = float(expected_hits - uptime_hits)
    percent_down = diff / expected_hits * 100
    uptime = 100 - percent_down
    return '{:.3f}'.format(uptime)


def process_metrics(metrics, region, start, end):
    results = list()
    for metric in metrics:
        graphite = app.config['GRAPHITE_SERVER']
        base_url = build_graphite_request(graphite,
                                          metric['targets'], region, start,
                                          end)
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
            value = calculate_uptime(data, start, end)
        else:
            raise SyntaxError('Invalid calculation type')

        metric['value'] = value
        results.append(metric)

    return results

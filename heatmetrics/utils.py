import requests
from urllib import quote
from heatmetrics import app


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


def process_metrics(metrics, span, region):
    results = list()
    for metric in metrics:
        graphite = app.config['GRAPHITE_SERVER']
        base_url = build_graphite_request(graphite, span, metric['targets'],
                                          region)
        metric['base_url'] = base_url
        url = base_url + '&format=json'
        req = requests.get(url)
        req.raise_for_status()
        data = req.json()

        value = 0
        if metric['type'] == 'sum':
            value = calculate_count(data)
        elif metric['type'] == 'percent':
            value = calculate_percentage(data)
        elif metric['type'] == 'average':
            value = calculate_average(data)
        else:
            raise SyntaxError('Invalid calculation type')

        metric['value'] = value
        results.append(metric)

    return results

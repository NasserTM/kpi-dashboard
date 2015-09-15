from flask import Flask, request, render_template, redirect, flash, url_for
from heatmetrics import app, metrics_config
from heatmetrics.utils import process_metrics


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/region/<region>')
def get_region(region):
    span = request.args.get('span')
    if span is None:
        span = metrics_config['default_span']

    metrics = process_metrics(metrics_config['metrics'], span, region)
    return render_template('region.html', metrics=metrics, region=region,
                           span=span)

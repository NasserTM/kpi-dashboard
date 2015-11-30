from datetime import date, datetime, timedelta
from flask import Flask, request, render_template, redirect, flash, url_for
from kpi_dash import app, metrics_config
from kpi_dash.forms import DateRangeForm
from kpi_dash.utils import process_metrics


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/region/<region>', methods=['GET', 'POST'])
def get_region(region):
    form = DateRangeForm()
    today = date.today()
    start = today - timedelta(days=7)
    end = datetime.now()
    if request.method == "POST":
        start = form.start_date.data
        end = form.end_date.data
        print start
        print end

    metrics = process_metrics(metrics_config['metrics'], region, start, end)
    return render_template('region.html', metrics=metrics, region=region,
                           form=form)

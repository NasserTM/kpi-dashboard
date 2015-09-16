# Heat KPI Dashboard

## Requirements

- python2.7
- pip

## Prepare

`pip install -r requirements.txt`

## Run Locally

`./runserver.py`

## Running via uWSGI

`uwsgi -s /tmp/uwsgi.sock --module heatmetrics --callable app`

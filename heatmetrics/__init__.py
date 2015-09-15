import yaml
from flask import Flask

app = Flask(__name__)

app.config['DEBUG'] = True

with open('config.yml', 'r') as stream:
    metrics_config = yaml.load(stream)

app.config['GRAPHITE_SERVER'] = metrics_config['graphite']

import heatmetrics.views

import yaml
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_admin import Admin

app = Flask(__name__)
Bootstrap(app)
admin = Admin(app, name='KPI Dashboard', template_mode='bootstrap3')

with open('config.yml', 'r') as stream:
    metrics_config = yaml.load(stream)

app.config['SECRET_KEY'] = metrics_config['secret_key']
app.config['DEBUG'] = metrics_config['debug']
app.config['GRAPHITE_SERVER'] = metrics_config['graphite']
app.config['brand'] = metrics_config['brand']
app.config['regions'] = metrics_config['regions']


import kpi_dash.views

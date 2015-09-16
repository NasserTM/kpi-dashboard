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

## Config

Below is an example config.

```yaml
---
brand: Heat KPI Dashboard
graphite: http://graphite.rs-heat.com
regions:
  - dfw
  - ord
  - iad
  - lon
  - syd
  - hkg
default_span: -7days
metrics:
  - display_name: Percent 50x Responses
    type: percent
    unit: percent
    null_zero: true
    targets:
      - 'removeAbovePercentile(sumSeries(hitcount(stats.heat.*_{region}_rs-heat_com.api.response_5*.requests, "30s")),90)'
      - 'removeAbovePercentile(sumSeries(hitcount(stats.heat.*_{region}_rs-heat_com.api.response_2*.requests, "30s"),hitcount(stats.heat.*_{region}_rs-heat_com.api.response_3*.requests, "30s"),hitcount(stats.heat.*_{region}_rs-heat_com.api.response_4*.requests, "30s")),90)'
  - display_name: Overall Average API Response Time
    type: average
    unit: seconds
    null_zero: false
    targets:
      - 'removeAbovePercentile(averageSeries(stats.timers.heat.*_{region}_rs-heat_com.api.response_*.response_time.mean),90)'
```

* `brand` - The name displayed on the top left of the site
* `graphite` - Address of the graphite server
* `regions` - List of region names
* `default_span` - Graphite relative time definition
* `metrics` - Where you define the graphite calls and how they should be processed
  * `display_name` - Pretty display name for the metrics
  * `type` - `percent`, `sum`, or `average`
  * `unit` - Unit to display
  * `targets` - Array of Graphite targets. For `sum` and `average`, a single target is expected. For `percent`, two need to be supplied

from flask_wtf import Form
from flask_admin.form.widgets import DatePickerWidget
from wtforms import DateField, SubmitField
from wtforms.validators import DataRequired


class DateRangeForm(Form):
    start_date = DateField('Start',
                           widget=DatePickerWidget())
    end_date = DateField('End', widget=DatePickerWidget())
    submit = SubmitField('Go')

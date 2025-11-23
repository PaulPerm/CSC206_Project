from flask_wtf import FlaskForm
from wtforms import  StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class VehicleFilterForm(FlaskForm):
    vehicle_type = SelectField('Type', choices=[], validators=[Optional()])
    manufacturer = SelectField('Make', choices=[], validators=[Optional()])
    model_year = SelectField('Year', choices=[], validators=[Optional()])
    fuel_type = SelectField('Fuel', choices=[], validators=[Optional()])
    color = SelectField('Color', choices=[], validators=[Optional()])
    submit = SubmitField('Search')

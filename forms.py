from flask_wtf import FlaskForm
from wtforms import  StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class VehicleFilterForm(FlaskForm):
    vehicle_type = SelectField("Type", choices=[], validators=[Optional()])
    manufacturer = SelectField("Make", choices=[], validators=[Optional()])
    model_year = SelectField("Year", choices=[], validators=[Optional()])
    fuel_type = SelectField("Fuel", choices=[], validators=[Optional()])
    color = SelectField("Color", choices=[], validators=[Optional()])
    submit = SubmitField("Search")

class BuyVehicleForm(FlaskForm):
    customer_id = SelectField("Customer", choices=[], validators=[DataRequired()])
    purchase_price = IntegerField("Price", validators=[DataRequired()])
    purchase_date = StringField("Purchase Date", validators=[DataRequired()])
    vehicle_condition = SelectField("Condition", choices=[("Poor", "Poor"), ("Fair", "Fair"), ("Good", "Good"), ("Excellent", "Excellent"),], validators=[DataRequired()])
    submit = SubmitField("Purchase")

class SellVehicleForm(FlaskForm):
    customer_id = SelectField("Customer", choices=[], validators=[DataRequired()])
    sales_date = StringField("Sale Date (YYYY-MM-DD)", validators=[DataRequired()])
    submit = SubmitField("Complete Sale")
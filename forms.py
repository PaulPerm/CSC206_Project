from flask_wtf import FlaskForm
from wtforms import  StringField, PasswordField, SubmitField, SelectField, IntegerField, DecimalField
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
    vin = StringField("VIN", validators=[DataRequired()])
    mileage = DecimalField("Mileage", validators=[DataRequired()])
    description = StringField("Description", validators=[Optional()])

    manufacturer_id = SelectField("Manufacturer", choices=[], validators=[DataRequired()])
    vehicle_type_id = SelectField("Type", choices=[], validators=[DataRequired()])
    model_year = IntegerField("Model Year", validators=[DataRequired()])
    model_name = StringField("Model Name", validators=[DataRequired()])
    fuel_type = StringField("Fuel Type", validators=[DataRequired()])

    customer_id = SelectField("Customer", choices=[], validators=[DataRequired()])
    purchase_price = IntegerField("Price", validators=[DataRequired()])
    purchase_date = StringField("Purchase Date", validators=[DataRequired()])

    vehicle_condition = SelectField(
        "Condition",
        choices=[
            ("Excellent", "Excellent"),
            ("Very Good", "Very Good"),
            ("Good", "Good"),
            ("Fair", "Fair"),
        ],
        validators=[DataRequired()],
    )

    submit = SubmitField("Purchase")

class SellVehicleForm(FlaskForm):
    customer_id = SelectField("Customer", choices=[], validators=[DataRequired()])
    sales_date = StringField("Sale Date (YYYY-MM-DD)", validators=[DataRequired()])
    submit = SubmitField("Complete Sale")
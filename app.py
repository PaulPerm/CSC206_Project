from flask import Flask, render_template, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from sql_queries import vehicle_query, report_query
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import Optional

app = Flask(__name__)
app.secret_key = 'csc206-session-key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'S4q/[CSCpaul'
app.config['MYSQL_DB'] = 'csc206cars'

mysql = MySQL(app)

class VehicleFilterForm(FlaskForm):
    vehicle_type = StringField('Type', validators=[Optional()])
    manufacturer = StringField('Make', validators=[Optional()])
    model_year = IntegerField('Year', validators=[Optional()])
    fuel_type = StringField('Fuel', validators=[Optional()])
    color = StringField('Color', validators=[Optional()])
    submit = SubmitField('Search')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    vc = vehicle_query.Vehicles()
    form = VehicleFilterForm()
    query = vc.VEHICLE_LIST_QUERY
    params = []
    filters = []

    if form.validate_on_submit():
        if form.vehicle_type.data:
            filters.append("vt.vehicle_type_name LIKE %s")
            params.append("%" + form.vehicle_type.data + "%")

        if form.manufacturer.data:
            filters.append("m.manufacturer_name LIKE %s")
            params.append("%" + form.manufacturer.data + "%")

        if form.model_year.data:
            filters.append("v.model_year = %s")
            params.append(form.model_year.data)

        if form.fuel_type.data:
            filters.append("v.fuel_type LIKE %s")
            params.append("%" + form.fuel_type.data + "%")

        if form.color.data:
            filters.append("c.color_name LIKE %s")
            params.append("%" + form.color.data + "%")

        if len(filters) > 0:
            where = " AND " + " AND ".join(filters)
            query = query.replace("GROUP BY", where + " GROUP BY")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, tuple(params))
    output = cur.fetchall()
    cur.close()

    return render_template('vehicles.html', vehicles=output, form=form)


@app.route('/reports')
def reports():
    return render_template('reports/reports.html')

@app.route('/reports/sales')
def report_sales():
    rc = report_query.Reports()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rc.SALES_PRODUCTIVITY_QUERY)
    results = cur.fetchall()
    cur.close()
    return render_template('reports/sales.html', results=results)

@app.route('/reports/sellers')
def report_sellers():
    rc = report_query.Reports()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rc.SELLER_HISTORY_QUERY)
    results = cur.fetchall()
    cur.close()
    return render_template('reports/seller.html', results=results)

@app.route('/reports/parts')
def report_parts():
    rc = report_query.Reports()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rc.PART_STATISTICS_QUERY)
    results = cur.fetchall()
    cur.close()
    return render_template('reports/parts.html', results=results)

@app.route('/login')
def login():
    return render_template('login.html')
                           
if __name__ == '__main__':
    app.run(debug=True)
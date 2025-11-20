from flask import Flask, render_template, redirect, request
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
    vehicle_type = SelectField('Type', choices=[], validators=[Optional()])
    manufacturer = SelectField('Make', choices=[], validators=[Optional()])
    model_year = SelectField('Year', choices=[], validators=[Optional()])
    fuel_type = SelectField('Fuel', choices=[], validators=[Optional()])
    color = SelectField('Color', choices=[], validators=[Optional()])
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
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT vehicle_type_name FROM vehicletypes")
    form.vehicle_type.choices = [('', 'Any')] + [(row[0], row[0]) for row in cur.fetchall()]

    cur.execute("SELECT manufacturer_name FROM manufacturers")
    form.manufacturer.choices = [('', 'Any')] + [(row[0], row[0]) for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT model_year FROM vehicles ORDER BY model_year DESC")
    form.model_year.choices = [('', 'Any')] + [(row[0], row[0]) for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT fuel_type FROM vehicles")
    form.fuel_type.choices = [('', 'Any')] + [(row[0], row[0]) for row in cur.fetchall()]

    cur.execute("""
    SELECT DISTINCT c.color_name 
    FROM colors c
    JOIN vehiclecolors vc ON vc.colorID = c.colorID
    """)

    form.color.choices = [('', 'Any')] + [(row[0], row[0]) for row in cur.fetchall()]

    cur.close()
    
    if request.args.get("show_all") == "1":
        query = vc.all_vehicles_list()
        params = []  # reset params
    else:
        # Normal filter behavior
        if form.validate_on_submit():
            filters = []

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

            if filters:
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

@app.route('/vehicles/<int:vehicle_id>')      
def vehicle_details(vehicle_id):
    vc = vehicle_query.Vehicles()
    query = vc.vehicle_details()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, (vehicle_id,))
    vehicle = cur.fetchone()
    cur.close()
    return render_template('vehicle_details.html', vehicle=vehicle)

if __name__ == '__main__':
    app.run(debug=True)
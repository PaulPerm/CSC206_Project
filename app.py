from flask import Flask, render_template, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from sql_queries import vehicle_query, report_query
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import Optional

app = Flask(__name__)
app.secret_key = '4b9f20eae5cb24ad3fc5b6f6e5d3f9c7'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'S4q/[CSCpaul'
app.config['MYSQL_DB'] = 'csc206cars'

mysql = MySQL(app)

class VehicleFilterForm(FlaskForm):
    vehicle_type = StringField('Vehicle Type:', validators=[Optional()])
    manufacturer = StringField('Manufacturer:', validators=[Optional()])
    model_year = IntegerField('Model Year:', validators=[Optional()])
    fuel_type = StringField('Fuel Type:', validators=[Optional()])
    color = StringField('Color:', validators=[Optional()])
    submit = SubmitField('Search')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    # vc = vehicle_query.Vehicles()
    # form = VehicleFilterForm()

    # cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # query = vc.VEHICLE_LIST_QUERY
    # conditions = []
    # params = []

    # if form.validate_on_submit():
    #     if form.vehicle_type.data:
    #         conditions.append("vt.vehicle_type_name LIKE %s")
    #         params.append(f"%{form.vehicle_type.data}%")
    #     if form.manufacturer.data:
    #         conditions.append("m.manufacturer_name LIKE %s")
    #         params.append(f"%{form.manufacturer.data}%")
    #     if form.model_year.data:
    #         conditions.append("v.model_year = %s")
    #         params.append(form.model_year.data)
    #     if form.fuel_type.data:
    #         conditions.append("v.fuel_type LIKE %s")
    #         params.append(f"%{form.fuel_type.data}%")
    #     if form.color.data:
    #         conditions.append("c.color_name LIKE %s")
    #         params.append(f"%{form.color.data}%")

    #     if conditions:
    #         where_clause = " AND " + " AND ".join(conditions)
    #         query = query.replace("GROUP BY", f"{where_clause}\nGROUP BY")
    #         cur.execute(query, params)
    #     else:
    #         cur.execute(query)
    # else:
    #     cur.execute(query)
    
    # vehicles = cur.fetchall()
    # cur.close()

    # return render_template('vehicles.html', vehicles=vehicles, form=form)
    vc = vehicle_query.Vehicles()
    form = VehicleFilterForm()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = vc.VEHICLE_LIST_QUERY
    params = []

    # Simple form filtering (realistic version)
    if form.validate_on_submit():
        if form.vehicle_type.data:
            query = query.replace("GROUP BY", "AND vt.vehicle_type_name LIKE %s GROUP BY")
            params.append("%" + form.vehicle_type.data + "%")

        if form.manufacturer.data:
            query = query.replace("GROUP BY", "AND m.manufacturer_name LIKE %s GROUP BY")
            params.append("%" + form.manufacturer.data + "%")

        if form.model_year.data:
            query = query.replace("GROUP BY", "AND v.model_year = %s GROUP BY")
            params.append(form.model_year.data)

        if form.fuel_type.data:
            query = query.replace("GROUP BY", "AND v.fuel_type LIKE %s GROUP BY")
            params.append("%" + form.fuel_type.data + "%")

        if form.color.data:
            query = query.replace("GROUP BY", "AND c.color_name LIKE %s GROUP BY")
            params.append("%" + form.color.data + "%")

        cur.execute(query, tuple(params))
    else:
        cur.execute(query)

    vehicles = cur.fetchall()
    cur.close()

    return render_template('vehicles.html', vehicles=vehicles, form=form)

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
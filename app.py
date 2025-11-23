from flask import Flask, render_template, redirect, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from sql_queries import vehicle_query, report_query
from forms import LoginForm, VehicleFilterForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    vc = vehicle_query.Vehicles()
    form = VehicleFilterForm()

    role = session.get("role", "Public")

    if role == "Owner":
        query = vc.ALL_VEHICLES_QUERY
    else:
        query = vc.VEHICLE_LIST_QUERY

    params = []

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    
    form.vehicle_type.choices = [('', 'Any')]
    cur.execute("SELECT vehicle_type_name FROM vehicletypes")
    rows = cur.fetchall()
    for r in rows:
        form.vehicle_type.choices.append((r["vehicle_type_name"], r["vehicle_type_name"]))

  
    form.manufacturer.choices = [('', 'Any')]
    cur.execute("SELECT manufacturer_name FROM manufacturers")
    rows = cur.fetchall()
    for r in rows:
        form.manufacturer.choices.append((r["manufacturer_name"], r["manufacturer_name"]))

    
    form.model_year.choices = [('', 'Any')]
    cur.execute("SELECT DISTINCT model_year FROM vehicles ORDER BY model_year DESC")
    rows = cur.fetchall()
    for r in rows:
        form.model_year.choices.append((str(r["model_year"]), str(r["model_year"])))

    
    form.fuel_type.choices = [('', 'Any')]
    cur.execute("SELECT DISTINCT fuel_type FROM vehicles")
    rows = cur.fetchall()
    for r in rows:
        form.fuel_type.choices.append((r["fuel_type"], r["fuel_type"]))

    
    form.color.choices = [('', 'Any')]
    cur.execute("""
        SELECT DISTINCT c.color_name
        FROM colors c
        JOIN vehiclecolors vc ON vc.colorID = c.colorID
    """)
    rows = cur.fetchall()
    for r in rows:
        form.color.choices.append((r["color_name"], r["color_name"]))

    cur.close()

    if request.args.get("show_all") == "1":
        query = vc.ALL_VEHICLES_QUERY
        params = []
    elif form.validate_on_submit():
        filters = []

        if form.vehicle_type.data:
            filters.append("vt.vehicle_type_name = %s")
            params.append(form.vehicle_type.data)

        if form.manufacturer.data:
            filters.append("m.manufacturer_name = %s")
            params.append(form.manufacturer.data)

        if form.model_year.data:
            filters.append("v.model_year = %s")
            params.append(form.model_year.data)

        if form.fuel_type.data:
            filters.append("v.fuel_type = %s")
            params.append(form.fuel_type.data)

        if form.color.data:
            filters.append("c.color_name = %s")
            params.append(form.color.data)

        if filters:
            where = " AND " + " AND ".join(filters)
            query = query.replace("GROUP BY", where + " GROUP BY")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(query, tuple(params))
    vehicles = cur.fetchall()
    cur.close()

    return render_template('vehicles.html', vehicles=vehicles, form=form)



@app.route('/reports')
def reports():
    return render_template('reports/reports.html')

@app.route('/reports/sales')
def report_sales():
    if session.get("role") != "Owner":
        return redirect(url_for("home"))
    
    rc = report_query.Reports()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rc.SALES_PRODUCTIVITY_QUERY)
    results = cur.fetchall()
    cur.close()
    return render_template('reports/sales.html', results=results)

@app.route('/reports/sellers')
def report_sellers():
    if session.get("role") != "Owner":
        return redirect(url_for("home"))
    
    rc = report_query.Reports()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rc.SELLER_HISTORY_QUERY)
    results = cur.fetchall()
    cur.close()
    return render_template('reports/seller.html', results=results)

@app.route('/reports/parts')
def report_parts():
    if session.get("role") != "Owner":
        return redirect(url_for("home"))
    
    rc = report_query.Reports()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rc.PART_STATISTICS_QUERY)
    results = cur.fetchall()
    cur.close()
    return render_template('reports/parts.html', results=results)

@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session["user_id"] = user["userID"]
            session["first_name"] = user["first_name"]
            session["last_name"] = user["last_name"]
            session["role"] = user["role"]

            return redirect(url_for("vehicles"))
        return render_template("login.html", form=form, error=True)
    
    return render_template('login.html', form = form, error=False)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/vehicles/<int:vehicle_id>')      
def vehicle_details(vehicle_id):
    vc = vehicle_query.Vehicles()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute(vc.vehicle_details(), (vehicle_id,))
    vehicle = cur.fetchone()

    cur.execute(vc.vehicle_parts(), (vehicle_id,))
    parts = cur.fetchall()

    cur.execute(vc.vehicle_seller(), (vehicle_id,))
    seller = cur.fetchone()

    cur.execute(vc.vehicle_buyer(), (vehicle_id,))
    buyer = cur.fetchone()

    cur.close()

    return render_template("vehicle_details.html", vehicle=vehicle, parts=parts, seller=seller, buyer=buyer)

@app.route("/buy/<int:vehicle_id>")
def buy_vehicle(vehicle_id):
    role = session.get("role", "Public")

    if role not in ["Buyer", "Owner"]:
        return redirect(url_for("login")) 
    
    return render_template('buy_vehicle.html', vehicle_id=vehicle_id)

@app.route("/sell/<int:vehicle_id>")
def sell_vehicle(vehicle_id):
    role = session.get("role", "Public")

    if role not in ["Sales", "Owner"]:
        return redirect(url_for("login")) 
    
    return render_template('sell_vehicle.html', vehicle_id=vehicle_id)


if __name__ == '__main__':
    app.run(debug=True)
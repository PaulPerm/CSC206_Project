from flask import Flask, render_template, redirect, request, session, url_for, flash
from forms import LoginForm, VehicleFilterForm, BuyVehicleForm, SellVehicleForm
from sql_queries import transaction_queries, vehicle_query, report_query
from mydatabase import myConnect 
from config import Config
import MySQLdb.cursors  


app = Flask(__name__)
app.secret_key = "csc206-session-key"  
app.config.from_object(Config)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = myConnect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        row = cur.fetchone()
        columns = [col[0] for col in cur.description]
        user = dict(zip(columns, row)) if row else None
        cur.close()
        conn.close()

        if user:
            session["user_id"] = user["userID"]
            session["first_name"] = user["first_name"]
            session["last_name"] = user["last_name"]
            session["role"] = user["role"]
            return redirect(url_for("vehicles"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/vehicles', methods=["GET", "POST"])
def vehicles():
    vc = vehicle_query.Vehicles()
    tq = transaction_queries.TransactionQueries()
    form = VehicleFilterForm()

    role = session.get("role", "Public")
    user_id = session.get("user_id")

    query = vc.ALL_VEHICLES_QUERY if role == "Owner" else vc.VEHICLE_LIST_QUERY
    params = []

    conn = myConnect()
    cur = conn.cursor()

    
    form.vehicle_type.choices = [('', 'Any')]
    cur.execute("SELECT vehicle_type_name FROM vehicletypes")
    form.vehicle_type.choices += [(r[0], r[0]) for r in cur.fetchall()]

   
    form.manufacturer.choices = [('', 'Any')]
    cur.execute("SELECT manufacturer_name FROM manufacturers")
    form.manufacturer.choices += [(r[0], r[0]) for r in cur.fetchall()]

   
    form.model_year.choices = [('', 'Any')]
    cur.execute("SELECT DISTINCT model_year FROM vehicles ORDER BY model_year DESC")
    form.model_year.choices += [(str(r[0]), str(r[0])) for r in cur.fetchall()]

    
    form.fuel_type.choices = [('', 'Any')]
    cur.execute("SELECT DISTINCT fuel_type FROM vehicles")
    form.fuel_type.choices += [(r[0], r[0]) for r in cur.fetchall()]

    
    form.color.choices = [('', 'Any')]
    cur.execute("""
        SELECT DISTINCT c.color_name
        FROM colors c
        JOIN vehiclecolors vc ON vc.colorID = c.colorID
    """)
    form.color.choices += [(r[0], r[0]) for r in cur.fetchall()]

    if request.args.get("show_all") == "1":
        query = vc.ALL_VEHICLES_QUERY
    elif form.validate_on_submit():
        filters = []

        if form.vehicle_type.data:
            filters.append("vt.vehicle_type_name = ?")
            params.append(form.vehicle_type.data)
        if form.manufacturer.data:
            filters.append("m.manufacturer_name = ?")
            params.append(form.manufacturer.data)
        if form.model_year.data:
            filters.append("v.model_year = ?")
            params.append(form.model_year.data)
        if form.fuel_type.data:
            filters.append("v.fuel_type = ?")
            params.append(form.fuel_type.data)
        if form.color.data:
            filters.append("c.color_name = ?")
            params.append(form.color.data)

        if filters:
            where = " AND " + " AND ".join(filters)
            query = query.replace("GROUP BY", where + " GROUP BY")

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    vehicles = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()

    return render_template('vehicles.html', vehicles=vehicles, form=form)


@app.route('/vehicle/<int:vehicle_id>')
def vehicle_details(vehicle_id):
    conn = myConnect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM vehicles WHERE vehicleID = %s", (vehicle_id,))
    row = cur.fetchone()
    columns = [col[0] for col in cur.description]
    vehicle = dict(zip(columns, row)) if row else None

    cur.close()
    conn.close()

    if not vehicle:
        flash("Vehicle not found", "danger")
        return redirect(url_for("vehicles"))

    return render_template('vehicle_details.html', vehicle=vehicle)

@app.route("/report_sales")
def report_sales():
    rq = report_query.ReportQueries()

    conn = myConnect()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)  
    results = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("sales.html", results=results)

@app.route("/report_parts")
def report_parts():
    rq = report_query.ReportQueries()

    conn = myConnect()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rq.parts_report())  # assumes method in report_query.py
    results = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("parts.html", results=results)

@app.route("/report_seller")
def report_seller():
    rq = report_query.ReportQueries()

    conn = myConnect()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(rq.seller_report())  # assumes method in report_query.py
    results = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("seller.html", results=results)


@app.route("/buy/<int:vehicle_id>", methods=["GET", "POST"])
def buy_vehicle(vehicle_id):
    if session.get("role") not in ["Buyer", "Owner"]:
        return redirect(url_for("login"))

    form = BuyVehicleForm()
    tq = transaction_queries.TransactionQueries()

    conn = myConnect()
    cur = conn.cursor()

    cur.execute(tq.customer_list())
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    customers = [dict(zip(columns, row)) for row in rows]

    choices = [("", "Select Customer")]
    choices += [(str(c["customerID"]), f"{c['first_name']} {c['last_name']}") for c in customers]
    form.customer_id.choices = choices

    if form.validate_on_submit():
        customer_id = form.customer_id.data
        purchase_price = form.purchase_price.data
        purchase_date = form.purchase_date.data
        vehicle_condition = form.vehicle_condition.data
        user_id = session.get("user_id")

        try:
            cur.execute(
                tq.insert_purchase(),
                (vehicle_id, customer_id, user_id, purchase_date, purchase_price, vehicle_condition)
            )
            conn.commit()
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return render_template("buy_vehicle.html", form=form, vehicle_id=vehicle_id)

        cur.close()
        conn.close()
        return render_template("purchase_confirmation.html", vehicle_id=vehicle_id)

    return render_template("buy_vehicle.html", form=form, vehicle_id=vehicle_id)


@app.route("/sell/<int:vehicle_id>", methods=["GET", "POST"])
def sell_vehicle(vehicle_id):
    if session.get("role") not in ["Sales", "Owner"]:
        return redirect(url_for("login"))

    form = SellVehicleForm()
    tq = transaction_queries.TransactionQueries()

    conn = myConnect()
    cur = conn.cursor()
    cur.execute(tq.customer_list())
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    customers = [dict(zip(columns, row)) for row in rows]

    choices = [("", "Select Customer")]
    choices += [(str(c["customerID"]), f"{c['first_name']} {c['last_name']}") for c in customers]
    form.customer_id.choices = choices

    if form.validate_on_submit():
        customer_id = form.customer_id.data
        sales_date = form.sales_date.data
        user_id = session.get("user_id")

        try:
            cur.execute(tq.insert_sale(), (vehicle_id, customer_id, user_id, sales_date))
            conn.commit()
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return render_template("sell_vehicle.html", form=form, vehicle_id=vehicle_id)

        cur.close()
        conn.close()
        return redirect(url_for("vehicles"))

    return render_template("sell_vehicle.html", form=form, vehicle_id=vehicle_id)


if __name__ == "__main__":
    app.run(debug=True)

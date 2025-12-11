from flask import Flask, render_template, redirect, request, session, url_for, flash
from forms import LoginForm, VehicleFilterForm, BuyVehicleForm, SellVehicleForm
from sql_queries import transaction_queries, vehicle_query, report_query
from mydatabase import myConnect 
from config import Config
from MySQLdb.cursors import DictCursor


app = Flask(__name__)
app.secret_key = "csc206-session-key"  
app.config.from_object(Config)

@app.route('/')
def home():
    return redirect(url_for('vehicles'))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = myConnect()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cur.fetchone()   
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
    form = VehicleFilterForm()

    role = session.get("role", "Public")
    user_id = session.get("user_id")

    if role == "Owner":
        query = vc.ALL_VEHICLES_QUERY
    else:
        query = vc.SELLABLE_VEHICLES_QUERY
    params = []

    
    conn = myConnect()
    cur = conn.cursor(DictCursor)

    
    form.vehicle_type.choices = [('', 'Any')]
    cur.execute("SELECT vehicle_type_name FROM vehicletypes")
    form.vehicle_type.choices += [(r["vehicle_type_name"], r["vehicle_type_name"]) for r in cur.fetchall()]

    form.manufacturer.choices = [('', 'Any')]
    cur.execute("SELECT manufacturer_name FROM manufacturers")
    form.manufacturer.choices += [(r["manufacturer_name"], r["manufacturer_name"]) for r in cur.fetchall()]

    form.model_year.choices = [('', 'Any')]
    cur.execute("SELECT DISTINCT model_year FROM vehicles ORDER BY model_year DESC")
    form.model_year.choices += [(str(r["model_year"]), str(r["model_year"])) for r in cur.fetchall()]

    form.fuel_type.choices = [('', 'Any')]
    cur.execute("SELECT DISTINCT fuel_type FROM vehicles")
    form.fuel_type.choices += [(r["fuel_type"], r["fuel_type"]) for r in cur.fetchall()]

    form.color.choices = [('', 'Any')]
    cur.execute("""
        SELECT DISTINCT c.color_name
        FROM colors c
        JOIN vehiclecolors vc ON vc.colorID = c.colorID
    """)
    form.color.choices += [(r["color_name"], r["color_name"]) for r in cur.fetchall()]

   
    filters = []

    if request.args.get("show_all") == "1" and role == "Owner":
        query = vc.ALL_VEHICLES_QUERY

    elif form.validate_on_submit():
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
            where_clause = " AND " + " AND ".join(filters)

            if "WHERE" in query.upper():
                if "GROUP BY" in query.upper():
                    parts = query.split("GROUP BY")
                    query = parts[0] + where_clause + " GROUP BY " + parts[1]
                else:
                    query += where_clause
            else:
                if "GROUP BY" in query.upper():
                    parts = query.split("GROUP BY")
                    query = parts[0] + " WHERE " + " AND ".join(filters) + " GROUP BY " + parts[1]
                else:
                    query += " WHERE " + " AND ".join(filters)

    
    cur.execute(query, tuple(params))
    vehicles = cur.fetchall()  

    cur.close()
    conn.close()

    return render_template('vehicles.html', vehicles=vehicles, form=form)




@app.route('/vehicle/<int:vehicle_id>')
def vehicle_details(vehicle_id):
    conn = myConnect()
    cur = conn.cursor()

    vc = vehicle_query.Vehicles()

 
    cur.execute(vc.vehicle_details(), (vehicle_id,))
    vehicle = cur.fetchone()

    if not vehicle:
        flash("Vehicle not found", "danger")
        return redirect(url_for("vehicles"))

    
    cur.execute(vc.vehicle_parts(), (vehicle_id,))
    parts = cur.fetchall()

    
    cur.execute(vc.vehicle_seller(), (vehicle_id,))
    seller = cur.fetchone()

    
    cur.execute(vc.vehicle_buyer(), (vehicle_id,))
    buyer = cur.fetchone()

    
    cur.execute("SELECT 1 FROM salestransactions WHERE vehicleID = %s", (vehicle_id,))
    is_sold = cur.fetchone() is not None

    cur.close()
    conn.close()

    return render_template(
        'vehicle_details.html',
        vehicle=vehicle,
        parts=parts,
        seller=seller,
        buyer=buyer,
        is_sold=is_sold
    )

@app.route("/report_sales")
def report_sales():
    rq = report_query.ReportQueries()

    conn = myConnect()
    cur = conn.cursor()
    cur.execute(rq.sales_report())
    results = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("reports/sales.html", results=results)

@app.route("/report_parts")
def report_parts():
    rq = report_query.ReportQueries()

    conn = myConnect()
    cur = conn.cursor()
    cur.execute(rq.parts_report())
    results = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("reports/parts.html", results=results)

@app.route("/report_seller")
def report_seller():
    rq = report_query.ReportQueries()

    conn = myConnect()
    cur = conn.cursor()
    cur.execute(rq.seller_report())
    results = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("reports/seller.html", results=results)


@app.route("/buy", methods=["GET", "POST"])
def buy_vehicle():
   
    if session.get("role") == "Sales":
        return redirect(url_for("login"))

    form = BuyVehicleForm()
    tq = transaction_queries.TransactionQueries()

    conn = myConnect()
    cur = conn.cursor()

    
    cur.execute(tq.customer_list())
    customers = cur.fetchall()
    form.customer_id.choices = [("", "Select Customer")] + [
        (str(c["customerID"]), f"{c['first_name']} {c['last_name']}")
        for c in customers
    ]

   
    cur.execute("SELECT manufacturerID, manufacturer_name FROM manufacturers")
    manufacturers = cur.fetchall()
    form.manufacturer_id.choices = [
        (str(m["manufacturerID"]), m["manufacturer_name"])
        for m in manufacturers
    ]

   
    cur.execute("SELECT vehicle_typeID, vehicle_type_name FROM vehicletypes")
    types = cur.fetchall()
    form.vehicle_type_id.choices = [
        (str(t["vehicle_typeID"]), t["vehicle_type_name"])
        for t in types
    ]

    if form.validate_on_submit():
        cur.execute("SELECT vehicleID FROM vehicles WHERE vin = %s", (form.vin.data,))
        existing = cur.fetchone()
        if existing:
            
            form.vin.errors.append("A vehicle with this VIN already exists. Please enter a different VIN.")
             
            return render_template("buy_vehicle.html", form=form)

        try:
           
            cur.execute(
                tq.insert_vehicle(),
                (
                    form.vin.data,                   
                    form.mileage.data,              
                    form.description.data or "",     
                    form.model_name.data,            
                    form.model_year.data,           
                    form.fuel_type.data,             
                    form.manufacturer_id.data,       
                    form.vehicle_type_id.data,       
                )
            )
            conn.commit()
            vehicle_id = cur.lastrowid

            
            cur.execute(
                tq.insert_purchase(),
                (
                    vehicle_id,                      
                    session.get("user_id"),          
                    form.customer_id.data,           
                    form.purchase_price.data,        
                    form.purchase_date.data,         
                    form.vehicle_condition.data,     
                )
            )
            conn.commit()

            flash("Purchase recorded successfully.", "success")

            cur.close()
            conn.close()

            
            return redirect(url_for("purchase_confirmation", vehicle_id=vehicle_id))

        except Exception as e:
            conn.rollback()
            
            print("DB ERROR IN /buy:", e)
            
            return render_template("buy_vehicle.html", form=form)

    cur.close()
    conn.close()
    return render_template("buy_vehicle.html", form=form)


@app.route("/purchase_confirmation/<int:vehicle_id>")
def purchase_confirmation(vehicle_id):
    return render_template("purchase_confirmation.html", vehicle_id=vehicle_id)

@app.route("/sell/<int:vehicle_id>", methods=["GET", "POST"])
def sell_vehicle(vehicle_id):
    if session.get("role") not in ["Sales", "Owner"]:
        return redirect(url_for("login"))

    form = SellVehicleForm()
    tq = transaction_queries.TransactionQueries()

    conn = myConnect()
    cur = conn.cursor()
    cur = conn.cursor()
    cur.execute(tq.customer_list())
    customers = cur.fetchall()  

    choices = [("", "Select Customer")]
    choices += [
        (str(c["customerID"]), f"{c['first_name']} {c['last_name']}")
        for c in customers
    ]
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
        return redirect(url_for("sell_confirmation", vehicle_id=vehicle_id))

    return render_template("sell_vehicle.html", form=form, vehicle_id=vehicle_id)

@app.route("/sell_confirmation/<int:vehicle_id>")
def sell_confirmation(vehicle_id):
    
    if session.get("role") not in ["Sales", "Owner"]:
        return redirect(url_for("login"))

    return render_template("sell_confirmation.html", vehicle_id=vehicle_id)

if __name__ == "__main__":
    app.run(debug=True)

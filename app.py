from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash

app = Flask(_name_)
app.secret_key = "replace_with_a_strong_secret"

# ---------- Database Connection ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Prajwal@23",
        database="vehicle"
    )


# ---------- User Authentication ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("⚠ Both username and password are required.", "warning")
            return redirect(url_for('login'))

        db = get_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM app_user WHERE username=%s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f"✅ Welcome back, {user['username']}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("❌ Invalid username or password", "danger")

        except Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            cursor.close()
            db.close()

    return render_template('login.html')


# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("👋 Logged out successfully.", "info")
    return redirect(url_for('login'))


# ---------- Home ----------
@app.route('/')
def index():
    return render_template('index.html')


# ---------- Dashboard ----------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("⚠ Please login first.", "warning")
        return redirect(url_for('login'))

    db = get_connection()
    cursor = db.cursor()
    stats = {}
    try:
        cursor.execute("SELECT COUNT(*) FROM vehicle")
        stats['vehicles'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM payment")
        stats['payments'] = cursor.fetchone()[0]
        cursor.execute("SELECT IFNULL(SUM(Amount),0) FROM payment WHERE Status = 'Completed'")
        stats['total_collected'] = cursor.fetchone()[0]
    except Error as e:
        flash(f"DB Error: {e}", "danger")
        stats = {'vehicles': 0, 'payments': 0, 'total_collected': 0}
    finally:
        cursor.close()
        db.close()
    return render_template('dashboard.html', stats=stats)


# ---------- Admin Panel ----------
@app.route('/admin_panel')
def admin_panel():
    if 'role' not in session or session['role'] != 'admin':
        flash("🚫 Access denied. Admins only.", "danger")
        return redirect(url_for('dashboard'))

    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total_users FROM app_user")
        total_users = cursor.fetchone()['total_users']

        cursor.execute("SELECT COUNT(*) AS total_vehicles FROM vehicle")
        total_vehicles = cursor.fetchone()['total_vehicles']

        cursor.execute("SELECT COUNT(*) AS total_services FROM service_record")
        total_services = cursor.fetchone()['total_services']

    except Error as e:
        flash(f"Database error: {e}", "danger")
        total_users = total_vehicles = total_services = 0
    finally:
        cursor.close()
        db.close()

    return render_template(
        'admin_panel.html',
        total_users=total_users,
        total_vehicles=total_vehicles,
        total_services=total_services
    )


# ---------- Show All Vehicles ----------
@app.route('/vehicles')
def vehicles():
    if 'username' not in session:
        flash("⚠ Please login first.", "warning")
        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        if q:
            sql = "SELECT * FROM vehicle WHERE Model LIKE %s OR V_no LIKE %s"
            like = f"%{q}%"
            cursor.execute(sql, (like, like))
        else:
            cursor.execute("SELECT * FROM vehicle")
        data = cursor.fetchall()
    except Error as e:
        flash(f"DB Error: {e}", "danger")
        data = []
    finally:
        cursor.close()
        db.close()
    return render_template('vehicles.html', vehicles=data, q=q)


# ---------- Add Vehicle ----------
@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if 'username' not in session:
        flash("⚠ Please login first.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        owner_id = request.form.get('owner_id')
        license_plate = request.form.get('license')
        model = request.form.get('model')
        milage = request.form.get('milage')
        v_no = request.form.get('v_no')

        if not (owner_id and license_plate and model and milage and v_no):
            flash("⚠ All fields are required.", "warning")
            return redirect(url_for('vehicles'))

        db = get_connection()
        cursor = db.cursor()

        try:
            cursor.execute("SELECT Owner_id FROM owner WHERE Owner_id = %s", (owner_id,))
            owner_exists = cursor.fetchone()

            if not owner_exists:
                cursor.execute("""
                    INSERT INTO owner (Owner_id, Name, Ph_no, Email, Address)
                    VALUES (%s, %s, %s, %s, %s)
                """, (owner_id, f'Owner {owner_id}', '0000000000', f'owner{owner_id}@example.com', 'Unknown Address'))

            cursor.execute("""
                INSERT INTO vehicle (Owner_id, License, Model, Milage, V_no)
                VALUES (%s, %s, %s, %s, %s)
            """, (owner_id, license_plate, model, milage, v_no))

            db.commit()
            flash("✅ Vehicle added successfully!", "success")

        except Error as err:
            flash(f"❌ Database Error: {err}", "danger")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('vehicles'))

    return render_template('add_vehicle.html')


# ---------- Service Rating ----------
@app.route('/rating', methods=['GET', 'POST'])
def rating():
    if 'username' not in session:
        flash("⚠ Please login first.", "warning")
        return redirect(url_for('login'))

    avg_rating = None
    service_type_id = None

    if request.method == 'POST':
        service_type_id = request.form.get('serviceTypeId')
        if service_type_id:
            try:
                db = get_connection()
                cursor = db.cursor()
                cursor.execute("SELECT avg_service_rating(%s)", (service_type_id,))
                avg_rating = cursor.fetchone()[0]
            except Error as e:
                flash(f"Database error: {e}", "danger")
            finally:
                cursor.close()
                db.close()
        else:
            flash("Please enter a Service Type ID.", "warning")

    return render_template('rating.html', avg_rating=avg_rating, service_type_id=service_type_id)


# ---------- Total Service Cost ----------
@app.route('/service_cost', methods=['GET', 'POST'])
def service_cost():
    if 'username' not in session:
        flash("⚠ Please login first.", "warning")
        return redirect(url_for('login'))

    total_cost = None
    vehicle_id = None

    if request.method == 'POST':
        vehicle_id = request.form.get('vehicleId')
        if vehicle_id:
            try:
                db = get_connection()
                cursor = db.cursor()
                cursor.execute("SELECT total_service_cost(%s)", (vehicle_id,))
                result = cursor.fetchone()
                print("🔍 SQL Result:", result)  # 👈 debug line
                if result:
                    total_cost = result[0]
                    print("✅ Total cost fetched:", total_cost)
                else:
                    print("⚠ No result returned from SQL function.")
            except Error as e:
                flash(f"Database error: {e}", "danger")
                print("❌ Database error:", e)
            finally:
                cursor.close()
                db.close()
        else:
            flash("Please enter a Vehicle ID.", "warning")

    return render_template('service_cost.html', total_cost=total_cost, vehicle_id=vehicle_id)



# ---------- Mechanic Payments ----------
@app.route('/mechanic_payments/<int:mec_id>')
def mechanic_payments_view(mec_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("⚠ Only admin can view mechanic payments.", "danger")
        return redirect(url_for('dashboard'))

    payments = []
    totals = []
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.callproc('GetMechanicPayments', [mec_id])
        results = list(cursor.stored_results())
        if len(results) >= 1:
            payments = results[0].fetchall()
        if len(results) >= 2:
            totals = results[1].fetchall()
    except Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return render_template('mechanic_payments.html', mec_id=mec_id, payments=payments, totals=totals)


# ---------- Vehicle Details ----------
@app.route('/vehicles/<int:v_id>')
def vehicle_detail(v_id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM vehicle WHERE V_id = %s", (v_id,))
        vehicle = cursor.fetchone()
    except Error as e:
        flash(f"DB Error: {e}", "danger")
        vehicle = None
    finally:
        cursor.close()
        db.close()
    return render_template('vehicle_detail.html', vehicle=vehicle)


# ---------- Vehicle Service Details ----------
@app.route('/vehicle_service_details/<int:vehicle_id>')
def vehicle_service_details(vehicle_id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    services = []
    try:
        cursor.callproc('GetVehicleServiceDetails', [vehicle_id])
        for result in cursor.stored_results():
            services = result.fetchall()
    except Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        cursor.close()
        db.close()
    return render_template('vehicle_service_details.html', services=services, vehicle_id=vehicle_id)


# ---------- Delete Vehicle ----------
@app.route('/vehicles/delete/<int:v_id>', methods=['POST'])
def delete_vehicle(v_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("⚠ Only admin can delete vehicles.", "danger")
        return redirect(url_for('vehicles'))

    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM vehicle WHERE V_id = %s", (v_id,))
        db.commit()
        flash("🚗 Vehicle deleted successfully.", "info")
    except Error as e:
        flash(f"Can't delete vehicle: {e}", "danger")
    finally:
        cursor.close()
        db.close()
    return redirect(url_for('vehicles'))


# ---------- Payments ----------
@app.route('/payments')
def payments():
    if 'role' not in session or session['role'] != 'admin':
        flash("⚠ Only admin can view payments.", "danger")
        return redirect(url_for('dashboard'))

    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM payment ORDER BY Timestamp DESC")
        data = cursor.fetchall()
    except Error as e:
        flash(f"DB Error: {e}", "danger")
        data = []
    finally:
        cursor.close()
        db.close()
    return render_template('payments.html', payments=data)


# ---------- Add Payment ----------
@app.route('/add_payments', methods=['POST'])
def add_payments():
    if 'role' not in session or session['role'] != 'admin':
        flash("⚠ Only admin can add payments.", "danger")
        return redirect(url_for('dashboard'))

    record_id = request.form.get('record_id')
    mec_id = request.form.get('mechanic_id')
    amount = request.form.get('amount')
    payment_method = request.form.get('upi')
    payment_detail = request.form.get('credit_card')
    status = request.form.get('status', 'Pending')

    if not (record_id and mec_id and amount):
        flash("⚠ Record ID, Mechanic ID, and Amount are required.", "warning")
        return redirect(url_for('payments'))

    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO payment (Record_id, Mec_id, Amount, UPI, Credit_card, Timestamp, Status)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (record_id, mec_id, amount, payment_method, payment_detail, status))
        db.commit()
        flash("💰 Payment added successfully!", "success")
    except Error as e:
        db.rollback()
        flash(f"Database error: {e}", "danger")
    finally:
        cursor.close()
        db.close()
    return redirect(url_for('payments'))


# ---------- Run App ----------
if _name_ == '_main_':
    app.run(debug=True)
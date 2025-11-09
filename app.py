from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "replace_with_a_strong_secret"  # needed for flash messages


# ---------- Database Connection ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Prajwal@23",
        database="vehicle"
    )


# ---------- Home ----------
@app.route('/')
def index():
    return render_template('index.html')


# ---------- Show All Vehicles ----------
@app.route('/vehicles')
def vehicles():
    q = request.args.get('q', '').strip()
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        if q:
            sql = "SELECT * FROM Vehicle WHERE Model LIKE %s OR V_no LIKE %s"
            like = f"%{q}%"
            cursor.execute(sql, (like, like))
        else:
            cursor.execute("SELECT * FROM Vehicle")
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
    if request.method == 'POST':
        owner_id = request.form.get('owner_id')
        license_plate = request.form.get('license')
        model = request.form.get('model')
        milage = request.form.get('milage')
        v_no = request.form.get('v_no')

        if not (owner_id and license_plate and model and milage and v_no):
            flash("⚠️ All fields are required.", "warning")
            return redirect(url_for('vehicles'))

        db = get_connection()
        cursor = db.cursor()

        try:
            # ✅ Check if owner exists
            cursor.execute("SELECT Owner_id FROM Owner WHERE Owner_id = %s", (owner_id,))
            owner_exists = cursor.fetchone()

            # ✅ If not found, create dummy owner
            if not owner_exists:
                cursor.execute("""
                    INSERT INTO Owner (Owner_id, Name, Ph_no, Email, Address)
                    VALUES (%s, %s, %s, %s, %s)
                """, (owner_id, f'Owner {owner_id}', '0000000000', f'owner{owner_id}@example.com', 'Unknown Address'))

            # ✅ Insert vehicle record
            cursor.execute("""
                INSERT INTO Vehicle (Owner_id, License, Model, Milage, V_no)
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


# ---------- Vehicle Details ----------
@app.route('/vehicles/<int:v_id>')
def vehicle_detail(v_id):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Vehicle WHERE V_id = %s", (v_id,))
        vehicle = cursor.fetchone()
    except Error as e:
        flash(f"DB Error: {e}", "danger")
        vehicle = None
    finally:
        cursor.close()
        db.close()
    return render_template('vehicle_detail.html', vehicle=vehicle)


# ---------- Delete Vehicle ----------
@app.route('/vehicles/delete/<int:v_id>', methods=['POST'])
def delete_vehicle(v_id):
    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Vehicle WHERE V_id = %s", (v_id,))
        db.commit()
        flash("🚗 Vehicle deleted successfully.", "info")
    except Error as e:
        flash(f"Can't delete vehicle: {e}", "danger")
    finally:
        cursor.close()
        db.close()
    return redirect(url_for('vehicles'))


# ---------- Dashboard ----------
@app.route('/dashboard')
def dashboard():
    db = get_connection()
    cursor = db.cursor()
    stats = {}
    try:
        cursor.execute("SELECT COUNT(*) FROM Vehicle")
        stats['vehicles'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM payments")
        stats['payments'] = cursor.fetchone()[0]
        cursor.execute("SELECT IFNULL(SUM(Amount),0) FROM payments WHERE Status = 'Completed'")
        stats['total_collected'] = cursor.fetchone()[0]
    except Error as e:
        flash(f"DB Error: {e}", "danger")
        stats = {'vehicles': 0, 'payments': 0, 'total_collected': 0}
    finally:
        cursor.close()
        db.close()
    return render_template('dashboard.html', stats=stats)


# ---------- Payments ----------
@app.route('/payments')
def payments():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM payments ORDER BY Timestamp DESC")
        data = cursor.fetchall()
    except Error as e:
        flash(f"DB Error: {e}", "danger")
        data = []
    finally:
        cursor.close()
        db.close()
    return render_template('payments.html', payments=data)


# ---------- Add Payment (Fixed) ----------
@app.route('/add_payments', methods=['POST'])
def add_payments():
    record_id = request.form.get('record_id')
    mechanic_id = request.form.get('mechanic_id')
    amount = request.form.get('amount')
    upi = request.form.get('upi')
    credit_card = request.form.get('credit_card')
    status = request.form.get('status', 'Pending')

    if not (record_id and mechanic_id and amount):
        flash("⚠️ Record ID, Mechanic ID, and Amount are required.", "warning")
        return redirect(url_for('payments'))

    db = get_connection()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO payments (Record_id, Mec_id, Amount, UPI, Credit_card, Timestamp, Status)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (record_id, mechanic_id, amount, upi, credit_card, status))
        db.commit()
        flash("💰 payments added successfully!", "success")
    except Error as e:
        db.rollback()
        flash(f"Database error: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('payments'))


# ---------- Main ----------
if __name__ == '__main__':
    app.run(debug=True)

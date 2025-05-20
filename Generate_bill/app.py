from flask import Flask, render_template, request
import mysql.connector
from datetime import datetime, timedelta
import random
import calendar

app = Flask(__name__)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwas@2003",
        database="energy_data"
    )

# --- DATA GENERATION ---
def get_customer_ids():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT customer_id FROM masked_customer_data")
    customer_ids = cursor.fetchall()
    cursor.close()
    connection.close()
    return [cid[0] for cid in customer_ids]

def generate_daily_consumption_for_day():
    return random.uniform(5, 20)

def insert_daily_consumption(customer_id, date, consumption):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_daily_consumption (
            customer_id VARCHAR(20),
            date DATE,
            energy_consumption DECIMAL(5,2),
            PRIMARY KEY (customer_id, date)
        )
    """)
    cursor.execute("""
        INSERT INTO customer_daily_consumption (customer_id, date, energy_consumption)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE energy_consumption = VALUES(energy_consumption)
    """, (customer_id, date, consumption))
    connection.commit()
    cursor.close()
    connection.close()

def generate_and_insert_consumption(month, year):
    customer_ids = get_customer_ids()
    days_in_month = calendar.monthrange(year, month)[1]
    start_date = datetime(year, month, 1)

    for day in range(1, days_in_month + 1):
        current_date = start_date + timedelta(days=day - 1)
        for customer_id in customer_ids:
            consumption = generate_daily_consumption_for_day()
            insert_daily_consumption(customer_id, current_date.date(), consumption)

# --- BILLING CALCULATION ---
def create_billing_table():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_customer_bill (
            customer_id VARCHAR(20),
            month INT,
            year INT,
            total_units DECIMAL(10,2),
            energy_charge DECIMAL(10,2),
            fixed_charge DECIMAL(10,2),
            tax DECIMAL(10,2),
            total_bill DECIMAL(10,2),
            PRIMARY KEY (customer_id, month, year)
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

def calculate_and_store_bills(month, year):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT cdc.customer_id, SUM(cdc.energy_consumption), mcd.sanctioned_load
        FROM customer_daily_consumption cdc
        JOIN masked_customer_data mcd ON cdc.customer_id = mcd.customer_id
        WHERE MONTH(cdc.date) = %s AND YEAR(cdc.date) = %s
        GROUP BY cdc.customer_id
    """, (month, year))

    rows = cursor.fetchall()
    insert_query = """
        INSERT INTO monthly_customer_bill (
            customer_id, month, year, total_units,
            energy_charge, fixed_charge, tax, total_bill
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_units = VALUES(total_units),
            energy_charge = VALUES(energy_charge),
            fixed_charge = VALUES(fixed_charge),
            tax = VALUES(tax),
            total_bill = VALUES(total_bill)
    """

    for row in rows:
        customer_id, total_units, sanctioned_load = row
        if total_units is None or sanctioned_load is None:
            continue
        total_units = float(total_units)
        sanctioned_load = float(sanctioned_load)
        energy_charge = round(total_units * 6.0, 2)

        fixed_lookup = {1.0: 100, 1.5: 150, 2.0: 200, 3.0: 300}
        fixed_charge = fixed_lookup.get(sanctioned_load, 100)

        subtotal = energy_charge + fixed_charge
        tax = round(subtotal * 0.09, 2)
        total_bill = round(subtotal + tax, 2)

        cursor.execute(insert_query, (
            customer_id, month, year, total_units,
            energy_charge, fixed_charge, tax, total_bill
        ))

    connection.commit()
    cursor.close()
    connection.close()

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        try:
            month = int(request.form['month'])
            year = int(request.form['year'])
            if 1 <= month <= 12:
                generate_and_insert_consumption(month, year)
                create_billing_table()
                calculate_and_store_bills(month, year)
                message = f"✅ Bills generated for {calendar.month_name[month]} {year}."
            else:
                message = "❌ Invalid month value!"
        except Exception as e:
            message = f"❌ Error: {e}"
    return render_template("index.html", message=message)

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwas@2003",
        database="energy_data"
    )

@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    message = None  # Ensure 'message' is always defined
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            stored_password, role = result
            if stored_password.startswith("$2"):
                if bcrypt.checkpw(password.encode(), stored_password.encode()):
                    session['role'] = role
                    return redirect(url_for('customer'))
            elif password == stored_password:
                session['role'] = role
                return redirect(url_for('customer'))

        message = "Invalid username or password"

    return render_template('login.html', message=message)


@app.route('/customer', methods=['GET', 'POST'])
def customer():
    role = session.get('role')
    customer = None
    message = None

    if not role:
        return redirect(url_for('login'))

    if request.method == 'POST':
        customer_id = request.form['customer_id']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        table = "customer_data" if role == "admin" else "masked_customer_data"
        cursor.execute(f"SELECT * FROM {table} WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        cursor.close()
        conn.close()

        if not customer:
            message = "No data found for the given Customer ID."

    return render_template('customer.html', role=role, customer=customer, message=message)

if __name__ == '__main__':
    app.run(debug=True)

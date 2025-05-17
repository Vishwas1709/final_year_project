from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwas@2003",
        database="energy_data"
    )

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = (
            request.form['customer_id'],
            request.form['customer_name'],
            request.form['account_number'],
            request.form['email_id'],
            request.form['mobile_number'],
            request.form['address'],
            request.form['sanctioned_load']
        )
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO customer_data 
            (customer_id, customer_name, account_number, email_id, mobile_number, address, sanctioned_load)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data)

        connection.commit()
        cursor.close()
        connection.close()
        return "<h3 style='color:green;'>✅ Customer added successfully!</h3><a href='/'>Back</a>"

    except mysql.connector.Error as err:
        return f"<h3 style='color:red;'>❌ Error: {err}</h3><a href='/'>Back</a>"

if __name__ == '__main__':
    app.run(debug=True)

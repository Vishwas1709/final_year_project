from flask import Flask, request, render_template
import mysql.connector
from twilio.rest import Client
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Function to send SMS
def send_sms(to_number, message):
    if not to_number.startswith('+'):
        to_number = '+91' + to_number  # Add country code for Indian numbers

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')

    if not account_sid or not auth_token or not twilio_number:
        raise ValueError("Twilio credentials are missing from environment variables.")

    client = Client(account_sid, auth_token)

    try:
        sms = client.messages.create(
            body=message,
            from_=twilio_number,
            to=to_number
        )
        print(f"SMS sent to {to_number}, SID: {sms.sid}")
        return True
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False

# Route to show the send_bill form
@app.route('/')
def home():
    return render_template('send_bill.html')

# Route to handle bill sending
@app.route('/send-bill', methods=['POST'])
def send_bill():
    customer_id = request.form.get('customer_id')

    if not customer_id:
        return render_template('send_bill.html', message="Customer ID is required.")

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="vishwas@2003",  # Replace with your MySQL password
            database="energy_data"
        )
        cursor = conn.cursor()
        query = """
            SELECT 
                c.mobile_number, 
                m.month, 
                m.year, 
                m.total_units, 
                m.energy_charge, 
                m.fixed_charge, 
                m.tax, 
                m.total_bill
            FROM customer_data c
            JOIN monthly_customer_bill m ON c.customer_id = m.customer_id
            WHERE c.customer_id = %s
              AND (m.year, m.month) = (
                    SELECT MAX(year), MAX(month)
                    FROM monthly_customer_bill
                    WHERE customer_id = %s
                )
        """
        cursor.execute(query, (customer_id, customer_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            (
                mobile_number, month, year, total_units,
                energy_charge, fixed_charge, tax, total_bill
            ) = result

            message = (
                f"Hi {customer_id},\n"
                f"Month: {month}, Year: {year}\n"
                f"Units Used: {total_units}\n"
                f"Energy Charge: ₹{energy_charge}\n"
                f"Fixed Charge: ₹{fixed_charge}\n"
                f"Tax: ₹{tax}\n"
                f"Total Bill: ₹{total_bill}"
            )

            success = send_sms(mobile_number, message)
            status = "SMS sent successfully." if success else "Failed to send SMS."
            return render_template('send_bill.html', message=status)
        else:
            return render_template('send_bill.html', message="Customer ID not found or no bill available.")

    except Exception as e:
        return render_template('send_bill.html', message=f"Error: {e}")

if __name__ == '__main__':
    app.run(debug=True)



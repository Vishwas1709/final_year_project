import mysql.connector
from datetime import datetime

# Connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwas@2003",
        database="energy_data"
    )

# Create the billing table
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
    print("✅ Table 'monthly_customer_bill' ensured to exist.")

# Calculate and store monthly bills
def calculate_and_store_bills(month, year):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT cdc.customer_id, SUM(cdc.energy_consumption) AS total_units, 
                   mcd.sanctioned_load
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

            # Convert to float for safe calculations
            total_units = float(total_units)
            sanctioned_load = float(sanctioned_load)

            # Calculate billing components
            energy_charge = round(total_units * 6.0, 2)

            # Fixed charge mapping
            fixed_charge_lookup = {
                1.0: 100,
                1.5: 150,
                2.0: 200,
                3.0: 300
            }
            fixed_charge = fixed_charge_lookup.get(sanctioned_load, 100)

            subtotal = energy_charge + fixed_charge
            tax = round(subtotal * 0.09, 2)  # 9% GST
            total_bill = round(subtotal + tax, 2)

            # Insert or update record
            cursor.execute(insert_query, (
                customer_id, month, year, total_units,
                energy_charge, fixed_charge, tax, total_bill
            ))

        connection.commit()
        print("✅ Monthly billing data calculated and stored successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        cursor.close()
        connection.close()

# Main program
if __name__ == "__main__":
    month = int(input("Enter billing month (1-12): "))
    year = int(input("Enter billing year (e.g., 2025): "))

    if 1 <= month <= 12:
        create_billing_table()
        calculate_and_store_bills(month, year)
    else:
        print("❌ Invalid month input. Please enter a value between 1 and 12.")

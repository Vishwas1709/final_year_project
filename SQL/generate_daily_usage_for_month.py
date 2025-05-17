import mysql.connector
import random
from datetime import datetime, timedelta
import calendar

# Function to connect to MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwas@2003",
        database="energy_data"
    )

# Function to get customer_ids from masked_customer_data
def get_customer_ids():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT customer_id FROM masked_customer_data")
    customer_ids = cursor.fetchall()
    cursor.close()
    connection.close()
    return [customer_id[0] for customer_id in customer_ids]

# Function to generate energy consumption for a specific day in the month
def generate_daily_consumption_for_day():
    return random.uniform(5, 20)  # Random consumption between 5 to 20 kWh

# Function to insert daily consumption into MySQL
def insert_daily_consumption(customer_id, current_date, consumption):
    connection = connect_db()
    cursor = connection.cursor()

    # Ensure the table `customer_daily_consumption` exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_daily_consumption (
            customer_id VARCHAR(20),
            date DATE,
            energy_consumption DECIMAL(5,2),
            PRIMARY KEY (customer_id, date)
        )
    """)

    # Insert the daily energy consumption for each customer
    cursor.execute("""
        INSERT INTO customer_daily_consumption (customer_id, date, energy_consumption)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE energy_consumption = VALUES(energy_consumption)
    """, (customer_id, current_date, consumption))

    connection.commit()
    cursor.close()
    connection.close()

# Main function to generate and insert energy consumption data day by day
def generate_and_insert_consumption(month, year):
    customer_ids = get_customer_ids()
    
    # Calculate the number of days in the month, accounting for leap years in February
    if month == 2:
        if calendar.isleap(year):
            days_in_month = 29
        else:
            days_in_month = 28
    else:
        days_in_month = calendar.monthrange(year, month)[1]
    
    # Start from 1st day of the month
    start_date = datetime(year, month, 1)

    # Insert daily energy consumption data day by day for all customers
    for day in range(1, days_in_month + 1):
        current_date = start_date + timedelta(days=day-1)  # Increment date for each day
        print(f"Generating data for {calendar.month_name[month]} {day}, {year}")
        
        for customer_id in customer_ids:
            consumption = generate_daily_consumption_for_day()
            print(f"  Inserting consumption for customer {customer_id} on {current_date.date()}: {consumption:.2f} kWh")
            insert_daily_consumption(customer_id, current_date.date(), consumption)

    print("Data generation and insertion complete.")

# Example usage
if __name__ == "__main__":
    month = int(input("Enter month number (1-12): "))
    year = int(input("Enter year: "))
    
    if 1 <= month <= 12:
        generate_and_insert_consumption(month, year)
    else:
        print("Invalid month. Please enter a month between 1 and 12.")

import pandas as pd
import random
import os
from faker import Faker
import re
import mysql.connector

fake = Faker()
Faker.seed(42)
random.seed(42)

def sanitize_name(name):
    return re.sub(r'[^a-z]', '', name.lower())

def generate_custom_customer_id(name, suffix_num):
    base = sanitize_name(name)[:4]
    return f"{base}{suffix_num:04d}"

def generate_unique_account_number(used_accounts):
    while True:
        account_number = random.randint(10**9, 10**10 - 1)
        if account_number not in used_accounts:
            used_accounts.add(account_number)
            return account_number

def generate_customers(num_customers=50):
    data = []
    used_names = set()
    used_accounts = set()
    allowed_kwh_values = [1, 1.5, 2, 3]

    for i in range(1, num_customers + 1):
        while True:
            name = fake.unique.name()
            if name not in used_names:
                used_names.add(name)
                break

        sanitized_name = sanitize_name(name)
        customer_id = generate_custom_customer_id(name, i)
        account_number = generate_unique_account_number(used_accounts)
        email = f"{sanitized_name}{i}@example.com"
        mobile_number = f"9{random.randint(100000000, 999999999)}"
        address = fake.address().replace("\n", ", ")
        sanctioned_load = random.choice(allowed_kwh_values)

        data.append((
            customer_id,
            name,
            account_number,
            email,
            mobile_number,
            address,
            sanctioned_load
        ))

    return data

def insert_into_mysql(data):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwas@2003",
        database="energy_data"
    )
    cursor = connection.cursor()

    insert_query = """
    INSERT INTO customer_daily_usage (
        customer_id, customer_name, account_number, email_id,
        mobile_number, address, sanctioned_load
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(insert_query, data)
    connection.commit()
    cursor.close()
    connection.close()
    print("✅ 50 customer records inserted into MySQL table.")

# Generate and insert
customers = generate_customers()
insert_into_mysql(customers)

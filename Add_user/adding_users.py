from flask import Flask, request, render_template
import bcrypt
import mysql.connector

app = Flask(__name__)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def insert_user(username, password, role):
    hashed_password = hash_password(password)

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwas@2003",  # Your MySQL password
        database="energy_data"
    )
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, hashed_password.decode('utf-8'), role)
        )
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

# Route to display registration form
@app.route('/')
def show_form():
    return render_template('register_user.html')

# Route to handle form submission
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password or not role:
        return render_template('register_user.html', message="All fields are required.")

    if role not in ['admin', 'user']:
        return render_template('register_user.html', message="Invalid role.")

    success = insert_user(username, password, role)

    if success:
        return render_template('register_user.html', message="User registered successfully!")
    else:
        return render_template('register_user.html', message="Failed to register user.")

if __name__ == '__main__':
    app.run(debug=True)

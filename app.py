from werkzeug.security import generate_password_hash
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import os
import base64
from flask_mysqldb import MySQL
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session
import MySQLdb
from functools import wraps

app = Flask(__name__)
app.secret_key = 'e9b7c2d7d8f5e6c5a4b3c8d9e7f6a9b2'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'devnetx_contentus_db'

mysql = MySQL(app)

# Function to check if the user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or not session['loggedin']:
            flash('You must be logged in to view this page!', 'danger')
            return redirect(url_for('employee_login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to hash the password using Scrypt
def hash_password(password: str, salt: bytes):
    password_bytes = password.encode('utf-8')
    kdf = Scrypt(
        length=32,
        salt=salt,
        n=32768,
        r=8,
        p=1,
        backend=default_backend()
    )
    hashed_password = kdf.derive(password_bytes)
    return hashed_password

# Function to verify the password using Scrypt
def verify_password(stored_hash, password: str, salt: bytes):
    kdf = Scrypt(
        length=32,
        salt=salt,
        n=32768,
        r=8,
        p=1,
        backend=default_backend()
    )
    try:
        kdf.verify(password.encode('utf-8'), stored_hash)
        return True
    except Exception:
        return False

# Register Route
@app.route('/employee_register', methods=['GET', 'POST'])
def employee_register():
    if request.method == "POST":
        userName = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employee WHERE username = %s OR email = %s', (userName, email))
        account = cursor.fetchone()

        if account:
            flash('Account already exists!')
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Invalid email address!')
        elif not userName or not password or not email:
            flash('Please fill all the inputs!')
        elif password != confirm_password:
            flash('Passwords do not match!')
        else:
            salt = os.urandom(16)
            hashed_password = hash_password(password, salt)
            hashed_password_encoded = base64.b64encode(hashed_password).decode('utf-8')

            # Insert data into the database
            cursor.execute('INSERT INTO employee (username, email, password, salt) VALUES (%s, %s, %s, %s)', 
                           (userName, email, hashed_password_encoded, salt))
            mysql.connection.commit()
            flash('You have successfully registered!')
            return redirect(url_for('employee_login'))

        cursor.close()

    return render_template('register.html')

# Login Route
@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    message = ''
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employee WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user:
            stored_hash = base64.b64decode(user['password'])
            salt = user['salt']

            if verify_password(stored_hash, password, salt):
                session['loggedin'] = True
                session['id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                message = 'Logged in successfully!'
                cursor.close()
                return redirect(url_for('dashboard'))
            else:
                message = 'Invalid username or password'
        else:
            message = 'User not found or password incorrect'

        cursor.close()

    return render_template('login.html', message=message)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('employee_login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('base1.html')

@app.route('/Customer_Message')
@login_required
def Customer_Message():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, firstName, email, Message, created_at FROM contacts ORDER BY created_at")
    contacts = cur.fetchall()
    cur.close()
    return render_template('Contactus.html', contacts=contacts)

@app.route("/<int:id>/customer", methods=['POST'])
@login_required
def deletecustomer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM contacts WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('Customer_Message'))

@app.route('/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fname = request.form['firstName']
        lname = request.form['lastName']
        email = request.form['Email']
        subject = request.form['Subject']
        message = request.form['Message']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contacts (firstName, lastName, Email, Subject, Message) VALUES (%s, %s, %s, %s, %s)", 
                    (fname, lname, email, subject, message))
        mysql.connection.commit()
        cur.close()
        
        flash('Your message has been sent successfully!')
        return redirect(url_for('contact'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

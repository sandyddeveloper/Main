from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'e9b7c2d7d8f5e6c5a4b3c8d9e7f6a9b2'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'devnetx_contentus_db'

mysql = MySQL(app)

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data
        fname = request.form.get('firstName')
        lname = request.form.get('lastName')
        email = request.form.get('Email')
        subject = request.form.get('Subject')
        message = request.form.get('Message')
        
        # Basic form validation
        if not fname or not lname or not email  or not message:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('contact'))
        
        try:
            # Insert the form data into the database
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO contacts (firstName, lastName, Email, Subject, Message) VALUES (%s, %s, %s, %s, %s)",
                (fname, lname, email, subject, message)
            )
            mysql.connection.commit()
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()  # Roll back in case of error
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            cur.close()
        
        return redirect(url_for('contact'))
    
    # Render the contact form for GET requests
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, firstname, email,message, created_at FROM contacts ORDER BY created_at")
    contacts = cur.fetchall()

    cur.close()
    return render_template('dashboard.html', contacts=contacts)

@app.route("/<int:id>/customer", methods=['POST'])
def deletecustomer(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM contacts WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('dashboard'))  

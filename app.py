from flask import Flask, request, redirect, url_for, flash, get_flashed_messages, session
import sqlite3
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'  # Used for session management

DB_FILE = "users.db"
LOG_FILE = "login_attempts.csv"

# Create database and log file if they don't exist
def setup_database():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        # Insert an example user (admin, password123) if not exists
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'password123')")
        conn.commit()
        conn.close()

def setup_log_file():
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'username', 'password', 'success'])  # Log file headers

setup_database()
setup_log_file()

# Function to log login attempts
def log_attempt(username, password, success):
    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now().isoformat(), username, password, success])

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check credentials in database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)  # ❌ Vulnerable to SQL Injection!

        user = cursor.fetchone()
        conn.close()

        success = bool(user)
        log_attempt(username, password, success)  # Log attempt

        if success:
            session['username'] = username  # Store logged-in user
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.")
            return redirect(url_for('login'))

    messages = get_flashed_messages()
    message_html = ""
    if messages:
        message_html = f"""
        <div class="alert alert-danger text-center" role="alert">
            {" ".join(messages)}
        </div>
        """

    return f"""
    <html>
        <head>
            <title>Login Page</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
            <style>
                body {{
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 400px;
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
            </style>
        </head>
        <body class="d-flex align-items-center justify-content-center vh-100">
            <div class="container">
                <h2 class="text-center mb-4">Login</h2>
                {message_html}
                <form method="post">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username:</label>
                        <input type="text" id="username" name="username" class="form-control" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">Password:</label>
                        <input type="password" id="password" name="password" class="form-control" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                <p class="text-center mt-3"><a href="/register">Create an Account</a></p>
            </div>
        </body>
    </html>
    """


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    
    return f"""
    <html>
        <head>
            <title>Dashboard</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        </head>
        <body class="d-flex align-items-center justify-content-center vh-100">
            <div class="text-center">
                <h2 class="text-success">Welcome, {username}!</h2>
                <a href="/change_password" class="btn btn-warning">Change Password</a>
                <br><br>
                <a href="/logout" class="btn btn-danger">Logout</a>
            </div>
        </body>
    </html>
    """

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in

    username = session['username']  # Get logged-in username

    if request.method == 'POST':
        new_password = request.form.get('new_password')

        if not new_password:
            flash("Password cannot be empty.")
            return redirect(url_for('change_password'))

        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # ✅ Secure Query to Update Password
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        conn.close()

        flash("Password updated successfully!")
        return redirect(url_for('dashboard'))  # Redirect to dashboard after update

    return f"""
    <html>
        <head>
            <title>Change Password</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        </head>
        <body class="d-flex align-items-center justify-content-center vh-100">
            <div class="container">
                <h2 class="text-center">Change Password for {username}</h2>
                <form method="post">
                    <label class="form-label">New Password:</label>
                    <input type="password" name="new_password" required class="form-control">
                    <br>
                    <button type="submit" class="btn btn-success w-100">Update Password</button>
                </form>
                <br>
                <a href="/dashboard" class="btn btn-secondary w-100">Back to Dashboard</a>
            </div>
        </body>
    </html>
    """


# ✅ New Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username already exists
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already taken. Please choose another.")
            conn.close()
            return redirect(url_for('register'))

        # Insert new user
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        flash("Account created successfully! You can now log in.")
        return redirect(url_for('login'))

    messages = get_flashed_messages()
    message_html = ""
    if messages:
        message_html = f"""
        <div class="alert alert-danger text-center" role="alert">
            {" ".join(messages)}
        </div>
        """

    return f"""
    <html>
        <head>
            <title>Register</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
            <style>
                body {{
                    background-color: #f8f9fa;
                }}
                .container {{
                    max-width: 400px;
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
            </style>
        </head>
        <body class="d-flex align-items-center justify-content-center vh-100">
            <div class="container">
                <h2 class="text-center mb-4">Create an Account</h2>
                {message_html}
                <form method="post">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username:</label>
                        <input type="text" id="username" name="username" class="form-control" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">Password:</label>
                        <input type="password" id="password" name="password" class="form-control" required>
                    </div>
                    
                    <button type="submit" class="btn btn-success w-100">Create Account</button>
                </form>
                <p class="text-center mt-3"><a href="/">Back to Login</a></p>
            </div>
        </body>
    </html>
    """

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

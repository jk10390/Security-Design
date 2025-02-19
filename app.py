from flask import Flask, request, redirect, url_for, flash, get_flashed_messages, session, render_template_string
import sqlite3
import os
import csv
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'

DB_FILE = "users.db"
LOG_FILE = "login_attempts.csv"

# ✅ Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jacobwkennedy@gmail.com'  
app.config['MAIL_PASSWORD'] = 'ouoy egmj feyu ayzs'  
app.config['MAIL_DEFAULT_SENDER'] = 'jacobwkennedy@gmail.com'

mail = Mail(app)

# ✅ Ensure the database exists and includes an email column
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Ensure 'email' column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "email" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
    
    conn.close()

setup_database()

# ✅ Ensure log file exists
def setup_log_file():
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'username', 'password', 'success'])

setup_log_file()

# ✅ Function to log login attempts
def log_attempt(username, password, success):
    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now().isoformat(), username, password, str(success)])

# 🔥 Login Route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        success = bool(user)
        log_attempt(username, password, success)

        if success:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    messages = get_flashed_messages()
    message_html = "".join(f"<p style='color:red;'>{msg}</p>" for msg in messages)

    return f"""
    <html>
        <head><title>Login</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    </head>
        <body>
			<div style="text-align: center;">
            <h2>Login</h2>
            {message_html}
            <form method="post">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
                <br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
                <br>
                <br>
                <button type="submit">Login</button>
                <br>
            </form>
            <p><a href="/forgot_password" class="btn btn-dark">Forgot Password?</a></p>
            <p><a href="/register" class="btn btn-dark">Create an Account</a></p>
            </div>
        </body>
    </html>
    """

# 🔥 Dashboard Route (Users See Their Own Data, Admin Sees Everything)
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    is_admin = (username == 'admin')

    # 🔄 Auto-refresh JavaScript for admin
    refresh_script = """
    <script>
        function refreshData() {
            fetch('/api/get_login_attempts')
                .then(response => response.text())
                .then(data => {
                    document.getElementById("loginTableBody").innerHTML = data;
                });
        }
        setInterval(refreshData, 5000);
        window.onload = refreshData;
    </script>
    """ if is_admin else ""

    return f"""
    <html>
        <head>
			<div style="text-align: center;">
            <title>Dashboard</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
            {refresh_script}
        </head>
        <body class="container mt-5">
            <h2>Welcome, {username}!</h2>
            <a href="/change_password" class="btn btn-warning">Change Password</a>
            <a href="/" class="btn btn-danger">Logout</a>

            {"<h3 class='mt-4'>Registered Users</h3>" if is_admin else ""}
            {"<table class='table table-striped'><thead><tr><th>Username</th><th>Email</th><th>Password</th></tr></thead><tbody>" + get_users() + "</tbody></table>" if is_admin else ""}

            <h3 class="mt-4">Recent Login Attempts</h3>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Password</th>
                        <th>Success</th>
                    </tr>
                </thead>
                <tbody id="loginTableBody">
                    {get_login_attempts(username, is_admin)}
                </tbody>
            </table>
        </body>
    </html>
    """

# 🔥 Register Route (Includes Email)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already taken.")
            conn.close()
            return redirect(url_for('register'))

        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        conn.close()

        flash("Account created successfully!")
        return redirect(url_for('login'))

    messages = get_flashed_messages()
    message_html = "".join(f"<p style='color:red;'>{msg}</p>" for msg in messages)

    return f"""
    <html>
		<div style="text-align: center;">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <head><title>Register</title></head>
        <body>
            <h2>Create an Account</h2>
            {message_html}
            <form method="post">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
                <br>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                <br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
                <br>
                <br>
                <button type="submit">Register</button>
            </form>
            <p><a href="/" class="btn btn-warning">Back to Login</a></p>
        </body>
    </html>
    """


# 🔥 Forgot Password Route (Sends Plaintext Credentials)
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            username, password = user  # Retrieve username and password from database

            # ✅ Send email with plaintext credentials
            msg = Message("Your Account Credentials", recipients=[email])
            msg.body = f"Here are your login details:\n\nUsername: {username}\nPassword: {password}\n\nPlease keep this information secure."
            mail.send(msg)

            flash("Your credentials have been sent to your email.")
            return redirect(url_for('forgot_password'))

        else:
            flash("Email not found.")
            return redirect(url_for('forgot_password'))

    return """
    <html>
		<div style="text-align: center;">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <head><title>Forgot Password</title></head>
        <body>
            <h2>Forgot Password</h2>
            <form method="post">
                <label for="email">Enter your email:</label>
                <input type="email" id="email" name="email" required>
                <button type="submit">Submit</button>
            </form>
            <p><a href="/" class="btn btn-danger">Back to Login</a></p>
        </body>
    </html>
    """


# 🔥 Change Password Route
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        new_password = request.form.get('new_password')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        conn.close()

        flash("Password updated successfully!")
        return redirect(url_for('dashboard'))

    return f"""
    <html>
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <div style="text-align: center;">
        <head><title>Change Password</title></head>
        <body>
            <h2>Change Password</h2>
            <form method="post">
                <label for="new_password">New Password:</label>
                <br>
                <input type="password" id="new_password" name="new_password" required>
                <br>
                <br>
                <button type="submit" class="btn btn-dark">Update Password</button>
            </form>
            <p><a href="/dashboard" class="btn btn-danger">Back to Dashboard</a></p>
        </body>
    </html>
    """

# ✅ API to Get Login Attempts for Auto-Refresh
@app.route('/api/get_login_attempts')
def api_get_login_attempts():
    if 'username' not in session:
        return "Unauthorized", 403
    
    username = session['username']
    is_admin = (username == 'admin')

    return get_login_attempts(username, is_admin)

# ✅ Function to Retrieve Users from Database (Admin Only)
def get_users():
    users_html = ""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, password FROM users")
    for row in cursor.fetchall():
        users_html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
    conn.close()
    return users_html

# ✅ Function to Retrieve Login Attempts (Users See Their Own, Admin Sees All)
def get_login_attempts(current_user, is_admin):
    attempts_html = ""
    try:
        with open(LOG_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if is_admin or row["username"] == current_user:
                    success_class = "text-success" if row["success"] == "True" else "text-danger"
                    attempts_html += f"<tr><td>{row['username']}</td><td>{row['password']}</td><td class='{success_class}'>{row['success']}</td></tr>"
    except FileNotFoundError:
        attempts_html = "<tr><td colspan='3'>No login attempts found.</td></tr>"

    return attempts_html

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, redirect, url_for, flash, get_flashed_messages

import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'  # Used for session management and flash messages

# Hardcoded valid credentials for demonstration purposes.
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'password123'

# Log file to store login attempts.
LOG_FILE = 'login_attempts.csv'

def log_attempt(username, password, accepted):
    """
    Append a login attempt to the CSV log file.
    The CSV contains a header with:
      timestamp, username, password, accepted
    """
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'username', 'password', 'accepted']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'password': password,
            'accepted': accepted
        })

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Determine if the login is accepted.
        accepted = (username == VALID_USERNAME and password == VALID_PASSWORD)
        
        # Log the attempt.
        log_attempt(username, password, accepted)
        
        if accepted:
            return f"""
            <html>
                <head>
                    <title>Login Successful</title>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
                </head>
                <body class="d-flex align-items-center justify-content-center vh-100">
                    <div class="text-center">
                        <h2 class="text-success">Login Successful!</h2>
                        <p>Welcome, {username}.</p>
                        <a href="/" class="btn btn-primary">Logout</a>
                    </div>
                </body>
            </html>
            """
        else:
            flash("Invalid username or password. Please try again.")
            return redirect(url_for('login'))
    
    # Build the login page HTML.
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
                .login-container {{
                    max-width: 400px;
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
            </style>
        </head>
        <body class="d-flex align-items-center justify-content-center vh-100">
            <div class="login-container">
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
            </div>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Run the Flask app on localhost, port 5000 by default.
    app.run(debug=True)

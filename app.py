from flask import Flask, request, redirect, url_for, flash, get_flashed_messages
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'  # Used for session management and flash messages

# Hardcoded valid credentials and key for demonstration purposes.
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'password123'
VALID_KEY      = 'mysecretkey'

# Log file to store login attempts.
LOG_FILE = 'login_attempts.csv'

def log_attempt(username, password, key, accepted):
    """
    Append a login attempt to the CSV log file.
    The CSV contains a header with:
      timestamp, username, password, key, accepted
    """
    # Check if the file already exists so we can write the header if needed.
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'username', 'password', 'key', 'accepted']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'password': password,
            'key': key,
            'accepted': accepted
        })

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        key      = request.form.get('key')
        
        # Determine if the login is accepted.
        accepted = (username == VALID_USERNAME and
                    password == VALID_PASSWORD and
                    key == VALID_KEY)
        
        # Log the attempt (including credentials and the result).
        log_attempt(username, password, key, accepted)
        
        if accepted:
            return f"""
            <html>
                <head><title>Login Successful</title></head>
                <body>
                    <h2>Login Successful!</h2>
                    <p>Welcome, {username}.</p>
                </body>
            </html>
            """
        else:
            flash("Invalid username, password, or key. Please try again.")
            return redirect(url_for('login'))
    
    # Build the login page HTML.
    messages = get_flashed_messages()
    message_html = ""
    if messages:
        message_html = "<p style='color:red;'>{}</p>".format(" ".join(messages))
    
    return f"""
    <html>
        <head>
            <title>Login Page</title>
        </head>
        <body>
            <h2>Login Form</h2>
            {message_html}
            <form method="post">
                <label for="username">Username:</label><br>
                <input type="text" id="username" name="username" required><br><br>
                
                <label for="password">Password:</label><br>
                <input type="password" id="password" name="password" required><br><br>
                
                <label for="key">Key:</label><br>
                <input type="text" id="key" name="key" required><br><br>
                
                <input type="submit" value="Login">
            </form>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Run the Flask app on localhost, port 5000 by default.
    app.run(debug=True)

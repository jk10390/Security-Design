from flask import Flask, request, redirect, url_for, flash, get_flashed_messages
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'  # Used for session management and flash messages

DB_FILE = "users.db"

# Create an insecure database with a plaintext password field
def setup_database():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        # Insert an example user (admin, password123)
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
        conn.commit()
        conn.close()

setup_database()  # Ensure database exists

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # ❌ Insecure SQL Query (Vulnerable to SQL Injection)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()

        if user:
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

    # Build the login page HTML
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
    app.run(debug=True)

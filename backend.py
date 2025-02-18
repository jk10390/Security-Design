from flask import Flask, jsonify, render_template_string
import sqlite3
import csv
import os

app = Flask(__name__)

DB_FILE = "users.db"
LOG_FILE = "login_attempts.csv"

@app.route('/')
def home():
    return "<h3>Welcome to the Login Monitoring Dashboard! <br> <a href='/database_view'>View Database</a></h3>"

@app.route('/api/login_attempts')
def api_login_attempts():
    """API to get login attempts as JSON (without timestamps)"""
    attempts = []
    try:
        with open(LOG_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                attempts.append({
                    "username": row['username'],
                    "password": row['password'],
                    "success": row['success']
                })
    except FileNotFoundError:
        return jsonify([])  # Return empty JSON list if no file

    return jsonify(attempts)

@app.route('/api/users')
def api_users():
    """API to get users and passwords from the database as JSON"""
    users = []
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users")
    for row in cursor.fetchall():
        users.append({"username": row[0], "password": row[1]})
    conn.close()
    return jsonify(users)

@app.route('/database_view')
def view_database():
    """ Dashboard that displays both login attempts and users """
    html_template = """
    <html>
        <head>
            <title>Database View</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
            <script>
                function fetchData() {
                    // Fetch login attempts
                    fetch('/api/login_attempts')
                        .then(response => response.json())
                        .then(data => {
                            let tableBody = document.getElementById('loginTableBody');
                            tableBody.innerHTML = '';  // Clear table before updating

                            data.forEach(attempt => {
                                let row = `<tr>
                                    <td>${attempt.username}</td>
                                    <td>${attempt.password}</td>
                                    <td class="${attempt.success === 'True' ? 'text-success' : 'text-danger'}">
                                        ${attempt.success}
                                    </td>
                                </tr>`;
                                tableBody.innerHTML += row;
                            });
                        })
                        .catch(error => console.error('Error fetching login attempts:', error));

                    // Fetch users
                    fetch('/api/users')
                        .then(response => response.json())
                        .then(data => {
                            let userTableBody = document.getElementById('userTableBody');
                            userTableBody.innerHTML = '';  // Clear table before updating

                            data.forEach(user => {
                                let row = `<tr>
                                    <td>${user.username}</td>
                                    <td>${user.password}</td>
                                </tr>`;
                                userTableBody.innerHTML += row;
                            });
                        })
                        .catch(error => console.error('Error fetching users:', error));
                }

                setInterval(fetchData, 5000);  // Refresh every 5 seconds
                window.onload = fetchData;  // Load data on page load
            </script>
            <style>
                body {
                    background-color: #f8f9fa;
                    padding: 20px;
                }
                .container {
                    max-width: 900px;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                table {
                    width: 100%;
                }
                th, td {
                    padding: 10px;
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2 class="text-center">Database Overview</h2>
                <p class="text-center text-muted">This page updates every 5 seconds.</p>

                <h3>Login Attempts</h3>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Password</th>
                            <th>Success</th>
                        </tr>
                    </thead>
                    <tbody id="loginTableBody">
                        <!-- Table data will be loaded here by JavaScript -->
                    </tbody>
                </table>

                <h3>Registered Users</h3>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Password</th>
                        </tr>
                    </thead>
                    <tbody id="userTableBody">
                        <!-- Table data will be loaded here by JavaScript -->
                    </tbody>
                </table>

                <a href="/" class="btn btn-primary">Back to Home</a>
            </div>
        </body>
    </html>
    """
    
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Runs on port 5001

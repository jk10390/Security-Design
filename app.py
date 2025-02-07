from flask import Flask, request, redirect, url_for, flash, get_flashed_messages

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'  # Used for session management and flash messages

# Hardcoded valid credentials and key for demonstration purposes
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'password123'
VALID_KEY      = 'mysecretkey'

@app.route('/', methods=['GET', 'POST'])
def login():
    # If the form is submitted...
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        key      = request.form.get('key')
        
        # Check if all credentials are correct
        if username == VALID_USERNAME and password == VALID_PASSWORD and key == VALID_KEY:
            return """
            <html>
                <head><title>Login Successful</title></head>
                <body>
                    <h2>Login Successful!</h2>
                    <p>Welcome, {}.</p>
                </body>
            </html>
            """.format(username)
        else:
            flash("Invalid username, password, or key. Please try again.")
            return redirect(url_for('login'))
    
    # Build the login page HTML.
    # Note: In a production app you would normally use templates.
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

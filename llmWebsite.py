from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from bs4 import BeautifulSoup
import openai
import os

app = Flask(__name__, template_folder="templates")

# OpenAI API Key (Replace with your actual API key)
OPENAI_API_KEY = "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"
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get("website_url")
    if not url:
        return jsonify({"error": "No URL provided"})
    
    try:
        # Fetch the website source code
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        frontend_code = soup.prettify()
        
        # Send to OpenAI for analysis
        prompt = f"""
        Analyze this front-end code for security flaws and recommend fixes. Also, generate security testing scripts for:
        - Cross-Site Scripting (XSS)
        - Cross-Site Request Forgery (CSRF)
        - SQL Injection
        - Broken Authentication
        - Security Misconfigurations
        {frontend_code}
        """
        
        llm_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert analyzing front-end security."},
                {"role": "user", "content": prompt}
            ]
        )
        
        analysis_result = llm_response.choices[0].message.content
        return render_template("results.html", url=url, analysis_result=analysis_result)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching website: {str(e)}"})
    except Exception as e:
        return jsonify({"error": f"Analysis error: {str(e)}"})

if __name__ == '__main__':
    os.makedirs("templates", exist_ok=True)
    with open("templates/index.html", "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>Web Security Analyzer</title>
            <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'>
            <style>
                body {
                    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                    font-family: 'Arial', sans-serif;
                    color: white;
                    text-align: center;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.2);
                    width: 50%;
                }
                input {
                    width: 80%;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    margin: 10px 0;
                }
                button {
                    background-color: #ff5733;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: 0.3s;
                }
                button:hover {
                    background-color: #c70039;
                }
            </style>
        </head>
        <body>
            <div class='container'>
                <h1>Web Security Analyzer</h1>
                <p>Enter a website URL to analyze its security</p>
                <form method='post' action='/analyze' onsubmit='showLoading()'>
                    <input type='text' name='website_url' placeholder='Enter website URL...'>
                    <button type='submit'>Analyze</button>
                </form>
                <div id='loading' style='display: none;'>
                    <p>Analyzing... Please wait.</p>
                    <progress></progress>
                </div>
                <script>
                    function showLoading() {
                        document.getElementById('loading').style.display = 'block';
                    }
                </script>
            </div>
        </body>
        </html>
        """)
    
    with open("templates/results.html", "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>Analysis Results</title>
            <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'>
            <style>
                body {
                    background: #1a1a2e;
                    color: white;
                    font-family: 'Arial', sans-serif;
                    text-align: center;
                    padding: 20px;
                }
                .container {
                    max-width: 800px;
                    margin: auto;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.2);
                }
                .section {
                    background: rgba(255, 255, 255, 0.2);
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 5px;
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <div class='container'>
                <h1>Analysis Report</h1>
                <p>URL: {{ url }}</p>
                {% for section in analysis_result.split('\n\n') %}
                    <div class='section'>{{ section }}</div>
                {% endfor %}
                <br>
                <a href='/'>Back to Home</a>
            </div>
        </body>
        </html>
        """)
    
    app.run(debug=True, port=5001)

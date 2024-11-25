from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# Home Route - displays the login or signup page
@app.route('/')
def home():
    return render_template('login.html')

# Signup Route - handles the signup form submission
@app.route('/signup', methods=['POST'])
def signup():
    # Here you would normally save the user to the database
    # For now, we just simulate it by redirecting to the welcome page
    return redirect(url_for('welcome'))

# Login Route - handles the login form submission
@app.route('/login', methods=['POST'])
def login():
    # Normally, you'd validate credentials here (e.g., check username and password)
    # For now, we simulate success by redirecting to the welcome page
    return redirect(url_for('welcome.html'))

# Welcome Route - displays the welcome page after login or signup
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)

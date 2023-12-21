from flask import Flask, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)

# Secret key for session management (should be kept secret in a real application)
app.secret_key = 'your_secret_key'

# Read user data from the CSV file
def read_user_data():
    user_data = {}
    with open('data/users.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            user_data[row['username']] = row['password']
    return user_data

users = read_user_data()  # Initialize the users dictionary from the CSV file

# Define a route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            # Authentication successful, store the username in the session
            session['username'] = username
            return redirect(url_for('home'))
        else:
            # Authentication failed, display an error message
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)


# Define a route for a homepage
@app.route('/home')
def home():
    # Replace 'user1' with the actual username of the logged-in user
    # username = session['username']
    username = 'user1' # testing purposes
    return render_template('home.html', username=username)


if __name__ == '__main__':
    app.run()

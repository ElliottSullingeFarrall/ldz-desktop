from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------------------------------- Classes --------------------------------- #

class Users:
    def __init__(self):
        self.path = 'data/users.csv'
    def __enter__(self):
        self.data = pd.read_csv(self.path)
        return self.data
    def __exit__(self, exception_type, exception_value, exception_traceback):
        del self

# ----------------------------------- Pages ---------------------------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with Users() as users:
            user = users.loc[users.username == username].to_dict('records')[0]
            if password == user['password']:
                # Authentication successful, store the username in the session
                session['username'] = user['username']
                session['admin'] = bool(user['admin'])
                return redirect(url_for('home'))
            else:
                # Authentication failed, display an error message
                return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)

@app.route('/home', methods=['GET', 'POST'])
def home():
    # Testing
    # session['username'] = 'admin'
    # session['admin'] = True
    return render_template('home.html', username=session['username'], admin=session['admin'])

@app.route('/masa_reg', methods=['GET', 'POST'])
def masa_reg():
    return render_template('masa_reg.html', error=None, username=session['username'], admin=session['admin'])

@app.route('/masa_emb', methods=['GET', 'POST'])
def masa_emb():
    return render_template('masa_emb.html', error=None, username=session['username'], admin=session['admin'])

@app.route('/asnd_reg', methods=['GET', 'POST'])
def asnd_reg():
    return render_template('asnd_reg.html', error=None, username=session['username'], admin=session['admin'])

@app.route('/asnd_emb', methods=['GET', 'POST'])
def asnd_emb():
    return render_template('asnd_emb.html', error=None, username=session['username'], admin=session['admin'])

# ----------------------------------- Main ----------------------------------- #

if __name__ == '__main__':
    app.run()

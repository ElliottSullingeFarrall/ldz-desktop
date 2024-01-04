from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os.path as path
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------------------------------- Classes --------------------------------- #

class Users:
    def __init__(self):
        self.path = Path('data')
        self.file = Path('users.csv')
    def __enter__(self):
        self.data = pd.read_csv(self.path / self.file, index_col=False)
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        del self

    def login(self, username, password):
        # Check for user in database
        user = self.data.loc[self.data.username == username].to_dict('records')
        if len(user) == 1:
            user = user[0]
        else:
            return 'User not found!'
        
        # Check user password and login
        if password == user['password']:
            session['username'] = user['username']
            session['admin'] = bool(user['admin'])
        else:
            return 'Password invalid!'

class Appts:
    def __init__(self, type):
        self.type = type
        self.path = Path('data') / Path(session['username'])
        self.file = Path(self.type + '.csv')
    def __enter__(self):
        if path.exists(self.path / self.file):
            self.data = pd.read_csv(self.path / self.file, index_col=False)
        else:
            self.path.mkdir(parents=True, exist_ok=True)
            self.data = pd.DataFrame()
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.data.to_csv(self.path / self.file, index=False)
        del self

    def submit(self, row):
        self.data = pd.concat([pd.DataFrame(row, index=[0]), self.data], ignore_index=True)
    def remove(self, idx):
        self.data = self.data.drop(idx)

# ----------------------------------- Pages ---------------------------------- #
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with Users() as users:
            error = users.login(request.form['username'], request.form['password'])
            if not error:
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error=error)

    return render_template('login.html', error=None)

@app.route('/home')
def home():
    session['type'] = None

    return render_template('home.html')

@app.route('/settings')
def settings():
    pass

@app.route('/appts/<type>', methods=['GET', 'POST'])
def appts(type):
    session['type'] = type

    if request.method == 'POST':
        with Appts(session['type']) as appts:
            appts.submit(request.form)
        return redirect(url_for('appts', type=session['type']))
    
    return render_template(str(Path('appts') / Path(session['type'] + '.html')))

@app.route('/edit')
@app.route('/edit/<idx>')
def edit(idx=None):
    with Appts(session['type']) as appts:
        if idx:
            appts.remove(int(idx))
        return render_template('edit.html', headers=appts.data.columns, table=appts.data.values)

# ----------------------------------- Main ----------------------------------- #

if __name__ == '__main__':
    app.run()

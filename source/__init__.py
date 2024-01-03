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
        user = self.data.loc[self.data.username == username].to_dict('records')[0]
        if password == user['password']:
            session['username'] = user['username']
            session['admin'] = bool(user['admin'])
            error = None
        else:
            error = 'Invalid credentials'
        return error

class Appts:
    def __init__(self, username, type):
        self.username = username
        self.type = type
        self.path = Path('data') / Path(self.username)
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

@app.route('/home', methods=['GET', 'POST'])
def home():
    session['type'] = None
    return render_template('home.html')

@app.route('/masa_reg', methods=['GET', 'POST'])
def masa_reg():
    session['type'] = 'masa_reg'
    if request.method == 'POST':
        with Appts(session['username'], session['type']) as appts:
            row = {
                    'date' : request.form['date'],
                    'start time' : request.form['start_time'],
                    'end time' : request.form['end_time'],
                    'department' : request.form['department'],
                    'level' : request.form['level'],
                    'query 1' : request.form['query1'],
                    'query 2' : request.form['query2']
                }
            appts.submit(row)
        return redirect(url_for('masa_reg'))
    
    return render_template('masa_reg.html')

@app.route('/masa_emb', methods=['GET', 'POST'])
def masa_emb():
    session['type'] = 'masa_emb'
    if request.method == 'POST':
        with Appts(session['username'], session['type']) as appts:
            row = {
                    'date' : request.form['date'],
                    'start time' : request.form['start_time'],
                    'end time' : request.form['end_time'],
                    'department' : request.form['department'],
                    'level' : request.form['level'],
                    'query 1' : request.form['query1'],
                    'query 2' : request.form['query2']
                }
            appts.submit(row)
        return redirect(url_for('masa_emb'))
    
    return render_template('masa_emb.html')

@app.route('/asnd_reg', methods=['GET', 'POST'])
def asnd_reg():
    session['type'] = 'asnd_reg'
    if request.method == 'POST':
        with Appts(session['username'], session['type']) as appts:
            row = {
                    'date' : request.form['date'],
                    'start time' : request.form['start_time'],
                    'end time' : request.form['end_time'],
                    'department' : request.form['department'],
                    'level' : request.form['level'],
                    'query 1' : request.form['query1'],
                    'query 2' : request.form['query2']
                }
            appts.submit(row)
        return redirect(url_for('asnd_reg'))

    return render_template('asnd_reg.html')

@app.route('/asnd_emb', methods=['GET', 'POST'])
def asnd_emb():
    session['type'] = 'asnd_emb'
    if request.method == 'POST':
        with Appts(session['username'], session['type']) as appts:
            row = {
                    'date' : request.form['date'],
                    'start time' : request.form['start_time'],
                    'end time' : request.form['end_time'],
                    'department' : request.form['department'],
                    'level' : request.form['level'],
                    'query 1' : request.form['query1'],
                    'query 2' : request.form['query2']
                }
            appts.submit(row)
        return redirect(url_for('asnd_emb'))
    
    return render_template('asnd_emb.html')

@app.route('/<type>', methods=['GET', 'POST'])
def appts(type):
    session['type'] = type
    if request.method == 'POST':
        with Appts(session['username'], session['type']) as appts:
            row = {
                    'date' : request.form['date'],
                    'start time' : request.form['start_time'],
                    'end time' : request.form['end_time'],
                    'department' : request.form['department'],
                    'level' : request.form['level'],
                    'query 1' : request.form['query1'],
                    'query 2' : request.form['query2']
                }
            appts.submit(row)
        return redirect(url_for('appts', type=session['type']))
    
    return render_template(session['type'] + '.html')

@app.route('/edit')
@app.route('/edit/<idx>')
def edit(idx=None):
    with Appts(session['username'], session['type']) as appts:
        if idx:
            appts.remove(int(idx))
        return render_template('edit.html', headers=appts.data.columns, table=appts.data.values)

# ----------------------------------- Main ----------------------------------- #

if __name__ == '__main__':
    app.run()

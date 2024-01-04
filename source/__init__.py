from flask import Flask, render_template, request, redirect, url_for, session
from pathlib import Path
from pandas import DataFrame, read_csv, concat

import logging
logging.basicConfig(
    filename='app.log',
    encoding='utf-8',
    level=logging.DEBUG
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------------------------------- Classes --------------------------------- #

class Users:
    def __init__(self):
        self.path = Path('data') / Path('users.csv')
    def __enter__(self):
        self.data = read_csv(self.path, index_col=False)
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.data.to_csv(self.path, index=False)
        del self

    def login(self, form):
        # Check for user in database
        try:
            idx = self.data.index[self.data.username == form['username']][0]
        except IndexError:
            return 'User not found!'
        user = self.data.iloc[idx]
        
        # Check user password and login
        if form['password'] == user['password']:
            user.pop('password')
            session.update(user.to_dict())
        else:
            return 'Password invalid!'
    def password_change(self, form):
        # Check for user in database
        try:
            idx = self.data.index[self.data.username == session['username']][0]
        except IndexError:
            return 'User not found!'
        user = self.data.iloc[idx]

        # Check old password
        if form['password_old'] == user['password']:
            pass
        else:
            return 'Password invalid!'
        
        # Check passwords match and change
        if form['password_new'] == form['password_check']:
            self.data.at[idx, 'password'] = form['password_new']
        else:
            return 'Passwords do not match!'

class Appts:
    def __init__(self, type):
        self.type = type
        self.path = Path('data') / Path(session['username']) / Path(self.type + '.csv')
    def __enter__(self):
        if self.path.exists():
            self.data = read_csv(self.path, index_col=False)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.data = DataFrame()
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.data.to_csv(self.path, index=False)
        del self

    def submit(self, row):
        self.data = concat([DataFrame(row, index=[0]), self.data], ignore_index=True)
    def remove(self, idx):
        self.data = self.data.drop(idx)

# ----------------------------------- Pages ---------------------------------- #
        
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    
    if request.method == 'POST':
        with Users() as users:
            error = users.login(request.form)
            if not error:
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error=error)

    return render_template('login.html', error=None)

@app.route('/home')
def home():
    session['type'] = None

    return render_template('home.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    session['type'] = None

    if request.method == 'POST':
        with Users() as users:
            error = users.password_change(request.form)
            if not error:
                return redirect(url_for('home'))
            else:
                return render_template('settings.html', error=error)

    return render_template('settings.html', error=None)

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

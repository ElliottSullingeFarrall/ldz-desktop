from flask import Flask, Blueprint, current_app, flash, redirect, url_for, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from pandas import DataFrame, Series, read_sql, read_csv, concat, to_datetime
from pandas.errors import EmptyDataError

from datetime import datetime
from functools import wraps
from importlib import import_module
from pathlib import Path
from shutil import rmtree

import logging

db = SQLAlchemy()

# ---------------------------------------------------------------------------- #
#                                  Data Class                                  #
# ---------------------------------------------------------------------------- #

class Data:
    categories = [dir for dir in Path('source/templates/data').iterdir() if dir.is_dir()]
    options = {str(category.name) : [str(path.stem) for path in category.iterdir()] for category in categories}

    def __init__(self, category, type):
        self.category = category
        self.type = type
        self.path = Path('data') / Path(current_user.username) / Path(category) / Path(type).with_suffix('.csv')
    def __enter__(self):
        if self.path.exists():
            try:
                self.df = read_csv(self.path, index_col=False)
            except EmptyDataError:
                self.df = DataFrame()
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.df = DataFrame()
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.df.to_csv(self.path, index=False)
        del self

    def add(self, row):
        self.df = concat([DataFrame(row, index=[0]), self.df], ignore_index=True)
    def remove(self, idx):
        self.df = self.df.drop(idx)

    def summarise_month(self, month, col, n=5):
        dt = datetime.strptime(month, '%Y-%m')

        df = self.df.copy()
        df['Date'] = to_datetime(df['Date'])
        df = df.loc[(df['Date'].dt.month == dt.month) & (df['Date'].dt.year == dt.year)]
        
        top = df[col].value_counts().nlargest(n)
        bot = Series(df[col].value_counts().iloc[n:].sum(), index=['other'])
        data = concat([top, bot])

        return {key: value for key, value in data.items() if value != 0}

# ---------------------------------------------------------------------------- #
#                                  User Model                                  #
# ---------------------------------------------------------------------------- #

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def login(cls, form):
        user = cls.query.filter_by(username=form['username']).first()

        if user and check_password_hash(user.password, form['password']):
            login_user(user)
            return
        else:
            return 'Invalid login!'
        
    @classmethod
    def logout(cls):
        logout_user()
    
    @classmethod
    def change_password(cls, form):
        user = cls.query.filter_by(username=current_user.username).first()

        if form['password_new'] != form['password_check']:
            return 'Passwords do not match!'
        if not check_password_hash(user.password, form['password_old']):
            return 'Invalid password!'
        
        user.password = generate_password_hash(form['password_new'])
        db.session.commit()
        return
    
    @classmethod
    def get(cls, idx):
        table = read_sql(cls.query.statement, db.engine)
        user = cls.query.filter_by(username=table.at[idx, 'username']).first()
        return user
    
    @classmethod
    def view(cls):
        table = read_sql(cls.query.statement, db.engine)

        table.pop('id')
        table.pop('password')
        return table
    
    @classmethod
    def add(cls, form):
        user = cls.query.filter_by(username=form['username']).first()

        if not user:
            user = cls(username=form['username'], password=generate_password_hash(form['password']), admin=bool(form.get('admin')))
            db.session.add(user)
            db.session.commit()
            return
        else:
            return 'User already exists!'

    @classmethod
    def remove(cls, idx):
        table = read_sql(cls.query.statement, db.engine)
        user = cls.query.filter_by(username=table.at[idx, 'username']).first()

        db.session.delete(user)
        db.session.commit()

        rmtree(Path('data') / Path(user.username))

    @classmethod
    def reset_password(cls, idx, form):
        table = read_sql(User.query.statement, db.engine)
        user = cls.query.filter_by(username=table.at[idx, 'username']).first()

        if form['password_new'] == form['password_check']:
            user.password = generate_password_hash(form['password_new'])
            db.session.commit()
            return
        else:
            return 'Passwords do not match!'

# ---------------------------------------------------------------------------- #
#                                   Flask App                                  #
# ---------------------------------------------------------------------------- #

class App(Flask):
    styles = [str(file.name) for file in Path('source/static').iterdir()]

    def __init__(self):
        super().__init__(__name__)

        # ---------------------------------- Config ---------------------------------- #

        self.config['SECRET_KEY'] = 'secret-key-goes-here'
        self.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.root_path}/../data/users.sqlite'

        logging.getLogger().setLevel(logging.DEBUG)

        # --------------------------------- Database --------------------------------- #

        db.init_app(self)
        with self.app_context():
            db.create_all()
            # Create default user for empty db
            if not User.query.count():
                default = User(username='default', password=generate_password_hash('default'), admin=True)
                db.session.add(default)
                db.session.commit()

        # ----------------------------------- Login ---------------------------------- #

        login_manager = LoginManager()
        login_manager.login_view = 'auth.login'
        login_manager.init_app(self)
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # -------------------------------- Environment ------------------------------- #
    
        @self.context_processor
        def global_vars():
            return {'styles' : self.styles, 'options' : Data.options}

        # -------------------------------- Blueprints -------------------------------- #

        for filepath in (Path(__file__).parent / 'views').glob('[!_]*.py'):
            name = filepath.stem
            blueprint = import_module(f'source.views.{name}').__dict__[name]
            self.register_blueprint(blueprint, url_prefix=f'/{name}')

        # ---------------------------------- Routes ---------------------------------- #

        @self.route('/sw.js')
        def service_worker():
            return ('', 204)

        @self.route('/')
        @self.route('/index')
        def index():
            return redirect(url_for('home.index'))
        
    def run(self):
        super().run()

    @classmethod
    def blueprint(cls, __name__, __file__):
        return Blueprint(Path(__file__).stem, __name__, template_folder=f'../templates/{Path(__file__).stem}')

    @classmethod
    def login_required(cls, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login')) 
            return f(*args, **kwargs)
        return decorated_function

    @classmethod
    def admin_required(cls, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login')) 
            if not current_user.admin:
                return 
            return f(*args, **kwargs)
        return decorated_function

# ---------------------------------------------------------------------------- #
#                                    Factory                                   #
# ---------------------------------------------------------------------------- #

def create_app():
    app = App()
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()

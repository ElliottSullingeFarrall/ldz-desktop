from flask import Flask, Blueprint, current_app, flash, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
from pathlib import Path
from pandas import DataFrame, read_sql, read_csv, concat
from pandas.errors import EmptyDataError

db = SQLAlchemy()

# -------------------------------- Decorators -------------------------------- #

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            return 
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------- Classes --------------------------------- #

class Data:
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

# --------------------------------- Flask App -------------------------------- #

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.root_path}/../data/users.sqlite'

    @app.context_processor
    def global_vars():
        styles = [str(file.name) for file in Path('source/static').iterdir()]

        categories = [dir for dir in Path('source/templates/data').iterdir() if dir.is_dir()]
        options = {str(category.name) : [str(path.stem) for path in category.iterdir()] for category in categories}

        return {'styles' : styles, 'options' : options}

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        # Create default user
        if not User.query.count():
            default = User(username='default', password=generate_password_hash('default'), admin=True)
            db.session.add(default)
            db.session.commit()

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    return app

# ---------------------------------- Script ---------------------------------- #

if __name__ == '__main__':
    app = create_app()
    app.run()

from imports import *

db = SQLAlchemy()

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
    def list(cls):
        users = [user.username for user in cls.query.all()]
        return users

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
    def import_csv(cls, files):
        file = files['users']

        if file.filename == '':
            return 'No selected file!'
        if not file.filename.endswith('.csv'):
            return 'Invalid file type!'
        
        with NamedTemporaryFile(suffix='.csv') as temp:
            file.save(temp.name)
            df = read_csv(temp.name)
        
        for _, row in df.iterrows():
            user = cls.query.filter_by(username=row['username']).first()
            if not user:
                user = cls(username=row['username'], password=generate_password_hash(row['username']), admin=bool(row.get('admin')))
                db.session.add(user)
            else:
                return 'User already exists!'
        db.session.commit()

    @classmethod
    def remove(cls, idx):
        table = read_sql(cls.query.statement, db.engine)
        user = cls.query.filter_by(username=table.at[idx, 'username']).first()

        db.session.delete(user)
        db.session.commit()

        if (Path('data') / Path(user.username)).exists():
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
    
from imports import *

from db import *

# ---------------------------------------------------------------------------- #
#                                  Data Class                                  #
# ---------------------------------------------------------------------------- #

class Data:
    categories = [dir for dir in Path('src/templates/data').iterdir() if dir.is_dir()]
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

    @classmethod
    def pull(cls, form):
        dt = datetime.strptime(form.get('month'), '%Y-%m')
        category, type = form.get('category:type').split(':')
        users = form.getlist('users')

        df_list = []
        for user in users:
            path = Path('data') / Path(user) / Path(category) / Path(type).with_suffix('.csv')
            if path.exists():
                try:
                    df = read_csv(path, index_col=False)
                except EmptyDataError:
                    continue
            else:
                continue

            df['Date'] = to_datetime(df['Date'])
            df = df.loc[(df['Date'].dt.month == dt.month) & (df['Date'].dt.year == dt.year)]

            df_list.append(df)

        if df_list:
            return concat(df_list)
        else:
            return DataFrame()

    def summarise(self, year):
        if not self.df.empty:
            df = self.df.copy()
            df['Date'] = to_datetime(df['Date'])
            df = df[df['Date'].dt.year == int(year)]
            
            data = df['Date'].dt.month.value_counts().sort_index().to_dict()

            return data
        else:
            return {}

# ---------------------------------------------------------------------------- #
#                                   Flask App                                  #
# ---------------------------------------------------------------------------- #

class App(Flask):
    styles = [str(file.name) for file in Path('src/static').iterdir()]

    def __init__(self):
        super().__init__(__name__)

        # ---------------------------------- Config ---------------------------------- #

        self.config.from_pyfile(f'{Path(self.root_path).parent}/config.py')
        self.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{Path(self.root_path).parent}/data/users.sqlite'

        Path(f'{Path(self.root_path).parent}/data').mkdir(exist_ok=True)

        # logging.getLogger().setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG, filename='flask.log')

        # --------------------------------- Database --------------------------------- #

        db.init_app(self)
        with self.app_context():
            db.create_all()
            # Create default user for empty db
            if not User.query.count():
                default = User(username='default', password=generate_password_hash(self.config['SECRET_KEY']), admin=True)
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
            return {'styles' : self.styles, 'options' : Data.options, 'current_year' : datetime.now().year}

        # -------------------------------- Blueprints -------------------------------- #

        for filepath in (Path(__file__).parent / 'views').glob('[!_]*.py'):
            name = filepath.stem
            blueprint = import_module(f'src.views.{name}').__dict__[name]
            self.register_blueprint(blueprint, url_prefix=f'/{name}')

        # ---------------------------------- Routes ---------------------------------- #

        @self.route('/sw.js')
        def service_worker():
            return ('', 204)

        @self.route('/')
        @self.route('/index')
        def index():
            return redirect(url_for('home.index'))

        @self.route('/pull', methods=['POST'])
        def pull():
            secret_token = self.config['SECRET_KEY']
            request_token = request.headers.get('X-Secret-Token')

            if not secret_token or not request_token or secret_token != request_token:
                abort(403)

            if request.method == 'POST':
                git.Repo('.').remotes.origin.pull()
                with open('VERSION', 'w') as version_file:
                    version_file.write(git.Repo('.').head.object.hexsha)
                Path('/var/www/elliottsf_eu_pythonanywhere_com_wsgi.py').touch()
                return '', 200
            else:
                return '', 400
            
        @self.route('/version')
        def version():
            if Path('VERSION').exists():
                with open('VERSION', 'r') as version_file:
                    return version_file.read()
            else:
                abort(404)

    def run(self):
        super().run()

    @classmethod
    def blueprint(cls, name, file):
        return Blueprint(Path(file).stem, name, template_folder=f'../templates/{Path(file).stem}')

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
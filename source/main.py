from . import *

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        error = User.change_password(request.form)
        if not error:
            return redirect(url_for('main.home'))
    else:
        error = None

    return render_template('settings.html', error=error)

@main.route('/data/<type>', methods=['GET', 'POST'])
@login_required
def data(type):
    type = eval(type)

    if request.method == 'POST':
        with Data(type) as data:
            data.add(request.form)
        return redirect(url_for('main.data', type=type))
    
    return render_template(str(Path('data') / Path(*type).with_suffix('.html')))

@main.route('/edit/<type>')
@main.route('/edit/<type>/<idx>')
@login_required
def edit(type, idx=None):
    type = eval(type)

    with Data(type) as data:
        if idx:
            data.remove(int(idx))
        return render_template('data/edit.html', headers=data.df.columns, table=data.df.values)
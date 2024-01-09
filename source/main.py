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
            flash(error)

    return render_template('settings.html')

@main.route('/data/<category>/<type>', methods=['GET', 'POST'])
@login_required
def data(category, type):
    if request.method == 'POST':
        with Data(category, type) as data:
            data.add(request.form)
        return redirect(url_for('main.data', category=category, type=type))
    
    return render_template(f'data/{category}/{type}.html', category=category, type=type)

@main.route('/edit/<category>/<type>')
@main.route('/edit/<category>/<type>/<idx>')
@login_required
def edit(category, type, idx=None):
    with Data(category, type) as data:
        if idx:
            data.remove(int(idx))
        return render_template('data/edit.html', category=category, type=type, headers=data.df.columns, table=data.df.values)
from .. import *

data = App.blueprint(__name__, __file__)

@data.route('/view/<category>/<type>', methods=['GET', 'POST'])
@App.login_required
def view(category, type):
    if request.method == 'POST':
        with Data(category, type) as data:
            data.add(request.form)
        return redirect(url_for('.view', category=category, type=type))
    
    return render_template(f'{category}/{type}.html', category=category, type=type)

@data.route('/edit/<category>/<type>')
@data.route('/edit/<category>/<type>/<idx>')
@App.login_required
def edit(category, type, idx=None):
    with Data(category, type) as data:
        if idx:
            data.remove(int(idx))
        return render_template('edit.html', category=category, type=type, headers=data.df.columns, table=data.df.values)
from .. import *

data = App.blueprint(__name__, __file__)

@data.route('/<category>/<type>', methods=['GET', 'POST'])
@App.login_required
def add(category, type):
    if request.method == 'POST':
        with Data(category, type) as data:
            data.add(request.form)
        return redirect(url_for('.add', category=category, type=type))
    
    return render_template(f'{category}/{type}.html', category=category, type=type)

@data.route('/<category>/<type>/view')
@App.login_required
def edit(category, type):
    with Data(category, type) as data:
        return render_template('edit.html', category=category, type=type, headers=data.df.columns, table=data.df.values)

@data.route('/<category>/<type>/remove')    
@data.route('/<category>/<type>/remove/<idx>', methods=['GET', 'POST'])
@App.login_required
@App.confirm_required
def remove(category, type, idx=None):
    with Data(category, type) as data:
        data.remove(int(idx))
        return redirect(url_for('.edit', category=category, type=type))
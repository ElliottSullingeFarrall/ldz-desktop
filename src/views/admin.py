from .. import *

admin = App.blueprint(__name__, __file__)

# ----------------------------------- User ----------------------------------- #

@admin.route('/user')
@App.admin_required
def user_view():
    table = User.view()
    return render_template('user/view.html', headers=table.columns, table=table.values)
    
@admin.route('/user/add', methods=['GET', 'POST'])
@App.admin_required
def user_add():
    if request.method == 'POST':
        error = User.add(request.form)
        if not error:
            return redirect(url_for('.user_view'))
        else:
            flash(error)

    return render_template('admin/user/add.html')

@admin.route('/user/import', methods=['GET', 'POST'])
@App.admin_required
def user_import():
    if request.method == 'POST':
        error = User.import_csv(request.files)
        if not error:
            return redirect(url_for('.user_view'))
        else:
            flash(error)
    return render_template('user/import.html')

@admin.route('/user/edit/<idx>', methods=['GET', 'POST'])
@App.admin_required
def user_edit(idx):
    if request.method == 'POST':
        error = User.reset_password(int(idx), request.form)
        if not error:
            return redirect(url_for('.user_view'))
        else:
            flash(error)

    user = User.get(int(idx))
    if user.username == current_user.username:
        return redirect(url_for('.user_view'))
            
    return render_template('user/edit.html', idx=idx)

@admin.route('/user/remove/<idx>')
@App.admin_required
def user_remove(idx=None):
    User.remove(int(idx))
    return redirect(url_for('.user_view'))

# ----------------------------------- Data ----------------------------------- #

@admin.route('/data', methods=['GET', 'POST'])
@App.admin_required
def data():
    if request.method == 'POST':
        df = Data.pull(request.form)
        return Response(df.to_csv(index=False), mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=data.csv'})

    return render_template('data.html', users=User.list())
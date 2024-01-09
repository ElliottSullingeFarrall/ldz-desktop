from . import *

user = Blueprint('user', __name__)

@user.route('/user')
@login_required
@admin_required
def view():
    table = User.view()
    return render_template('user/view.html', headers=table.columns, table=table.values)
    
@user.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        error = User.add(request.form)
        if not error:
            return redirect(url_for('user.view'))
    else:
        error = None

    return render_template('user/add.html', error=error)

@user.route('/user/edit/<idx>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(idx):
    if request.method == 'POST':
        error = User.reset_password(int(idx), request.form)
        if not error:
            return redirect(url_for('user.view'))
    else:
        error = None

    user = User.get(int(idx))
    if user.username == current_user.username:
        return redirect(url_for('user.view'))
            
    return render_template('user/edit.html', idx=idx, error=error)

@user.route('/user/remove/<idx>')
@login_required
@admin_required
def remove(idx=None):
    User.remove(int(idx))
    return redirect(url_for('user.view'))
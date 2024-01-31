from . import *

admin = Blueprint('admin', __name__)

@admin.route('/admin/user')
@login_required
@admin_required
def user_view():
    table = User.view()
    return render_template('admin/user/view.html', headers=table.columns, table=table.values)
    
@admin.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    if request.method == 'POST':
        error = User.add(request.form)
        if not error:
            return redirect(url_for('admin.user_view'))
        else:
            flash(error)

    return render_template('admin/user/add.html')

@admin.route('/admin/user/edit/<idx>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(idx):
    if request.method == 'POST':
        error = User.reset_password(int(idx), request.form)
        if not error:
            return redirect(url_for('admin.user_view'))
        else:
            flash(error)

    user = User.get(int(idx))
    if user.username == current_user.username:
        return redirect(url_for('admin.user_view'))
            
    return render_template('admin/user/edit.html', idx=idx)

@admin.route('/admin/user/remove/<idx>')
@login_required
@admin_required
def user_remove(idx=None):
    User.remove(int(idx))
    return redirect(url_for('admin.user_view'))
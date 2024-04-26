from .. import *

user = App.blueprint(__name__, __file__)

@user.route('/settings', methods=['GET', 'POST'])
@App.login_required
def settings():
    if request.method == 'POST':
        error = User.change_password(request.form)
        if not error:
            return redirect(url_for('main.home'))
        else:
            flash(error)

    return render_template('settings.html')
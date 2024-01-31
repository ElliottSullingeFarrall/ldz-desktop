from .. import *

user = Blueprint('user', __name__)

@user.route('/user/settings', methods=['GET', 'POST'])
@App.login_required
def settings():
    if request.method == 'POST':
        error = User.change_password(request.form)
        if not error:
            return redirect(url_for('main.home'))
        else:
            flash(error)

    return render_template('user/settings.html')
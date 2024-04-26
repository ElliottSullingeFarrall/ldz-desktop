from .. import *

auth = App.blueprint(__name__, __file__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user:
        User.logout()
     
    if request.method == 'POST':
        error = User.login(request.form)
        if not error:
            return redirect(url_for('home.index'))
        else:
            flash(error)

    return render_template('login.html')

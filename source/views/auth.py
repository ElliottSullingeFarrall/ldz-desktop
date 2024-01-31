from .. import *

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    logging.debug(current_user)
    if current_user:
        User.logout()
     
    if request.method == 'POST':
        error = User.login(request.form)
        if not error:
            return redirect(url_for('main.home'))
        else:
            flash(error)
    
    return render_template('auth/login.html')

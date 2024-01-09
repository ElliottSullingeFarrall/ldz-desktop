from . import *

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        error = User.login(request.form)
        if not error:
            return redirect(url_for('main.home'))
    else:
        error = None
    
    return render_template('login.html', error=error)

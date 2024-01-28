from . import *

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/get_charts', methods=['GET'])                       
@main.route('/get_charts/<year>/<month>', methods=['GET'])
@login_required
def get_charts(year=None, month=None):
    charts = {}
    for category in Data.options:
        for type in Data.options[category]:
            with Data(category, type) as data:
                chart_data = data.summarise_month(year, month, 'Query 1')

            trace = {
                'values': list(chart_data.values()),
                'labels': [label[:30] for label in chart_data.keys()],
                'type': 'pie',
                'hoverinfo': 'label'
            }
            layout = {
                'title': f'{category.capitalize()} {type.upper()}',
                'paper_bgcolor': 'transparent',
                'height': 300,
                'width': 300,
                'showlegend': False,
                'margin': {'l': 10, 'r': 10, 't': 30, 'b': 10}
            }

            charts[f'{category}:{type}'] = {'data': [trace], 'layout': layout}
    return jsonify(charts)

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        error = User.change_password(request.form)
        if not error:
            return redirect(url_for('main.home'))
        else:
            flash(error)

    return render_template('settings.html')

@main.route('/data/<category>/<type>', methods=['GET', 'POST'])
@login_required
def data(category, type):
    if request.method == 'POST':
        with Data(category, type) as data:
            data.add(request.form)
        return redirect(url_for('main.data', category=category, type=type))
    
    return render_template(f'data/{category}/{type}.html', category=category, type=type)

@main.route('/edit/<category>/<type>')
@main.route('/edit/<category>/<type>/<idx>')
@login_required
def edit(category, type, idx=None):
    with Data(category, type) as data:
        if idx:
            data.remove(int(idx))
        return render_template('data/edit.html', category=category, type=type, headers=data.df.columns, table=data.df.values)
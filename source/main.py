from . import *

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@main.route('/home')
@login_required
def home():
    return render_template('home.html')
                           
@main.route('/getChartData/<month>', methods=['GET'])
@login_required
def get_chart_data(month):
    # TODO: Obtain options from global_vars
    categories = [dir for dir in Path('source/templates/data').iterdir() if dir.is_dir()]
    options = {str(category.name) : [str(path.stem) for path in category.iterdir()] for category in categories}
    
    charts = {}
    for category in options:
        for type in options[category]:
            with Data(category, type) as data:
                df = data.df
                df['Date'] = to_datetime(data.df['Date'])
                df = df[df['Date'].dt.month_name() == month]
            # Process the data to get the top 5 entries and group the rest into 'other'
            top5 = df['Query 1'].value_counts().nlargest(5)
            other = Series(df['Query 1'].value_counts().iloc[5:].sum(), index=['other'])
            chart = concat([top5, other])

            # Filter out the values that are 0
            chart_dict = {key: value for key, value in chart.items() if value != 0}

            # Create a trace object for the pie chart
            trace = {
                'values': list(chart_dict.values()),
                'labels': [label[:30] for label in chart_dict.keys()],
                'type': 'pie',
                'hoverinfo': 'label'
            }
            # Create a layout object for the pie chart
            layout = {
                'title': f'{category.capitalize()} {type.upper()}',
                'paper_bgcolor': 'transparent',
                'height': 300,
                'width': 300,
                'showlegend': False,
                'margin': {'l': 10, 'r': 10, 't': 30, 'b': 10}
            }

            charts[f'{category}-{type}'] = {'data': [trace], 'layout': layout}
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
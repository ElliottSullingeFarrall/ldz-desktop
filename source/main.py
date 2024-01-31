from . import *

main = Blueprint('main', __name__)

@main.route('/sw.js')
def service_worker():
    return ('', 204)

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


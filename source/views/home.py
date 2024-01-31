from .. import *

home = App.blueprint(__name__, __file__)

@home.route('/')
@App.login_required
def index():
    return render_template('index.html')

@home.route('/chart', methods=['GET'])                       
@home.route('/chart/<category>/<type>/<month>', methods=['GET'])
@App.login_required
def chart(category=None, type=None, month=None):
    with Data(category, type) as data:
        chart_data = data.summarise_month(month, 'Query 1')

    trace = {
        'values': list(chart_data.values()),
        'labels': [label[:30] for label in chart_data.keys()],
        'type': 'pie',
        'hoverinfo': 'label'
    }
    layout = {
        'title': f'{category.capitalize()} {type.upper()}',
        'paper_bgcolor': 'transparent',
        'height': 500,
        'width': 500,
        'showlegend': False,
        'margin': {'l': 10, 'r': 10, 't': 30, 'b': 10}
    }

    chart = {'data': [trace], 'layout': layout}
    return jsonify(chart)


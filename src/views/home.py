from .. import *

home = App.blueprint(__name__, __file__)

@home.route('/')
@App.login_required
def index():
    return render_template('index.html')

@home.route('/charts', methods=['GET'])                       
@home.route('/charts/<category>/<type>/<year>', methods=['GET'])
@App.login_required
def charts(category=None, type=None, year=None):
    with Data(category, type) as data:
        chart_data = data.summarise(year)

    trace = {
        'x': [datetime(2000, i, 1).strftime('%b') for i in range(1, 13)],
        'y': [chart_data.get(month, 0) for month in range(1, 13)],
        'type': 'scatter',
        'mode': 'lines+markers',
    }
    layout = {
        'paper_bgcolor': 'transparent',
        'plot_bgcolor': 'transparent',
        'showlegend': False,
        'autosize': True,
        'margin': {'l': 10, 'r': 10, 't': 40, 'b': 40},
        'title': f'{category.capitalize()} - {type.upper()}',
        'xaxis': {
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
        },
        'yaxis': {
            'title': '# Students',
            'range': [0, 'auto'],
            'rangemode': 'tozero',
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
        },
    }

    return jsonify({'data': [trace], 'layout': layout})

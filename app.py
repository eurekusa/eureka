from dash import Dash, dcc, html
from pages import Facade, index
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
global facade
facade = Facade()


if __name__ == '__main__':
    app.run_server(debug=True)

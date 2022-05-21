from dash import Dash, dcc, html
from pages import Facade, index
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.2/font/bootstrap-icons.css"])
server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='url2', refresh=True),
    html.Div(id='page-content'),
    dcc.Store(id='load_upload_data_interface', storage_type='memory',data=None),
])
global facade
facade = Facade()

if __name__ == '__main__':
    app.run_server(debug=True)

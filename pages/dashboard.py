import ast

import dash
from dash import dcc, html, Input, State, Output, callback, ALL, MATCH, no_update
from app import facade, app
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

ERIKUSA_LOGO = app.get_asset_url('Erikusa_BBG.png')

navbar = dbc.Navbar(
    dbc.Container(
        [

            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=ERIKUSA_LOGO, height="30px")),
                ],
                align="center",
                className="g-0",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Link(dbc.Button([html.I(className="bi bi-columns-gap"),"  Change template"], outline=True, color="light",style={'white-space': 'nowrap'}),
                                     href='/'), className="mr-auto"),
                    dbc.Col(dcc.Link(dbc.Button([html.I(className="bi bi-file-earmark-arrow-down"),"  Import new data"], outline=True, color="light"),
                                     href='/upload'), className="mr-auto")
                ],
                align="center")
        ],
        fluid=True),
    className='shadow',
    color='#2c2b30',
    sticky="top",
)


def render_template(dashboard):
    layout = html.Div([
        navbar,
        dashboard
    ])
    return layout




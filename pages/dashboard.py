import ast

import dash
from dash import dcc, html, Input, State, Output, callback, ALL, MATCH, no_update
from app import facade, app
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

ERIKUSA_LOGO = app.get_asset_url('Ericon-WBK.png')

navbar = dbc.Navbar(
    dbc.Container(
        [

            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=ERIKUSA_LOGO, height="40em")),
                ],
                align="center",
                className="g-0",
            ),
            dbc.Row(
                [

                dbc.Col(
                        dbc.Button([html.I(className="bi bi-columns-gap"), "  Change template"], outline=True, href='/',className='outlined',style={'white-space': 'nowrap'}), className="mr-auto"),
                 dbc.Col(
                     dcc.Link(dbc.Button([html.I(className="bi bi-file-earmark-arrow-down"),"  Import new data"],class_name='outlined'),
                                     href='/upload'), className="mr-auto")
                ],
                align="center")
        ],
        fluid=True),
    className='shadow import_nav',
    sticky="top",
)



def render_template(dashboard):
    layout = dbc.Container([
        dbc.Row(navbar,className='p-0 m-0'),
        dbc.Row(dbc.Col(dashboard,className='p-0 m-0'),className='p-0 m-0',style={'background-color': '#fff'})
    ],fluid=True, style={'background-color': 'rgb(234,236,242)', }, className='p-0')
    return layout




import base64
import io

import pandas as pd
from dash import dcc, html, Input, State, Output, callback, ALL, MATCH, no_update
import ast

import dash
from dash import dcc, html, Input, State, Output, callback, ALL, MATCH, no_update
from app import facade, app
import dash_bootstrap_components as dbc

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
                    dbc.Col(dcc.Link(
                        dbc.Button([html.I(className="bi bi-columns-gap"), "  Change template"], outline=True,
                                   color="light"),
                        href='/'), className="mr-auto"),
                ],
                align="center")
        ],
        fluid=True),
    className='shadow',
    color='#2c2b30',
    sticky="top",
)
upload = dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select data file', style={'font-weight': 'bold', })
    ]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    },
    # Allow multiple files to be uploaded
    multiple=False
)

upload_file_card = [
    dbc.CardHeader(html.H5("Upload document")),
    dbc.CardBody(
        [
            dcc.Loading(upload,
                        type="default",
                        )
        ],
        style={"marginTop": 0, "marginBottom": 0},
    ),
]

error_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Something wrong happened !"), close_button=True),
        dbc.ModalBody("Please check your file type (excel, csv) and format."),
    ],
    id="error-centered",
    backdrop="static",
    centered=True,
    is_open=False,
)
data_validity_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Data validation"), close_button=True),
        dcc.Loading(dbc.ModalBody(id="data_validity_Body", children=["Please check data validity"])),
    ],
    id="data_validity",
    backdrop="static",
    centered=True,
    is_open=False,
    size="lg"
)
layout = html.Div([
    navbar,
    error_modal,
    data_validity_modal,
    dbc.Container(
        [
            dbc.Row([dbc.Col(dbc.Card(children=upload_file_card)), ], style={"marginTop": 30}),
        ],
        className="mt-12",
    ),
])


@callback(
    Output("data_validity", "is_open"),
    Output("error-centered", "is_open"),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State("data_validity", "is_open"),
    State("error-centered", "is_open"))
def update_document(content, filename, is_open, e_is_open):
    """
    reads the uploaded data file and updates facade raw_data attribute
    """
    if content is None:
        return dash.no_update, dash.no_update
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            facade.load_data(df)
            return not is_open, dash.no_update
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            facade.load_data(df)
            return not is_open, dash.no_update
        return dash.no_update, not e_is_open

    except Exception as e:
        print(e)
        return dash.no_update, not e_is_open


@callback(
    Output("data_validity_Body", "children"),
    Input("data_validity", "is_open"), prevent_initial_call=True)
def check_data(is_open):
    if is_open:
        answer = facade.check_data_validity(values=False)
        if answer[0] == 'ask_user':
            return answer[1]
    return dash.no_update


@callback(
    Output("data_form", "children"),
    Input("next_step", "n_clicks"),
    State({'type': 'column_match', 'value': ALL}, 'value')
    ,prevent_initial_call=True)
def checks_data(n_clicks, values):
    if any([value is None for value in values]):
        return dash.no_update
    else:

        answer = facade.check_data_validity(values=dash.callback_context.states_list[0])
        if answer[0] == 'ask_user':
            return answer[1]
        return dash.no_update


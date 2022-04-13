from dash import dcc, html, Input,State, Output, callback
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
            )],
        fluid=True),
    className='shadow',
    color='#2c2b30',
    sticky="top",
)

card = dbc.Card(
    [
        dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
        dbc.CardBody(
            [
                html.H4("Card title", className="card-title"),
                html.P(
                    "Some quick example text to build on the card title and "
                    "make up the bulk of the card's content.",
                    className="card-text",
                ),
                dbc.Button(html.I(className="bi bi-eye"), id="open-centered", className='outlined'),
            ]
        ),
    ],
    style={"width": "18rem"},
)
modal = html.Div(
    [dbc.Container(dbc.Row([card,
card,
card,
card,]),className="mt-12"),



        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Header"), close_button=True),
                dbc.ModalBody("This modal is vertically centered"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-centered",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False,
        ),
    ]
)



layout = html.Div([
    navbar,
    html.H3("Dashboard Templates Gallery"),
    modal
])

@callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
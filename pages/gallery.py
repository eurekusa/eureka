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
            )],
        fluid=True),
    className='shadow',
    color='#2c2b30',
    sticky="top",
)


def render_tags(template):
    tags = []
    for tag in template.tags:
        tags.append(dbc.Badge(
            tag,
            color="white",
            text_color="muted",
            className="border me-1",
        ))
    return tags


gallery_content = []
for template in facade.templates_list:
    card = dbc.Card([
        dbc.CardImg(src=app.get_asset_url(template.imgPreview), top=True),
        dbc.CardBody(
            [html.H5(template.name, className="card-title"),
             html.Div(render_tags(template), className="card-text"),
             dbc.Button(html.I(className="bi bi-eye"),
                        id={'type': 'template_card_button', 'name': template.name},
                        className='mt-2 outlined'),
             ],
            className='m-1 p-1'),
    ],
        style={"width": "18rem"},
        className="m-2 p-2 template_card"
    )
    modal = dbc.Modal(
        [dbc.ModalBody([
            dbc.Container(
                [
                    dbc.Row(

                        html.Img(id='preview_modal_img',
                                 src=app.get_asset_url(template.imgPreview),
                                 className="img-fluid rounded-start",
                                 ),
                    ),
                    dbc.Row(
                        [
                            html.H4(template.name, id='preview_modal_name', className="card-title"),
                            html.Div(render_tags(template), id='preview_modal_tags', className="card-text"),
                            html.Div(
                                template.description,
                                id='preview_modal_description',
                                className="card-text",
                            ),

                        ], className='m-2'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.A(children=dbc.Button(
                                "Load this template",
                                className="outlined",
                                n_clicks=0,
                            ), id={"type": "load_model_button", "name": template.name},href='/upload'), className='ml-auto')], className='m-2')
                ],
                className="g-0",
            )
        ], className='p-1'),
        ],
        id={'type': 'preview_modal', 'name': template.name},
        centered=True,
        is_open=False,
    )
    gallery_content.append(card)
    gallery_content.append(modal)

gallery = html.Div(
    [dbc.Container(dbc.Row(gallery_content, justify="center"), className="mt-12"),
     ]
)

layout = html.Div([
    navbar,
    html.H3("Dashboard Templates Gallery", className='main_header'),
    gallery
])


@callback(
    Output({"type": "preview_modal", "name": MATCH}, "is_open"),
    Input({"type": "template_card_button", "name": MATCH}, "n_clicks"),
    State({"type": "preview_modal", "name": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


@callback(
    Output("load_upload_data_interface", "data"),
    Input({'type': 'load_model_button', 'name': ALL}, "n_clicks"),
    prevent_initial_call=True)
def load_template(n1):
    if n1 in [[0, 0], [None, None]]:
        return no_update
    button_id = ast.literal_eval(dash.callback_context.triggered[0]['prop_id'].split('.')[0])
    facade.set_template(button_id['name'])
    return True

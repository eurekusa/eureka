from dash import Input, Output, callback
from pages import page1, page2, galery


@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page1':
        return galery.layout
    elif pathname == '/page2':
        return page2.layout
    else:
        return page1.layout
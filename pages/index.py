from dash import Input, Output, callback, no_update
from app import facade
from pages import import_data, gallery, dashboard


@callback(Output('page-content', 'children'),
          Output('url', 'pathname'),
          Input('url', 'pathname'),
          prevent_initial_call=True)
def display_page(pathname):
    if pathname == '/':
        return gallery.layout, no_update
    elif pathname == '/upload':
        if facade.current_template is None:
            return gallery.layout, '/'
        else:
            return import_data.layout, no_update
    elif pathname == '/dashboard':
        if facade.current_template is None:
            return gallery.layout, '/'
        else:
            if facade.raw_data is None:
                return import_data.layout, '/upload'
            else:
                return dashboard.render_template(facade.render_layout()),no_update
    else:
        return '404', no_update

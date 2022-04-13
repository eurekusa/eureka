from dash import dcc, html, Input, Output, callback

layout = html.Div([
    html.H3('Page 2'),
    dcc.Dropdown(
        {f'Page 2 - {i}': f'{i}' for i in ['London', 'Berlin', 'Paris']},
        id='page-2-dropdown'
    ),
    html.Div(id='page-2-display-value'),
    dcc.Link('Go to Page 1', href='/page2')
])

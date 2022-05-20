from app import app, facade
from dash import Input, Output, callback, no_update
from erikusa.metrics import cagr, growth
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from dash import dcc, html, Input, State, Output, callback, ALL
import dash
import plotly.express as px
from dash import no_update
from dash.exceptions import PreventUpdate


@callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")]
)
def tab_content(active_tab):
    return facade.current_template.tabs_dict[active_tab]


@callback(
    Output({'index': 'top', 'level': 'country'}, "max"),
    Output('range_checklist', 'options'),
    Output('range_checklist', 'value'),
    Input("country_checklist", 'value'),
    Input('per', 'value'),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'), )
def update_filters(countries, per, value):
    value = 'Sales volume' if value else 'Sales value'
    T_column = facade.current_template.clean_data.attrs['columns_dict'][per]
    C_column = facade.current_template.clean_data.attrs['columns_dict']['Country level']

    df = facade.current_template.clean_data
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == '{"index":"sales_toggle","type":"Country level"}':
        S_columns = facade.current_template.clean_data.attrs['columns_dict'][value]
        options = [{"label": column, "value": index} for index, column in enumerate(S_columns)]
        return df[df[C_column].isin(countries)][T_column].unique().shape[0], options, list(range(len(S_columns)))
    return df[df[C_column].isin(countries)][T_column].unique().shape[0], no_update, no_update


@callback(
    Output("country_checklist", 'value'),
    Input('select_all_country', 'n_clicks'),
    Input('clear_all_country', 'n_clicks'),
    State("country_checklist", 'options'), )
def update_country_filter(select, clear, options):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == 'select_all_country':
        return [option['value'] for option in options]
    if triggered_id == 'clear_all_country':
        return []
    return no_update


@callback(
    Output('MS_country_header', "children"),
    Output('MS_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input("country_checklist", 'value'),
    Input('range_checklist', 'value'),
)
def market_size(value, countries, range):
    range.sort()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    value, msg = ('Sales volume', 'volume') if value else ('Sales value', 'value')
    S_column = df.attrs['columns_dict'][value]
    S_column = [S_column[i] for i in range]
    ms = df[S_column].sum(axis=1).sum()
    return f"Market size in {msg}", str(ms)


@callback(
    Output('cagr_country_header', "children"),
    Output('cagr_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input("country_checklist", 'value'),
    Input('range_checklist', 'value'))
def cagr_card(value, countries, range):
    range.sort()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    value = 'Sales volume' if value else 'Sales value'
    S_columns = df.attrs['columns_dict'][value]
    if len(range) and len(countries):
        begin = S_columns[range[0]]
        final = S_columns[range[-1]]
        sales = df[[begin, final]].sum()
        t = range[-1] - range[0]
        cagr_v = 0 if t == 0 else cagr(begin=[sales[begin]], final=[sales[final]], t=t)[0] * 100
        return f"CAGR in {value.split()[1]}", "{:.2f}%".format(cagr_v)
    return f"CAGR in {value.split()[1]}", "{:.2f}%".format(0)



@callback(
    Output('RS_country_header', "children"),
    Output('RS_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input('range_checklist', 'value'),
    Input('per', 'value'),
)
def RS_card(value, top, countries, range, per):
    country_sales = None
    range.sort()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per]
    value = 'Sales volume' if value else 'Sales value'

    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    volume = df[[C_column] + S_columns]
    volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
    volume['Sales'] = volume[S_columns].sum(1)
    country_sales = volume.sort_values('Sales', ascending=False)[
                            [df.attrs['columns_dict'][per], 'Sales']][:top].values
    msg = f"Ranking {per.split()[0]} by sales in {value.split()[1]}"
    body = []
    if len(range):
        body = [html.Tbody([html.Tr([html.Td(country[0]), html.Td(country[1])]) for country in country_sales])]
    headers = [html.Thead(html.Tr([html.Th(per.split()[0]), html.Th("Sales")]))]

    table = dbc.Table(headers + body)

    return msg, table


@callback(
    Output('RG_country_header', "children"),
    Output('RG_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input('range_checklist', 'value'),
    Input('per', 'value'),)
def RG_card(value, top, countries, range, per):

    country_growth = None
    range.sort()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per]
    value = 'Sales volume' if value else 'Sales value'

    body = []
    msg = f"Ranking {per.split()[0]} by Growth in {value.split()[1]}"
    if len(range)>1 and len(countries):
        S_columns = df.attrs['columns_dict'][value]
        S_columns = [S_columns[i] for i in range]
        volume = df[[C_column] + S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['Growth'] = growth(data=volume, begin=S_columns[0], final=S_columns[-1]).values
        country_growth = volume.sort_values('Growth', ascending=False)[[
            df.attrs['columns_dict'][per], 'Growth']][:top].values
        body = [html.Tbody([html.Tr([html.Td(country[0]), html.Td("{:.2f}%".format(country[1] * 100))]) for country in country_growth])]
    headers = [html.Thead(html.Tr([html.Th(per.split()[0]), html.Th("Growth")]))]
    table = dbc.Table(headers + body)
    return msg, table


@callback(
    Output('pie_country_header', "children"),
    Output('pie_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('per', 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input('range_checklist', "value"), )
def MS_country_pie_card(value, per_filter, top, countries, range):
    market_share = None

    range.sort()
    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(countries):
        return f"Market share per {per_filter} in {value.split()[1]}", go.Figure()

    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per_filter]
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    ms = df[[C_column] + S_columns]
    ms = ms.groupby(by=C_column).sum().reset_index(level=[C_column])
    ms['MS'] = ms[S_columns].sum(axis=1)
    ms['MS'] = ms['MS'] / ms['MS'].sum()
    market_share = ms.sort_values('MS', ascending=False)[[C_column, 'MS']][:top]
    msg = f"Market share per {per_filter} in {value.split()[1]}"

    fig = go.Figure(data=[go.Pie(labels=market_share[C_column], values=market_share['MS'], textinfo='label+percent',
                                 insidetextorientation='radial')])

    return msg, fig


@callback(
    Output('line_country_header', "children"),
    Output('line_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('per', 'value'),
    Input("country_checklist", 'value'), )
def Sales_country_line_card(value, per_filter, countries):
    value = 'Sales volume' if value else 'Sales value'
    if not len(countries):
        return f'{value} per {per_filter}', go.Figure()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per_filter]

    S_columns = df.attrs['columns_dict'][value]
    Sales = df[[C_column] + S_columns]
    Sales = Sales.groupby(by=C_column).sum().reset_index(level=[C_column])
    fig = go.Figure()
    for index, row in Sales.iterrows():
        fig.add_trace(go.Scatter(x=S_columns, y=row[S_columns],
                                 mode='lines',
                                 name=row[C_column]))
    return f'{value} per {per_filter}', fig


@callback(
    Output('bar_country_header', "children"),
    Output('bar_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('per', 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input('range_checklist', "value"))
def MS_country_bar_card(value, per_filter, top, countries, range):
    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(countries):
        return f'Market Size/Growth in {value} per {per_filter}', go.Figure()
    market_share = None
    range.sort()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per_filter]

    S_columns = df.attrs['columns_dict'][value]
    S_columns=[S_columns[i] for i in range]
    df = df[[C_column] + S_columns]
    df = df.groupby(by=C_column).sum().reset_index(level=[C_column])

    df['MS'] = df[S_columns].sum(axis=1)
    df = df.sort_values('MS', )[:top]
    fig = go.Figure(data=[go.Bar(
        x=df['MS'],
        y=df[C_column],
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        orientation='h',
    )])
    if len(range) > 1:
        df['Growth'] = growth(data=df, begin=S_columns[0], final=S_columns[-1]).values
        step = df['MS'].max() / 16
        annotations = [dict(xref='x', yref='y',
                            y=zd, x=xd + step,
                            text=str(yd) + '%',
                            font=dict(family='Arial', size=12,
                                      color='rgb(50, 171, 96)'),
                            showarrow=False) for zd, yd, xd in
                       zip(df[C_column], df['Growth'].round(decimals=2), df['MS'])]
        fig.update_layout(annotations=annotations)

    return f'Market Size/Growth in {value} per {per_filter}', fig


@callback(
    Output('bubble_country_header', "children"),
    Output('bubble_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('per', 'value'),
    Input("country_checklist", 'value'),
    Input('range_checklist', "value"))
def country_bubble_card(value, per, countries, range):
    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(countries):
        return f'Market Size/CAGR/Share in {value.split()[1]} per {per.split()[0]}', go.Figure()
    range.sort()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per]
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    df = df[[C_column] + S_columns]
    df = df.groupby(by=C_column).sum().reset_index(level=[C_column])
    df['Sales'] = df[S_columns].sum(1)
    begin = S_columns[0]
    final = S_columns[-1]
    t = range[-1] - range[0]
    df['CAGR'] = cagr(df,begin=begin, final=final, t=t).values * 100
    df['MS'] = (df['Sales'] / df['Sales'].sum())*100

    fig = go.Figure(data=[go.Scatter(
        x=df['Sales'], y=df['CAGR'],
        mode='markers',
        text=df[C_column],
        marker=dict(
        size=df['MS'],
        color=df['MS'],
        sizemode='area',
        sizeref=2.*(df['MS'].max())/(40.**2),
        sizemin=4
    )
    )])
    return f'Market Size/CAGR/Share in {value.split()[1]} per {per.split()[0]}', fig







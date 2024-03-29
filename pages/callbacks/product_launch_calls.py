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
    Output({'index': ALL, 'level': 'country'}, "max"),
    Output('pie_top', 'max'),
    Output('bar_top', 'max'),
    Input("country_checklist", 'value'),
    Input('pie_per', 'value'),
    Input('bar_per', 'value'),
)
def update_filters(countries, pie_per,bar_per):
    ctx = dash.callback_context
    n = len(ctx.outputs_list[0])
    output = [[len(countries)] * n]
    T_column = facade.current_template.clean_data.attrs['columns_dict'][pie_per]
    C_column = facade.current_template.clean_data.attrs['columns_dict']['Country level']
    df = facade.current_template.clean_data
    output.append(df[df[C_column].isin(countries)][T_column].unique().shape[0])
    T_column = facade.current_template.clean_data.attrs['columns_dict'][bar_per]
    output.append(df[df[C_column].isin(countries)][T_column].unique().shape[0])
    return output


@callback(
    Output('MS_country_header', "children"),
    Output('MS_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input("country_checklist", 'value'),
)
def market_size(value,countries):
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]

    if value:
        ms_volume = df[df.attrs['columns_dict']['Sales volume']].sum(axis=1).sum()
        return "Market size in volume", str(ms_volume)
    else:
        ms_value = df[df.attrs['columns_dict']['Sales value']].sum(axis=1).sum()
        return "Market size in value", str(ms_value)


@callback(
    Output('cagr_country_header', "children"),
    Output('cagr_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input("country_checklist", 'value'),
)
def cagr_card(value,countries):
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']

    df = df[df[C_column].isin(countries)]
    if value:

        volume = df[df.attrs['columns_dict']['Sales volume']].sum()
        begin = df.attrs['columns_dict']['Sales volume'][0]
        final = df.attrs['columns_dict']['Sales volume'][-1]
        t = len(df.attrs['columns_dict']['Sales volume']) - 1
        return "CAGR in volume", "{:.2f}%".format(cagr(begin=[volume[begin]], final=[volume[final]], t=t)[0] * 100)
    else:
        value = df[df.attrs['columns_dict']['Sales value']].sum()
        begin = df.attrs['columns_dict']['Sales value'][0]
        final = df.attrs['columns_dict']['Sales value'][-1]
        t = len(df.attrs['columns_dict']['Sales value']) - 1

        return "CAGR in value", "{:.2f}%".format(cagr(begin=[value[begin]], final=[value[final]], t=t)[0] * 100)


@callback(
    Output('RS_country_header', "children"),
    Output('RS_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input({'index': 'RS_top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),)
def RS_card(value, top,countries):
    country_sales = None
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]

    if value:
        S_columns = df.attrs['columns_dict']['Sales volume']
        volume = df[[C_column] + S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['Sales'] = volume[S_columns].sum(1)
        country_sales = volume.sort_values('Sales', ascending=False)[[df.attrs['columns_dict']['Country level'], 'Sales']][:top].values
        msg = "Ranking by sales in volume"
    else:
        S_columns = df.attrs['columns_dict']['Sales value']
        value = df[[C_column] + S_columns]
        value = value.groupby(by=C_column).sum().reset_index(level=[C_column])
        value['Sales'] = value[S_columns].sum(1)
        country_sales = value.sort_values('Sales', ascending=False)[[
            df.attrs['columns_dict']['Country level'], 'Sales']][:top].values
        msg = "Ranking by sales in value"
    body = [html.Tbody([html.Tr([html.Td(country[0]), html.Td(country[1])]) for country in country_sales])]
    headers = [html.Thead(html.Tr([html.Th("Country"), html.Th("Sales")]))]

    table = dbc.Table(headers + body)

    return msg, table


@callback(
    Output('RG_country_header', "children"),
    Output('RG_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input({'index': 'RG_top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),)
def RG_card(value, top,countries):
    country_growth = None
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]

    if value:
        S_columns = df.attrs['columns_dict']['Sales volume']
        volume = df[[C_column] + S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['Growth'] = growth(data=volume, begin=S_columns[0], final=S_columns[-1])
        country_growth = volume.sort_values('Growth', ascending=False)[[
            df.attrs['columns_dict']['Country level'], 'Growth']][:top].values
        msg = "Ranking by Growth in volume"
    else:
        S_columns = df.attrs['columns_dict']['Sales value']
        value = df[[C_column] + S_columns]
        value = value.groupby(by=C_column).sum().reset_index(level=[C_column])
        value['Growth'] = growth(data=value, begin=S_columns[0], final=S_columns[-1])
        country_growth = value.sort_values('Growth', ascending=False)[[
            df.attrs['columns_dict']['Country level'], 'Growth']][:top].values
        msg = "Ranking by Growth in value"
    body = [html.Tbody(
        [html.Tr([html.Td(country[0]), html.Td("{:.2f}%".format(country[1] * 100))]) for country in country_growth])]
    headers = [html.Thead(html.Tr([html.Th("Country"), html.Th("Growth")]))]

    table = dbc.Table(headers + body)

    return msg, table


@callback(
    Output('pie_country_header', "children"),
    Output('pie_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('pie_per', 'value'),
    Input('pie_top', 'value'),
    Input("country_checklist", 'value'),
    Input('pie_country_slider', "value"),)
def MS_country_pie_card(value, per_filter, top, countries,range):
    market_share = None
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per_filter]
    if value:
        S_columns = df.attrs['columns_dict']['Sales volume'][range[0]:range[1]+1]
        volume = df[[C_column] + S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['MS'] = volume[S_columns].sum(axis=1)
        volume['MS'] = volume['MS'] / volume['MS'].sum()
        market_share = volume.sort_values('MS', ascending=False)[[C_column, 'MS']][:top]
        msg = f"Market share per {per_filter} in volume"
    else:
        S_columns = df.attrs['columns_dict']['Sales value'][range[0]:range[1]+1]
        value = df[[C_column] + S_columns]
        value = value.groupby(by=C_column).sum().reset_index(level=[C_column])
        value['MS'] = value[S_columns].sum(axis=1)
        value['MS'] = value['MS'] / value['MS'].sum()
        market_share = value.sort_values('MS', ascending=False)[[C_column, 'MS']][:top]
        msg = f"Market share per {per_filter} in value"
    fig = go.Figure(data=[go.Pie(labels=market_share[C_column], values=market_share['MS'], textinfo='label+percent',
                                 insidetextorientation='radial'
                                 )])

    return msg, fig


@callback(
    Output('pie_country_slider', "min"),
    Output('pie_country_slider', "max"),
    Output('pie_country_slider', "marks"),
    Output('pie_country_slider', "value"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value')
)
def set_country_pie_slider_params(value):
    switch_vol_val= 'Sales volume' if value else 'Sales value'
    S_columns = facade.current_template.clean_data.attrs['columns_dict'][switch_vol_val]
    return 0 ,len(S_columns)-1,dict(list(enumerate(S_columns))),[0 ,len(S_columns)-1]



@callback(
    Output('line_country_header', "children"),
    Output('line_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('line_per', 'value'),
    Input("country_checklist", 'value'),)
def Sales_country_line_card(value, per_filter, countries):
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per_filter]
    value = 'Sales volume' if value else 'Sales value'
    S_columns = df.attrs['columns_dict'][value]
    Sales = df[[C_column] + S_columns]
    Sales = Sales.groupby(by=C_column).sum().reset_index(level=[C_column])
    fig = go.Figure()
    for index, row in Sales.iterrows():
        fig.add_trace(go.Scatter(x=S_columns, y=row[S_columns],
                                 mode='lines',
                                 name=row[C_column]))
    return f'{value} per {per_filter}',fig


@callback(
    Output('bar_country_header', "children"),
    Output('bar_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('bar_per', 'value'),
    Input('bar_top', 'value'),
    Input("country_checklist", 'value'),)
def MS_country_bar_card(value, per_filter,top, countries):
    market_share = None
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per_filter]
    value = 'Sales volume' if value else 'Sales value'
    S_columns = df.attrs['columns_dict'][value]
    df = df[[C_column] + S_columns]
    df = df.groupby(by=C_column).sum().reset_index(level=[C_column])
    df['Growth'] = growth(data=df, begin=S_columns[0], final=S_columns[-1])
    df['MS'] = df[S_columns].sum(axis=1)
    df = df.sort_values('MS',)[:top]
    step = df['MS'].max()/16

    annotations=[dict(xref='x', yref='y',
                            y=zd, x=xd + step,
                            text=str(yd) + '%',
                            font=dict(family='Arial', size=12,
                                      color='rgb(50, 171, 96)'),
                            showarrow=False) for zd,yd,xd in zip(df[C_column], df['Growth'].round(decimals=2),df['MS'])]

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

    print(df['MS'])
    fig.update_layout(annotations=annotations)

    return f'Market Size/Growth in {value} per {per_filter}',fig
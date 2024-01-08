from app import app, facade
from dash import Input, Output, callback, no_update
from erikusa.metrics import cagr, growth
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from dash import dcc, html, Input, State, Output, callback, ALL, MATCH
import dash
import plotly.express as px
from dash import no_update
from dash.exceptions import PreventUpdate
custom_template = {
    "layout": go.Layout(
        font={
            "family": "Nunito",
            "size": 12,
            "color": "#707070",
        },
        title={
            "font": {
                "family": "Lato",
                "size": 18,
                "color": "#1f1f1f",
            },
        },
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        colorway=px.colors.qualitative.G10,
    )
}

def trim_sales(number):
    length = len(str(round(number)))

    d, m = divmod(length, 3)

    d = d if m else d - 1
    conv_dict = {1: str(round(number / 10 ** 3, 2)) + 'K',
                 2: str(round(number / 10 ** 6, 2)) + 'M',
                 3: str(round(number / 10 ** 9, 2)) + 'B',
                 0: str(number)}
    return conv_dict[d]


def trim_percentage(number):
    return round(number * 100, 2)


def style_percentage(percent):
    if percent > 0:
        return html.P(f'+{percent}%', style={'color': 'rgb(0 135 60)'}, className='m-0')
    if percent < 0:
        return html.P(f'{percent}%', style={'color': 'rgb(235 15 41)'}, className='m-0')
    else:
        return html.P(f'{percent}%', className='m-0')


def cagr_style(number):
    percent = round(number * 100, 2)
    if percent > 0:
        return html.H5(f'+{percent}%', className='p-0 m-0 card-value', style={'color': 'rgb(0 135 60)'})
    if percent < 0:
        return html.H5(f'{percent}%', className='p-0 m-0 card-value', style={'color': 'rgb(235 15 41)'})
    else:
        return html.H5(f'{percent}%', className='p-0 m-0 card-value')


triming_dict = {
    'Market size volume': trim_sales,
    'Market size value': trim_sales,
    'Market share volume': lambda x: style_percentage(trim_percentage(x)),
    'Growth in Volume': lambda x: style_percentage(trim_percentage(x)),
    'CAGR in volume': lambda x: style_percentage(trim_percentage(x)),
    'Market share value': lambda x: style_percentage(trim_percentage(x)),
    'Growth in value': lambda x: style_percentage(trim_percentage(x)),
    'CAGR in value': lambda x: style_percentage(trim_percentage(x)),
}


@callback(
    Output({'index': 'top', 'level': 'country'}, "max"),
    Output({'index': 'range_checklist', 'level': 'Country level'}, 'options'),
    Output({'index': 'range_checklist', 'level': 'Country level'}, 'value'),
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
    if triggered_id in ['{"index":"sales_toggle","type":"Country level"}',
                        '{"index":"sales_toggle","type":"Family level"}']:
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
    Input({'index': 'range_checklist', 'level': 'Country level'}, 'value'),
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
    return f"Market size in {msg}", trim_sales(ms)


@callback(
    Output('cagr_country_header', "children"),
    Output('cagr_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input("country_checklist", 'value'),
    Input({'index': 'range_checklist', 'level': 'Country level'}, 'value'))
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
        cagr_v = 0 if t == 0 else cagr(begin=[sales[begin]], final=[sales[final]], t=t)[0]
        return f"CAGR in {value.split()[1]}", cagr_style(cagr_v)
    return f"CAGR in {value.split()[1]}", cagr_style(0)


@callback(
    Output('RS_country_header', "children"),
    Output('RS_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input({'index': 'range_checklist', 'level': 'Country level'}, 'value'),
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
    volume['TSales'] = volume['Sales'].apply(trim_sales)
    country_sales = volume.sort_values('Sales', ascending=False)[
                        [df.attrs['columns_dict'][per], 'TSales']][:top].values
    msg = f"Ranking {per.split()[0]} by sales in {value.split()[1]}"
    body = []
    if len(range):
        body = [html.Tbody([html.Tr([html.Td(country[0]), html.Td(country[1])]) for country in country_sales])]
    headers = [html.Thead(html.Tr([html.Th(per.split()[0]), html.Th("Sales")]))]

    table = dbc.Table(headers + body, className='data-table')

    return msg, table


@callback(
    Output('RG_country_header', "children"),
    Output('RG_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input({'index': 'range_checklist', 'level': 'Country level'}, 'value'),
    Input('per', 'value'), )
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
    if len(range) > 1 and len(countries):
        S_columns = df.attrs['columns_dict'][value]
        S_columns = [S_columns[i] for i in range]
        volume = df[[C_column] + S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['Growth'] = growth(data=volume, begin=S_columns[0], final=S_columns[-1]).values
        country_growth = volume.sort_values('Growth', ascending=False)[[
            df.attrs['columns_dict'][per], 'Growth']][:top].values
        body = [html.Tbody(
            [html.Tr([html.Td(country[0]), html.Td(triming_dict['CAGR in volume'](country[1]))]) for country in
             country_growth])]

    headers = [html.Thead(html.Tr([html.Th(per.split()[0]), html.Th("Growth")]))]
    table = dbc.Table(headers + body, className='data-table')
    return msg, table


@callback(
    Output('pie_country_header', "children"),
    Output('pie_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('per', 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input({'index': 'range_checklist', 'level': 'Country level'}, "value"), )
def MS_country_pie_card(value, per_filter, top, countries, range):
    market_share = None

    range.sort()
    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(countries) and not top:
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
    top = top if ms.shape[0] > top else ms.shape[0]
    ms.sort_values('MS', ascending=False, inplace=True)
    results = ms[:top]
    if ms.shape[0] > top:
        tmp = ms[S_columns + ['MS']][top:].sum()
        tmp[C_column] = f'Others ({ms.shape[0] - top})'
        results = results.append(tmp, ignore_index=True)
    results['MS'] = results['MS'] / results['MS'].sum()
    market_share = results[[C_column, 'MS']]
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

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=f"Sales in{value.split()[1]}",
        legend_title="Countries",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )
    return f'{value} per {per_filter}', fig


@callback(
    Output('bar_country_header', "children"),
    Output('bar_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('per', 'value'),
    Input({'index': 'top', 'level': 'country'}, 'value'),
    Input("country_checklist", 'value'),
    Input({'index': 'range_checklist', 'level': 'Country level'}, "value"))
def MS_country_bar_card(value, per_filter, top, countries, range):
    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(countries) or not top:
        return f'Market Size/Growth in {value} per {per_filter}', go.Figure()
    market_share = None
    range.sort()
    df = facade.current_template.clean_data
    C_column = df.attrs['columns_dict']['Country level']
    df = df[df[C_column].isin(countries)]
    C_column = df.attrs['columns_dict'][per_filter]

    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    df = df[[C_column] + S_columns]
    df = df.groupby(by=C_column).sum().reset_index(level=[C_column])

    df['MS'] = df[S_columns].sum(axis=1)
    df = df.sort_values('MS', )[-top:]
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
        step = df['MS'].max() / 14
        annotations = [dict(xref='x', yref='y',
                            y=zd, x=xd + step,
                            text=str(yd) + '%',
                            font=dict(family='Arial', size=12,
                                      color='rgb(50, 171, 96)'),
                            showarrow=False) for zd, yd, xd in
                       zip(df[C_column], (df['Growth']*100).round(decimals=2), df['MS'])]
        fig.update_layout(annotations=annotations)
    fig.update_layout(
        xaxis_title="Market size / Growth%",
        yaxis_title="Country",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )

    return f'Market Size/Growth in {value} per {per_filter}', fig


@callback(
    Output('bubble_country_header', "children"),
    Output('bubble_country', "figure"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('per', 'value'),
    Input("country_checklist", 'value'),
    Input({'index': 'range_checklist', 'level': 'Country level'}, "value"))
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
    df['CAGR'] = cagr(df, begin=begin, final=final, t=t).values * 100
    df['MS'] = (df['Sales'] / df['Sales'].sum()) * 100

    fig = go.Figure(data=[go.Scatter(
        x=df['Sales'], y=df['CAGR'],
        mode='markers',
        text=df[C_column],
        marker=dict(
            size=df['MS'],
            color=df['MS'],
            sizemode='area',
            sizeref=2. * (df['MS'].max()) / (40. ** 2),
            sizemin=4
        )
    )])
    fig.update_layout(
        xaxis_title="Market size",
        yaxis_title="CAGR",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )

    return f'Market Size/CAGR/Share in {value.split()[1]} per {per.split()[0]}', fig

def cagr_desc(cagr):
    if cagr > 10:
        return " an interesting"
    if 0 > cagr:
        return "a low"
    else:
        return "a"

@callback(
    Output('summary_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input("country_checklist", 'value'),)
def country_bubble_card(value,countries):

    value = 'Sales volume' if value else 'Sales value'
    c_column = facade.current_template.clean_data.attrs['columns_dict']['Country level']
    s_column = facade.current_template.clean_data.attrs['columns_dict'][value]
    df = facade.current_template.clean_data
    df = df[df[c_column].isin(countries)]
    if not df.shape[0]:
        return dbc.Alert('There is no enough data, please check your input file or filters', color="danger")
    country_num=df[c_column].unique().shape[0]
    msize= df[s_column].sum(axis=1).sum()
    begin = s_column[0]
    final = s_column[-1]
    sales = df[[begin, final]].sum()
    t = len(s_column)-1
    cagr_v = 0 if t == 0 else cagr(begin=[sales[begin]], final=[sales[final]], t=t)[0]

    df_score = facade.current_template.country_scores
    top= 5 if country_num > 5 else 1
    df_score = df_score[df_score[c_column].isin(countries)][:top]
    top_countries = df_score[c_column].tolist()
    g_column = f'Growth in {value.split()[1]}'
    ms_column = f"Market size {value.split()[1]}"
    point=f"The total market {value.split()[1]} size in these {country_num} countries is equal to {trim_sales(msize)}"
    if t != 0:
        cagr_v= trim_percentage(cagr_v)
        description= cagr_desc(cagr_v)
        point+= f" with {description} CAGR equal to {cagr_v}% over the last {t+1} years. "
    list_elements=[html.Li(point)]

    if top ==1:
        ms=df_score[ms_column].iloc[0]
        gc = df_score[g_column].iloc[0]
        point=f"Our assessment shows that {top_countries[0]} is the most dynamic and interesting market in terms of market size ({trim_sales(ms)}) and market growth ({round(gc * 100, 2)}%)."
        list_elements.append(html.Li(point))

    elif top >1:
        print(df_score.columns)
        country_string = ', and '.join([', '.join(top_countries[:-1]),top_countries[-1]])
        point = f"Our assessment shows that {country_string} is the most dynamic and interesting market in terms of market size and market growth."
        list_elements.append(html.Li(point))
        df_score.sort_values(ms_column, ascending=False, inplace=True)
        point = f"{df_score[c_column].iloc[0]} is the largest market in sales {value.split()[1]} with {trim_sales(df_score[ms_column].iloc[0])} followed by {df_score[c_column].iloc[1]} and {df_score[c_column].iloc[2]} with {trim_sales(df_score[ms_column].iloc[1])} and {trim_sales(df_score[ms_column].iloc[2])} respectively."

        if t != 0:
            df_score.sort_values(g_column, ascending=False, inplace=True)
            point+=f" and {df_score[c_column].iloc[0]} is the fastest growing market with {round(df_score[g_column].iloc[0] * 100, 2)}% over the last {t} {'years' if t > 1 else 'year'}"
        list_elements.append(html.Li(point))
    return html.P(html.Ul(list_elements))


# @callback(
#    Output('scoring_country', "children"),
#    Input({'index': 'top', 'level': 'country'}, 'value'),
#    Input("country_checklist", 'value'),
#)
#def country_scoring_table(top, countries):
    #    df = facade.current_template.country_scores
    #c_column = df.attrs['columns']['Country level']
    #m_columns = df.attrs['columns']['Score Column']
    #df = df[df[c_column].isin(countries)][:top]
    #rows = [html.Tr(
    #    [html.Td(country[c_column])] + [html.Td(round(country['Score'], 1))])
    #    for _, country in df.iterrows()]
    #body = [html.Tbody(rows)]
    #headers = [
    #    html.Thead(html.Tr([html.Th('Country')] + [html.Th("Score")]))]

    #    table = dbc.Table(headers + body, className='data-table')

#    return table


@callback(
    Output({'index': 'top', 'level': 'family'}, "max"),
    Output({'type': 'family_checklist', 'level': 'family'}, 'options'),
    Output({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Output({'index': 'range_checklist', 'level': 'Family level'}, 'options'),
    Output({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input('select_all_family', 'n_clicks'),
    Input('clear_all_family', 'n_clicks'),
    State({'type': 'family_checklist', 'level': 'family'}, 'options'),
    State({'type': 'family_checklist', 'level': 'family'}, 'disabled'))
def update_filters(families, country, value, select_click, clear_click, all_options, disabled):
    T_column = facade.current_template.clean_data.attrs['columns_dict']['Family level']
    F_column = facade.current_template.clean_data.attrs['columns_dict']['Family level']
    ctx = dash.callback_context
    df = facade.current_template.clean_data
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id in (
            '{"type":"family_checklist","level":"country"}',
            '{"level":"country","type":"family_checklist"}') and not disabled:
        C_column = facade.current_template.clean_data.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
        options = [{"label": column, "value": column} for column in list(df[F_column].unique())]
        max = df[T_column].unique().shape[0]
        return max, options, list(df[F_column].unique()), no_update, no_update
    elif triggered_id in (
            '{"type":"family_checklist","level":"family"}', '{"level":"family","type":"family_checklist"}',
            '{"type":"select","level":"family",'
            '"index":"per"}',):
        df = df[df[F_column].isin(families)]
        max = df[T_column].unique().shape[0]
        return max, no_update, no_update, no_update, no_update
    elif triggered_id == '{"index":"sales_toggle","level":"Family level"}':
        value = 'Sales volume' if value else 'Sales value'
        S_columns = facade.current_template.clean_data.attrs['columns_dict'][value]
        options = [{"label": column, "value": index} for index, column in enumerate(S_columns)]
        return no_update, no_update, no_update, options, list(range(len(S_columns)))
    elif triggered_id == 'select_all_family':
        return no_update, no_update, [option['value'] for option in all_options], no_update, no_update

    elif triggered_id == 'clear_all_family':
        return no_update, no_update, [], no_update, no_update

    return no_update, no_update, no_update, no_update, no_update


@callback(
    Output('MS_family_header', "children"),
    Output('MS_family', "children"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'),

)
def market_size(value, families, country, range, disabled):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]

    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    value, msg = ('Sales volume', 'volume') if value else ('Sales value', 'value')
    S_column = df.attrs['columns_dict'][value]
    S_column = [S_column[i] for i in range]
    ms = df[S_column].sum(axis=1).sum()
    return f"Market size in {msg}", trim_sales(ms)


@callback(
    Output('cagr_family_header', "children"),
    Output('cagr_family', "children"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'), )
def cagr_card(value, families, country, range, disabled):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    value = 'Sales volume' if value else 'Sales value'
    S_columns = df.attrs['columns_dict'][value]
    if len(range) and len(families):
        begin = S_columns[range[0]]
        final = S_columns[range[-1]]
        sales = df[[begin, final]].sum()
        t = range[-1] - range[0]
        cagr_v = 0 if t == 0 else cagr(begin=[sales[begin]], final=[sales[final]], t=t)[0]
        return f"CAGR in {value.split()[1]}", cagr_style(cagr_v)
    return f"CAGR in {value.split()[1]}", cagr_style(0)


@callback(
    Output('RS_family_header', "children"),
    Output('RS_family', "children"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'index': 'top', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'), )
def RS_card(value, top, families, country, range, disabled):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    C_column = df.attrs['columns_dict']['Family level']
    value = 'Sales volume' if value else 'Sales value'
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    volume = df[[C_column] + S_columns]
    volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
    volume['Sales'] = volume[S_columns].sum(1)
    volume['TSales'] = volume['Sales'].apply(trim_sales)
    family_sales = volume.sort_values('Sales', ascending=False)[
                       [F_column, 'TSales']][:top].values
    msg = f"Ranking {'Family level'.split()[0]} by sales in {value.split()[1]}"
    body = []
    if len(range):
        body = [html.Tbody([html.Tr([html.Td(family[0]), html.Td(family[1])]) for family in family_sales])]
    headers = [html.Thead(html.Tr([html.Th('Family level'.split()[0]), html.Th("Sales")]))]

    table = dbc.Table(headers + body, className='data-table')

    return msg, table


@callback(
    Output('RG_family_header', "children"),
    Output('RG_family', "children"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'index': 'top', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'),
)
def RG_card(value, top, families, country, range, disabled):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    C_column = df.attrs['columns_dict']['Family level']
    value = 'Sales volume' if value else 'Sales value'
    body = []
    msg = f"Ranking {'Family level'.split()[0]} by Growth in {value.split()[1]}"
    if len(range) > 1 and len(families):
        S_columns = df.attrs['columns_dict'][value]
        S_columns = [S_columns[i] for i in range]
        volume = df[[C_column] + S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['Growth'] = growth(data=volume, begin=S_columns[0], final=S_columns[-1]).values
        family_growth = volume.sort_values('Growth', ascending=False)[[
            df.attrs['columns_dict']['Family level'], 'Growth']][:top].values
        body = [
            html.Tbody([html.Tr([html.Td(family[0]), html.Td(triming_dict['CAGR in volume'](family[1]))]) for family in
                        family_growth])]
    headers = [html.Thead(html.Tr([html.Th('Family level'.split()[0]), html.Th("Growth")]))]
    table = dbc.Table(headers + body, className='data-table')
    return msg, table


@callback(
    Output('pie_family_header', "children"),
    Output('pie_family', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'index': 'top', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'), )
def MS_family_pie_card(value, top, families, country, range, disabled):
    market_share = None

    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(families) or not top:
        return f"Market share per {'Family level'} in {value.split()[1]}", go.Figure()

    range.sort()
    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    C_column = df.attrs['columns_dict']['Family level']
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    ms = df[[C_column] + S_columns]

    ms = ms.groupby(by=C_column).sum().reset_index(level=[C_column])
    ms['MS'] = ms[S_columns].sum(axis=1)
    top = top if ms.shape[0] > top else ms.shape[0]
    ms.sort_values('MS', ascending=False, inplace=True)
    results = ms[:top]

    if ms.shape[0] > top:
        tmp = ms[S_columns + ['MS']][top:].sum()
        tmp[C_column] = f'Others ({ms.shape[0] - top})'
        results = results.append(tmp, ignore_index=True)
    results['MS'] = results['MS'] / results['MS'].sum()
    market_share = results[[C_column, 'MS']]
    msg = f"Market share per {'Family level'} in {value.split()[1]}"
    fig = go.Figure(data=[go.Pie(labels=market_share[C_column], values=market_share['MS'], textinfo='label+percent',
                                 insidetextorientation='radial')])
    return msg, fig


@callback(
    Output('line_family_header', "children"),
    Output('line_family', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'),

)
def Sales_family_line_card(value, families, country, disabled):
    value = 'Sales volume' if value else 'Sales value'
    if not len(families):
        return f'{value} per Family level', go.Figure()

    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    C_column = df.attrs['columns_dict']['Family level']

    S_columns = df.attrs['columns_dict'][value]
    Sales = df[[C_column] + S_columns]
    Sales = Sales.groupby(by=C_column).sum().reset_index(level=[C_column])
    fig = go.Figure()
    for index, row in Sales.iterrows():
        fig.add_trace(go.Scatter(x=S_columns, y=row[S_columns],
                                 mode='lines',
                                 name=row[C_column]))
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=f"Sales in{value.split()[1]}",
        legend_title="families",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )
    return f'{value} per Family level', fig


@callback(
    Output('bar_family_header', "children"),
    Output('bar_family', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'index': 'top', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'), )
def MS_family_bar_card(value, top, families, country, range, disabled):
    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(families) or top == 0:
        return f'Market Size/Growth in {value} per Family level', go.Figure()
    market_share = None
    range.sort()
    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    C_column = df.attrs['columns_dict']['Family level']

    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    df = df[[C_column] + S_columns]
    df = df.groupby(by=C_column).sum().reset_index(level=[C_column])

    df['MS'] = df[S_columns].sum(axis=1)
    df = df.sort_values('MS', )[-top:]
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
        step = df['MS'].max() / 14
        annotations = [dict(xref='x', yref='y',
                            y=zd, x=xd + step,
                            text=str(yd) + '%',
                            font=dict(family='Arial', size=12,
                                      color='rgb(50, 171, 96)'),
                            showarrow=False) for zd, yd, xd in
                       zip(df[C_column], (df['Growth']*100).round(decimals=2), df['MS'])]
        fig.update_layout(annotations=annotations)

    fig.update_layout(
        xaxis_title="Market size / Growth%",
        yaxis_title="Family",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )

    return f'Market Size/Growth in {value} per Family level', fig


@callback(
    Output('bubble_family_header', "children"),
    Output('bubble_family', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Family level'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'country'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Family level'}, 'value'),
    State({'type': 'family_checklist', 'level': 'country'}, 'disabled'))
def family_bubble_card(value, families, country, range, disabled):
    value = 'Sales volume' if value else 'Sales value'
    if not len(range) or not len(families):
        return f"Market Size/CAGR/Share in {value.split()[1]} per {'Family level'.split()[0]}", go.Figure()
    range.sort()
    df = facade.current_template.clean_data
    if not disabled:
        C_column = df.attrs['columns_dict']['Country level']
        df = df[df[C_column] == country]
    F_column = df.attrs['columns_dict']['Family level']
    df = df[df[F_column].isin(families)]
    C_column = df.attrs['columns_dict']['Family level']
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    df = df[[C_column] + S_columns]
    df = df.groupby(by=C_column).sum().reset_index(level=[C_column])
    df['Sales'] = df[S_columns].sum(1)
    begin = S_columns[0]
    final = S_columns[-1]
    t = range[-1] - range[0]
    df['CAGR'] = cagr(df, begin=begin, final=final, t=t).values * 100
    df['MS'] = (df['Sales'] / df['Sales'].sum()) * 100
    min_ms=df['MS'].min()
    min_ms=0 if min_ms>=0 else -min_ms
    fig = go.Figure(data=[go.Scatter(
        x=df['Sales'], y=df['CAGR'],
        mode='markers',
        text=df[C_column],
        marker=dict(
            size=df['MS']+min_ms,
            color= df['MS'],
            sizemode='area',
            sizeref=2. * (df['MS'].max()) / (40. ** 2),
            sizemin=4
        )
    )])

    fig.update_layout(
        xaxis_title="Market size",
        yaxis_title="CAGR",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )

    return f"Market Size/CAGR/Share in {value.split()[1]} per {'Family level'.split()[0]}", fig


@callback(
    Output('scoring_family', "children"),
    Input({'index': 'top', 'level': 'family'}, 'value'),
    Input({'type': 'family_checklist', 'level': 'family'}, 'value'),
)
def family_scoring_table(top, families):
    df = facade.current_template.family_scores

    f_column = df.attrs['columns']['levels']['Family']
    m_columns = df.attrs['columns']['Score Column']
    df = df[df[f_column].isin(families)][:top]
    rows = None
    headers = None
    match_dict = df.attrs['columns']['levels']
    if len(match_dict.keys()) > 1:
        rows = [html.Tr(
            [html.Td(country[match_dict['Country']]), html.Td(country[match_dict['Family']])] + [
                html.Td(round(country['Score'], 1))])
            for _, country in df.iterrows()]
        headers = [html.Thead(html.Tr([html.Th('Country'), html.Th('Family')] + [html.Th("Score")]))]
    else:
        rows = [html.Tr(
            [html.Td(country[match_dict['Family']])] + [
                html.Td(round(country['Score'], 1))])
            for _, country in df.iterrows()]
        headers = [html.Thead(html.Tr([html.Th('Family')] + [html.Th("Score")]))]

    body = [html.Tbody(rows)]
    table = dbc.Table(headers + body, className='data-table')

    return table


@callback(
    Output({'index': 'top', 'level': 'molecule'}, "max"),
    Output({'type': 'molecule_checklist', 'level': 'molecule'}, 'options'),
    Output({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Output({'type': 'molecule_checklist', 'level': 'family'}, 'options'),
    Output({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Output({'index': 'range_checklist', 'level': 'Molecule level'}, 'options'),
    Output({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),

    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input('select_all_molecule', 'n_clicks'),
    Input('clear_all_molecule', 'n_clicks'),

    State({'type': 'molecule_checklist', 'level': 'molecule'}, 'options'),
    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled'))
def update_filters(country, family, molecules, switch, select_all, clear_all, molecule_options, disabled_family,
                   disabled_country):
    df = facade.current_template.clean_data
    m_column = facade.current_template.clean_data.attrs['columns_dict']['Molecule level']
    f_column = facade.current_template.clean_data.attrs['columns_dict']['Family level']
    c_column = facade.current_template.clean_data.attrs['columns_dict']['Country level']
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id in ('{"type":"molecule_checklist","level":"country"}',
                        '{"level":"country","type":"molecule_checklist"}') and not disabled_country:
        families_options = no_update
        family_value = no_update
        molecules_options = no_update
        molecule_value = no_update
        if not disabled_family:
            family_scores = facade.current_template.family_scores
            family_scores = family_scores[family_scores[c_column] == country]
            top_num = family_scores[f_column].unique().shape[0]
            top_num = 5 if top_num > 5 else top_num
            top_families = list(family_scores[f_column][:top_num])
            families_options = [{"label": family, "value": family} for family in top_families]
            family_value = top_families[0]
            df = df[df[c_column] == country]
            molecule_value = list(df[df[f_column] == family_value][m_column].unique())
            molecules_options = [{"label": molecule, "value": molecule} for molecule in molecule_value]
        else:
            molecule_value = list(df[df[c_column] == country][m_column].unique())
            molecules_options = [{"label": molecule, "value": molecule} for molecule in molecule_value]
        return len(molecule_value), molecules_options, molecule_value, families_options, family_value, no_update, no_update

    if triggered_id in ('{"type":"molecule_checklist","level":"family"}',
                        '{"level":"family","type":"molecule_checklist"}') and not disabled_family:
        if not disabled_country:
            df = df[df[c_column] == country]
        df = df[df[f_column] == family]
        molecule_value = list(df[m_column].unique())
        molecules_options = [{"label": molecule, "value": molecule} for molecule in molecule_value]
        return len(molecule_value), molecules_options, molecule_value, no_update, no_update, no_update, no_update

    if triggered_id in (
    '{"type":"molecule_checklist","level":"molecule"}', '{"level":"molecule","type":"molecule_checklist"}'):
        return len(molecules), no_update, no_update, no_update, no_update, no_update, no_update

    if triggered_id in ('select_all_molecule'):
        molecules_value = [molecule["value"] for molecule in molecule_options]
        return len(molecules_value), no_update, molecules_value, no_update, no_update, no_update, no_update
    if triggered_id in ('clear_all_molecule'):
        return 0, no_update, [], no_update, no_update, no_update, no_update
    if triggered_id in (
    '{"index":"sales_toggle","level":"Molecule level"}', '{"level":"Molecule level","index":"sales_toggle"}'):
        switch_val_vol = 'Sales volume' if switch else 'Sales value'
        timeline = facade.current_template.clean_data.attrs['columns_dict'][switch_val_vol]
        timeline_options = [{"label": year, "value": index} for index, year in enumerate(timeline)]

        return no_update, no_update, no_update, no_update, no_update, timeline_options, list(range(len(timeline)))
    return no_update, no_update, no_update, no_update, no_update, no_update, no_update

@callback(
    Output('MS_molecule_header', "children"),
    Output('MS_molecule', "children"),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),

    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled')

)
def market_size(value, country, family, molecules, range, disabled_family, disabled_country):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_country:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]
    value, msg = ('Sales volume', 'volume') if value else ('Sales value', 'value')
    S_column = df.attrs['columns_dict'][value]
    S_column = [S_column[i] for i in range]
    ms = df[S_column].sum(axis=1).sum()
    return f"Market size in {msg}", trim_sales(ms)


@callback(
    Output('cagr_molecule_header', "children"),
    Output('cagr_molecule', "children"),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),

    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled'))
def cagr_card(value, country, family, molecules, range, disabled_family, disabled_country):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_country:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]

    value = 'Sales volume' if value else 'Sales value'
    S_columns = df.attrs['columns_dict'][value]
    if len(range) and len(molecules):
        begin = S_columns[range[0]]
        final = S_columns[range[-1]]
        sales = df[[begin, final]].sum()
        t = range[-1] - range[0]
        cagr_v = 0 if t == 0 else cagr(begin=[sales[begin]], final=[sales[final]], t=t)[0]
        return f"CAGR in {value.split()[1]}", cagr_style(cagr_v)
    return f"CAGR in {value.split()[1]}", cagr_style(0)


@callback(
    Output('RS_molecule_header', "children"),
    Output('RS_molecule', "children"),

    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'index': 'top', 'level': 'molecule'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),
    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled'))
def RS_card(switch, top, country, family, molecules, range, disabled_family, disabled_country):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_family:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]

    value = 'Sales volume' if switch else 'Sales value'
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    volume = df[[m_column] + S_columns]
    volume = volume.groupby(by=m_column).sum().reset_index(level=[m_column])
    volume['Sales'] = volume[S_columns].sum(1)
    volume['TSales'] = volume['Sales'].apply(trim_sales)
    molecule_sales = volume.sort_values('Sales', ascending=False)[
                       [m_column, 'TSales']][:top].values
    msg = f"Ranking {'Molecule level'.split()[0]} by sales in {value.split()[1]}"
    body = []
    if len(range):
        body = [html.Tbody([html.Tr([html.Td(molecule[0]), html.Td(molecule[1])]) for molecule in molecule_sales])]
    headers = [html.Thead(html.Tr([html.Th('Molecule level'.split()[0]), html.Th("Sales")]))]
    table = dbc.Table(headers + body, className='data-table')
    return msg, table


@callback(
    Output('RG_molecule_header', "children"),
    Output('RG_molecule', "children"),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'index': 'top', 'level': 'molecule'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),
    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled')
)
def RG_card(switch, top, country, family, molecules, range, disabled_family, disabled_country):
    range.sort()
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_family:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]

    value = 'Sales volume' if switch else 'Sales value'
    body = []
    msg = f"Ranking {'Molecule level'.split()[0]} by Growth in {value.split()[1]}"
    if len(range) > 1 and len(molecules):
        S_columns = df.attrs['columns_dict'][value]
        S_columns = [S_columns[i] for i in range]
        volume = df[[m_column] + S_columns]
        volume = volume.groupby(by=m_column).sum().reset_index(level=[m_column])
        volume['Growth'] = growth(data=volume, begin=S_columns[0], final=S_columns[-1]).values
        molecule_growth = volume.sort_values('Growth', ascending=False)[[
            df.attrs['columns_dict']['Molecule level'], 'Growth']][:top].values
        body = [
            html.Tbody([html.Tr([html.Td(molecule[0]), html.Td(triming_dict['CAGR in volume'](molecule[1]))]) for molecule in
                        molecule_growth])]
    headers = [html.Thead(html.Tr([html.Th('Molecule level'.split()[0]), html.Th("Growth")]))]
    table = dbc.Table(headers + body, className='data-table')
    return msg, table


@callback(
    Output('pie_molecule_header', "children"),
    Output('pie_molecule', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'index': 'top', 'level': 'molecule'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),
    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled'))
def MS_molecule_pie_card(switch, top, country, family, molecules, range, disabled_family, disabled_country):
    market_share = None

    value = 'Sales volume' if switch else 'Sales value'
    if not len(range) or not len(molecules) or not top:
        return f"Market share per {'Molecule level'} in {value.split()[1]}", go.Figure()

    range.sort()
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_family:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    ms = df[[m_column] + S_columns]


    ms = ms.groupby(by=m_column).sum().reset_index(level=[m_column])
    ms['MS'] = ms[S_columns].sum(axis=1)
    top = top if ms.shape[0] > top else ms.shape[0]
    ms.sort_values('MS', ascending=False,inplace=True)
    results = ms[:top]
    if ms.shape[0] > top:
        tmp = ms[S_columns + ['MS']][top:].sum()
        tmp[m_column] = f'Others ({ms.shape[0] - top})'
        results = results.append(tmp, ignore_index=True)
    results['MS'] = results['MS'] / results['MS'].sum()
    market_share = results[[m_column, 'MS']]
    msg = f"Market share per {'Molecule level'} in {value.split()[1]}"
    fig = go.Figure(data=[go.Pie(labels=market_share[m_column], values=market_share['MS'], textinfo='label+percent',
                                 insidetextorientation='radial')])
    return msg, fig



@callback(
    Output('line_molecule_header', "children"),
    Output('line_molecule', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled')

)
def Sales_molecule_line_card(value,country, family, molecules,  disabled_family, disabled_country):
    value = 'Sales volume' if value else 'Sales value'
    if not len(molecules):
        return f'{value} per Molecule level', go.Figure()

    df = facade.current_template.clean_data
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_family:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]

    S_columns = df.attrs['columns_dict'][value]
    Sales = df[[m_column] + S_columns]
    Sales = Sales.groupby(by=m_column).sum().reset_index(level=[m_column])
    fig = go.Figure()
    for index, row in Sales.iterrows():
        fig.add_trace(go.Scatter(x=S_columns, y=row[S_columns],
                                 mode='lines',
                                 name=row[m_column]))

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=f"Sales in{value.split()[1]}",
        legend_title="Molecules",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )

    return f'{value} per Molecule level', fig




@callback(
    Output('bar_molecule_header', "children"),
    Output('bar_molecule', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'index': 'top', 'level': 'molecule'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),
    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled'))
def MS_molecule_bar_card(switch, top, country, family, molecules, range, disabled_family, disabled_country):
    value = 'Sales volume' if switch else 'Sales value'
    if not len(range) or not len(molecules) or top == 0:
        return f'Market Size/Growth in {value} per Molecule level', go.Figure()
    market_share = None
    df = facade.current_template.clean_data
    range.sort()
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_family:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]

    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    df = df[[m_column] + S_columns]
    df = df.groupby(by=m_column).sum().reset_index(level=[m_column])

    df['MS'] = df[S_columns].sum(axis=1)
    df = df.sort_values('MS', )[-top:]
    fig = go.Figure(data=[go.Bar(
        x=df['MS'],
        y=df[m_column],
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
        step = df['MS'].max() / 14
        annotations = [dict(xref='x', yref='y',
                            y=zd, x=xd + step,
                            text=str(yd) + '%',
                            font=dict(family='Arial', size=12,
                                      color='rgb(50, 171, 96)'),
                            showarrow=False) for zd, yd, xd in
                       zip(df[m_column], (df['Growth']*100).round(decimals=2), df['MS'])]
        fig.update_layout(annotations=annotations)

    fig.update_layout(
        xaxis_title="Market size / Growth%",
        yaxis_title="Molecule",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )

    return f'Market Size/Growth in {value} per Molecule level', fig


@callback(
    Output('bubble_molecule_header', "children"),
    Output('bubble_molecule', "figure"),
    Input({'index': 'sales_toggle', 'level': 'Molecule level'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'country'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'family'}, 'value'),
    Input({'type': 'molecule_checklist', 'level': 'molecule'}, 'value'),
    Input({'index': 'range_checklist', 'level': 'Molecule level'}, 'value'),
    State({'type': 'molecule_checklist', 'level': 'family'}, 'disabled'),
    State({'type': 'molecule_checklist', 'level': 'country'}, 'disabled'))
def molecule_bubble_card(switch, country, family, molecules, range, disabled_family, disabled_country):
    value = 'Sales volume' if switch else 'Sales value'
    if not len(range) or not len(molecules):
        return f"Market Size/CAGR/Share in {value.split()[1]} per {'Molecule level'.split()[0]}", go.Figure()
    df = facade.current_template.clean_data
    range.sort()
    df = facade.current_template.clean_data
    if not disabled_country:
        c_column = df.attrs['columns_dict']['Country level']
        df = df[df[c_column] == country]
    if not disabled_family:
        f_column = df.attrs['columns_dict']['Family level']
        df = df[df[f_column] == family]

    m_column = df.attrs['columns_dict']['Molecule level']
    df = df[df[m_column].isin(molecules)]
    S_columns = df.attrs['columns_dict'][value]
    S_columns = [S_columns[i] for i in range]
    df = df[[m_column] + S_columns]
    df = df.groupby(by=m_column).sum().reset_index(level=[m_column])
    df['Sales'] = df[S_columns].sum(1)
    begin = S_columns[0]
    final = S_columns[-1]
    t = range[-1] - range[0]
    df['CAGR'] = cagr(df, begin=begin, final=final, t=t).values * 100
    df['MS'] = (df['Sales'] / df['Sales'].sum()) * 100
    min_ms=df['MS'].min()
    min_ms=0 if min_ms>=0 else -min_ms
    fig = go.Figure(data=[go.Scatter(
        x=df['Sales'], y=df['CAGR'],
        mode='markers',
        text=df[m_column],
        marker=dict(
            size=df['MS']+min_ms,
            color= df['MS'],
            sizemode='area',
            sizeref=2. * (df['MS'].max()) / (40. ** 2),
            sizemin=4
        )
    )])

    fig.update_layout(
        xaxis_title="Market size",
        yaxis_title="CAGR",
        font=dict(
            family="Times New Roman",
            color="grey"
        )
    )


    return f"Market Size/CAGR/Share in {value.split()[1]} per {'Molecule level'.split()[0]}", fig




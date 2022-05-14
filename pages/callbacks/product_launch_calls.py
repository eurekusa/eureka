from app import app, facade
from dash import Input, Output, callback, no_update
from erikusa.metrics import cagr,growth
import dash_bootstrap_components as dbc
from dash import dcc, html


@callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")]
)
def tab_content(active_tab):
    return facade.current_template.tabs_dict[active_tab]


@callback(
    Output('MS_country_header', "children"),
    Output('MS_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value')
)
def market_size(value):
    if value:
        ms_volume = facade.current_template.clean_data[
            facade.current_template.clean_data.attrs['columns_dict']['Sales volume']].sum(axis=1).sum()

        return "Market size in volume", str(ms_volume)
    else:
        ms_value = facade.current_template.clean_data[
            facade.current_template.clean_data.attrs['columns_dict']['Sales value']].sum(axis=1).sum()

        return "Market size in value", str(ms_value)


@callback(
    Output('cagr_country_header', "children"),
    Output('cagr_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value')
)
def cagr_card(value):
    if value:


        volume = facade.current_template.clean_data[
            facade.current_template.clean_data.attrs['columns_dict']['Sales volume']].sum()
        begin = facade.current_template.clean_data.attrs['columns_dict']['Sales volume'][0]
        final = facade.current_template.clean_data.attrs['columns_dict']['Sales volume'][-1]
        t = len(facade.current_template.clean_data.attrs['columns_dict']['Sales volume']) - 1
        return "CAGR in volume", "{:.2f}%".format(cagr(begin=[volume[begin]], final=[volume[final]], t=t)[0] * 100)
    else:
        value = facade.current_template.clean_data[
            facade.current_template.clean_data.attrs['columns_dict']['Sales value']].sum()
        begin = facade.current_template.clean_data.attrs['columns_dict']['Sales value'][0]
        final = facade.current_template.clean_data.attrs['columns_dict']['Sales value'][-1]
        t = len(facade.current_template.clean_data.attrs['columns_dict']['Sales value']) - 1

        return "CAGR in value", "{:.2f}%".format(cagr(begin=[value[begin]], final=[value[final]], t=t)[0] * 100)


@callback(
    Output('RS_country_header', "children"),
    Output('RS_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('RS_top', 'value'), )
def RS_card(value, top):
    country_sales = None
    C_column = facade.current_template.clean_data.attrs['columns_dict']['Country level']
    if value:
        S_columns=facade.current_template.clean_data.attrs['columns_dict']['Sales volume']
        volume = facade.current_template.clean_data[[C_column]+S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['Sales'] = volume[S_columns].sum(1)
        country_sales = volume.sort_values('Sales', ascending=False)[[
            facade.current_template.clean_data.attrs['columns_dict']['Country level'], 'Sales']][:top].values
        msg = "Ranking by sales in volume"
    else:
        S_columns = facade.current_template.clean_data.attrs['columns_dict']['Sales value']
        value = facade.current_template.clean_data[[C_column] + S_columns]
        value = value.groupby(by=C_column).sum().reset_index(level=[C_column])
        value['Sales'] = value[S_columns].sum(1)
        country_sales = value.sort_values('Sales', ascending=False)[[
            facade.current_template.clean_data.attrs['columns_dict']['Country level'], 'Sales']][:top].values
        msg = "Ranking by sales in value"
    body = [html.Tbody([html.Tr([html.Td(country[0]), html.Td(country[1])]) for country in country_sales])]
    headers = [html.Thead(html.Tr([html.Th("Country"), html.Th("Sales")]))]

    table = dbc.Table(headers + body)

    return msg, table


@callback(
    Output('RG_country_header', "children"),
    Output('RG_country', "children"),
    Input({'index': 'sales_toggle', 'type': 'Country level'}, 'value'),
    Input('RG_top', 'value'), )
def RG_card(value, top):
    country_growth = None
    C_column = facade.current_template.clean_data.attrs['columns_dict']['Country level']
    if value:
        S_columns = facade.current_template.clean_data.attrs['columns_dict']['Sales volume']
        volume = facade.current_template.clean_data[[C_column] + S_columns]
        volume = volume.groupby(by=C_column).sum().reset_index(level=[C_column])
        volume['Growth'] = growth(data=volume,begin=S_columns[0],final=S_columns[-1])
        country_growth = volume.sort_values('Growth', ascending=False)[[
            facade.current_template.clean_data.attrs['columns_dict']['Country level'], 'Growth']][:top].values
        msg = "Ranking by Growth in volume"
    else:
        S_columns = facade.current_template.clean_data.attrs['columns_dict']['Sales value']
        value = facade.current_template.clean_data[[C_column] + S_columns]
        value = value.groupby(by=C_column).sum().reset_index(level=[C_column])
        value['Growth'] = growth(data=value, begin=S_columns[0], final=S_columns[-1])
        country_growth = value.sort_values('Growth', ascending=False)[[
            facade.current_template.clean_data.attrs['columns_dict']['Country level'], 'Growth']][:top].values
        msg = "Ranking by Growth in value"
    body = [html.Tbody([html.Tr([html.Td(country[0]), html.Td("{:.2f}%".format(country[1]*100))]) for country in country_growth])]
    headers = [html.Thead(html.Tr([html.Th("Country"), html.Th("Growth")]))]

    table = dbc.Table(headers + body)

    return msg, table

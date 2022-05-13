import pandas as pd
from .template_interface import FormalTemplateInterface
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from pandas.api.types import is_numeric_dtype
from dash import no_update
from collections import Counter
from dash import Input, Output, html


class TestTemplate(FormalTemplateInterface):
    def __init__(self):
        self.name = '<template_unique_name>'
        self.description = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ' \
                           'ut labore et dolore magna aliqua. Aliquam id diam maecenas ultricies mi eget. Mi bibendum ' \
                           'neque egestas congue quisque egestas diam in arcu. Non curabitur gravida arcu ac. '
        self.imgPreview = 'test_preview.webp'
        self.tags = ['<tag1>', '<tag2>']
        self.pipline_index = 0
        self.pipline = [self.cat_num_columns, self.rank_class_sales, self.build_dataframe, self.empty_func]
        self.clean_data = None
        self.layout = None
        self.current_layout = None
        self.clean_data = None
        self.tabs_dict = dict()
        self.cat_options = [
            {"label": "Country level", "value": "Country level"},
            {"label": "Family level", "value": "Family level"},
            {"label": 'Molecule level', "value": 'Molecule level'},
            {"label": 'Brand level', "value": 'Brand level'},
            {"label": 'Discard column', "value": "Discard column"}]
        self.num_options = [
            {"label": "Sales volume", "value": "Sales volume"},
            {"label": "Sales value", "value": "Sales value"},
            {"label": 'Discard column', "value": 'Discard column'}, ]
        self.columns_dict = {'Country level': None,
                             'Family level': None,
                             'Molecule level': None,
                             'Brand level': None,
                             'Sales volume': [],
                             'Sales value': []}
        self.match_columns = {'Sales value': lambda x: self.columns_dict['Sales value'].append(x),
                              'Sales volume': lambda x: self.columns_dict['Sales volume'].append(x),
                              'Country level': lambda x: self.columns_dict.update({'Country level': x}, ),
                              'Family level': lambda x: self.columns_dict.update({'Family level': x}, ),
                              'Molecule level': lambda x: self.columns_dict.update({'Molecule level': x}, ),
                              'Brand level': lambda x: self.columns_dict.update({'Brand level': x}, )}

    def reset_columns(self):
        self.columns_dict = {'Country level': None,
                             'Family level': None,
                             'Molecule level': None,
                             'Brand level': None,
                             'Sales volume': [],
                             'Sales value': []}

    def check_data_validity(self, df: pd.DataFrame, values=False):
        if values == False:
            self.pipline_index = 0
        output = self.pipline[self.pipline_index](df, values)
        self.pipline_index += 1
        return output

    def pipline_step_back(self):
        self.pipline_index -= 1

    def prepare_data(self, df: pd.DataFrame):
        """Preprocess data for visualization"""
        return df

    def cat_num_columns(self, df, values=None):
        categorical = []
        numerical = []
        for column in df.columns:
            if is_numeric_dtype(df[column]):
                numerical.append(dbc.Row(
                    [
                        dbc.Label(column, html_for={'type': 'column_match', 'value': column}, width=3),
                        dbc.Col(
                            dbc.Select(
                                id={'type': 'column_match', 'value': column},
                                options=self.num_options,
                                required='required',
                            ),
                            width=9,
                        ),
                    ],
                    className="mb-3",
                ))
            else:
                categorical.append(dbc.Row(
                    [
                        dbc.Label(column, html_for={'type': 'column_match', 'value': column}, width=3),
                        dbc.Col(
                            dbc.Select(
                                id={'type': 'column_match', 'value': column},
                                options=self.cat_options,
                                required='required'
                            ),
                            width=9,
                        ),
                    ],
                    className="mb-3",
                ))

        form = dcc.Loading(dbc.Container(id='data_form', children=[dbc.Form(children=[html.H5('Select categorical '
                                                                                              'columns type '
                                                                                              ':'),
                                                                                      html.Hr()] + categorical +
                                                                                     [html.H5('Select sales type (in '
                                                                                              'value/volume) '
                                                                                              ':'), html.Hr()] +
                                                                                     numerical + [dbc.Row(
            dbc.Button("Next", outline=True, color="dark", className="mr-auto", n_clicks=0, id='next_step'),
            className="d-grid gap-2 col-3 mx-auto")])]))

        if len(categorical) == 0:
            return 'raise_error', dbc.Alert('No categorical columns was found in the data. Please check your input '
                                            'file !', color="danger"),
        if len(numerical) == 0:
            return 'raise_error', dbc.Alert('No Sales columns was found in the data. Please check your input '
                                            'file !', color="danger")

        return 'ask_user', form

    def rank_class_sales(self, df, values):
        columns = [value['value'] for value in values]
        column_counter = Counter(columns)
        if column_counter['Country level'] > 1:
            return 'raise_error', 'You can not select more than one Country level!', 'Input error', True
        if column_counter['Family level'] > 1:
            return 'raise_error', 'You can not select more than one Family level!', 'Input error', True
        if column_counter['Brand level'] > 1:
            return 'raise_error', 'You can not select more than one Brand level!', 'Input error', True
        if column_counter['Molecule level'] > 1:
            return 'raise_error', 'You can not select more than one Molecule level!', 'Input error', True
        if column_counter['Molecule level'] + column_counter['Country level'] + column_counter['Brand level'] + \
                column_counter['Molecule level'] == 0:
            return 'raise_error', 'You can not Discard all categorical columns!', 'Input error', True
        if column_counter['Sales volume'] + column_counter['Sales value'] == 0:
            return 'raise_error', 'You can not Discard all sales columns!', 'Input error', True
        for value in values:
            if value['value'] == 'Discard column':
                continue
            self.match_columns[value['value']](value['id']['value'])
        self.columns_dict['Sales value'].sort()
        self.columns_dict['Sales volume'].sort()
        value_dropdowns = []
        for idx, column in enumerate(self.columns_dict['Sales value']):
            value_dropdowns.append(dbc.Row(
                [
                    dbc.Label(column, html_for={'type': 'column_match', 'value': column}, width=3),
                    dbc.Col(
                        dbc.Select(
                            id={'type': 'column_match', 'value': column},
                            options=[{"label": i, "value": i} for i in range(len(self.columns_dict['Sales value']))],
                            required='required',
                            value=idx
                        ),
                        width=9,
                    ),
                ],
                className="mb-3",
            ))
        volume_dropdowns = []
        for idx, column in enumerate(self.columns_dict['Sales volume']):
            volume_dropdowns.append(dbc.Row(
                [
                    dbc.Label(column, html_for={'type': 'column_match', 'value': column}, width=3),
                    dbc.Col(
                        dbc.Select(
                            id={'type': 'column_match', 'value': column},
                            options=[{"label": i, "value": i} for i in range(len(self.columns_dict['Sales volume']))],
                            required='required',
                            value=idx
                        ),
                        width=9,
                    ),
                ],
                className="mb-3",
            ))
        value_dropdowns = [html.H5('Sales value Timeline: year 0-year n'), html.Hr()] + value_dropdowns if len(
            value_dropdowns) != 0 else value_dropdowns
        volume_dropdowns = [html.H5('Sales volume'
                                    ' Timeline: year 0-year n'), html.Hr()] + volume_dropdowns if len(
            volume_dropdowns) != 0 else volume_dropdowns

        form = dbc.Form(children=value_dropdowns + volume_dropdowns + [dbc.Row(
            dbc.Button("Next", outline=True, color="dark", className="mr-auto", n_clicks=0, id='next_step', ),
            className="d-grid gap-2 col-3 mx-auto")])
        return 'ask_user', form

    def build_dataframe(self, df, values):
        s_value_columns = []
        s_volume_columns = []
        for value in values:
            if value['id']['value'] in self.columns_dict['Sales value']:
                s_value_columns.append((int(value['value']), value['id']['value']))
            if value['id']['value'] in self.columns_dict['Sales volume']:
                s_volume_columns.append((int(value['value']), value['id']['value']))
        if (len(set([value[0] for value in s_value_columns])) != len(s_value_columns)) or (
                len(set([value[0] for value in s_volume_columns])) != len(s_volume_columns)):
            return 'raise_error', 'Sales columns can not have the same rank!', 'Input error', True

        s_value_columns.sort(key=lambda x: x[0])
        s_volume_columns.sort(key=lambda x: x[0])
        self.columns_dict['Sales value'] = [column[1] for column in s_value_columns]
        self.columns_dict['Sales volume'] = [column[1] for column in s_volume_columns]

        self.clean_data = df[self.get_columns()]
        self.current_layout = None
        self.clean_data.attrs['columns_dict'] = self.columns_dict
        layout = [dbc.Row(dbc.Alert(html.H4('Your data is ready !'), color="success")), dbc.Row(
            dbc.Button("Next", outline=True, color="dark", className="mr-auto", href='/dashboard', id='next_step',
                       n_clicks=0), className="d-grid gap-2 col-3 mx-auto")]
        return 'ask_user', layout

    def get_columns(self):

        columns = []
        for column in ['Country level', 'Family level', 'Molecule level', 'Brand level']:
            if self.columns_dict[column] is not None:
                columns.append(self.columns_dict[column])
        columns += self.columns_dict['Sales volume'] + self.columns_dict['Sales value']
        return columns

    def empty_func(self, df, values):
        return 'ask_user', no_update

    def build_dashboard(self):
        Tabs = []
        self.tabs_dict = dict()
        for level in ['Country level', 'Family level', 'Molecule level', 'Brand level']:
            if self.clean_data.attrs['columns_dict'][level] is not None:
                Tabs.append(dbc.Tab(label=level, tab_id=f"tab-{level.split()[0]}"))
                tab = f'test tab {level}'
                self.tabs_dict[f"tab-{level.split()[0]}"] = tab

        card = dbc.Card(
            [
                dbc.CardHeader(
                    dbc.Tabs(Tabs, id="card-tabs", active_tab=list(self.tabs_dict.keys())[0], )
                ),
                dbc.CardBody(id="card-content"),
            ]
        )

        dashboard = dbc.Container([dbc.Row(html.Div(children='''<template_unique_name>''')),
                                   dbc.Row(card)])
        return dashboard

    def render_layout(self):
        if self.current_layout is None:
            self.current_layout = self.build_dashboard()
        return self.current_layout

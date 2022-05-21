import pandas as pd
from .template_interface import FormalTemplateInterface
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from pandas.api.types import is_numeric_dtype
from dash import no_update
from collections import Counter
from dash import Input, Output, html
import dash_daq as daq
import plotly.graph_objs as go
from erikusa.metrics import cagr, growth
from sklearn.preprocessing import StandardScaler


class ProductLaunch(FormalTemplateInterface):
    def __init__(self):
        self.name = 'Product launch'
        self.description = [html.H5('This Dashboard has 4 views (Box in black) and will help guide  decisions around '
                                    'the launch of molecule X.'),
                            html.Ul([html.Li('1st view gives an idea about the size of opportunity in the region and '
                                             'by country.'),
                                     html.Li('2nd view gives an idea about the performance of a given products’ '
                                             'family in a specific market.'),
                                     html.Li('3rd view puts the light on molecule X and its performance compared to '
                                             'other molecules mainly within the  same family in a specific country.'),
                                     html.Li('4th view is for the forecast and future performance of the client in a '
                                             'specific country.'),
                                     html.Li('Besides the visualization part, Erikusa’s solution provides a set of '
                                             'insights, social media sensors (optional)  and a scoring system for an '
                                             'efficient data driven decision making.')])]
        self.imgPreview = 'test_preview.webp'
        self.tags = ['Scoring', 'Performance']
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
        self.get_tab = {
            'Country level': lambda x: x.get_country_tab(),
            'Family level': lambda x: x.get_family_tab(),
            'Molecule level': lambda x: x.get_molecule_tab(),
            'Brand level': lambda x: x.get_brand_tab(),
        }
        self.country_scores = None

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

                tab = dbc.Container(
                    children=self.get_tab[level](self)
                    , fluid=True)
                self.tabs_dict[f"tab-{level.split()[0]}"] = tab

        card = dbc.Card(
            [
                dbc.CardHeader(
                    dbc.Tabs(Tabs, id="card-tabs", active_tab=list(self.tabs_dict.keys())[0], )
                ),
                dbc.CardBody(id="card-content"),
            ]
        )

        dashboard = dbc.Container([dbc.Row(card)], className='mt-2', fluid=True)
        return dashboard

    def render_layout(self):
        if self.current_layout is None:
            self.current_layout = self.build_dashboard()
        return self.current_layout

    def get_country_tab(self):
        self.scoring_country_view()
        columns = []
        for level in ['Country level', 'Family level', 'Molecule level', 'Brand level']:
            if self.clean_data.attrs['columns_dict'][level] is not None:
                columns.append(level)
        countries = list(self.clean_data[self.clean_data.attrs['columns_dict']['Country level']].unique())
        max_input = len(countries)
        switch_vol_val = 'Sales value' if len(self.clean_data.attrs['columns_dict']['Sales value']) else 'Sales volume'
        S_columns = self.clean_data.attrs['columns_dict'][switch_vol_val]

        switch = daq.ToggleSwitch(id={'index': 'sales_toggle', 'type': 'Country level'},
                                  value=False if len(
                                      self.clean_data.attrs['columns_dict']['Sales value']) else True,
                                  disabled=True if not (
                                      len(self.clean_data.attrs['columns_dict']['Sales value'])) or not (
                                      len(self.clean_data.attrs['columns_dict']['Sales volume'])) else False)
        dropdown_country = dbc.DropdownMenu(

            label='Country',
            menu_variant="dark",
            children=[
                dbc.DropdownMenuItem(dbc.Button([html.I(className="bi bi-check2-square"),'(Select All)'], id='select_all_country', style={'width':'100%'}),toggle=False,),
                dbc.DropdownMenuItem(dbc.Button([html.I(className="bi bi-funnel"),'(Clear All)'], id='clear_all_country', style={'width':'100%'}),toggle=False,),
                dbc.DropdownMenuItem(divider=True,toggle=False,),

                dbc.Checklist(
                    options=[{"label": country, "value": country} for country in countries],
                    value=countries,
                    id="country_checklist",
                    class_name='p-1 "bi bi-file-earmark-arrow-down"'
                )
            ], class_name='m-0 p-0')
        dropdown_range = dbc.DropdownMenu(
            label='Timeline',
            menu_variant="dark",
            children=[
                dbc.Checklist(
                    options=[{"label": column, "value": index} for index, column in enumerate(S_columns)],
                    value=list(range(len(S_columns))),
                    id="range_checklist",
                    class_name='p-1 "bi bi-file-earmark-arrow-down"'
                )
            ], class_name='m-0 p-0')

        tab_filters = dbc.Row(
            [
                dbc.Col(html.H6('Value'), className="mr-auto", width='auto'),
                dbc.Col(switch, className="mr-auto", width='auto'),
                dbc.Col(html.H6('Volume'), className="mr-auto", width='auto'),
                dbc.Col(html.P("Select top: ", className='m-0 p-0 mr-1'), width='auto'),
                dbc.Col(dbc.Input(type="number",
                                  min=0, max=max_input, size='sm',
                                  id={'index': 'top', 'level': 'country'},
                                  value=5 if max_input > 5 else max_input, step=1), width='auto'),

                dbc.Col(dbc.Label('Sales per:', html_for='per', width='auto')),
                dbc.Col(
                    dbc.Select(id='per', options=[{"label": i, "value": i} for i in columns], required='required',
                               value=columns[0], ),
                    width='auto'),

                dbc.Col(dropdown_country, className="mr-auto", width='auto'),
                dbc.Col(dropdown_range, className="mr-auto", width='auto'),
            ], align="center", justify='end', className='mb-2')

        header_cards_2 = dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader([dbc.Row(html.H5(id='RS_country_header'))]),

                        dbc.CardBody(
                            [
                                html.H5(id='RS_country', children="<-- the value generated by the call back-->",
                                        className="card-title"),
                            ]
                        ),
                    ], color="primary", outline=True), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader([dbc.Row(html.H5(id='RG_country_header')),]),
                        dbc.CardBody(
                            [
                                html.H5(id='RG_country', children="<-- the value generated by the call back-->",
                                        className="card-title"),
                            ]
                        ),
                    ], color="primary", outline=True), className='mb-2'), ]),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='line_country_header', children='<Sales>', className='p-0 m-0'),
                                    width='auto'), align='center', justify='center')),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='line_country')), align='center', justify='center'),

                            ], className='p-0'
                        ),
                    ], color="primary", outline=True), className='mb-2'), )
                ,dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bubble_country_header', children='<Sales>', className='p-0 m-0'),
                                    width='auto'), align='center', justify='center')),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='bubble_country')), align='center', justify='center'),

                            ], className='p-0'
                        ),
                    ], color="primary", outline=True), className='mb-2'), )
            ], width=6),

            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='MS_country_header', children='<Market Size>', className='p-0 m-0'),
                                    width='auto'), align='center', justify='center')),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(
                                    html.H5(id='MS_country', children="<-- the value generated by the call back-->",
                                            className='p-0 m-0'), width='auto'), align='center', justify='center')
                            ]
                        ),
                    ], color="primary", outline=True), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(
                            dbc.Row(dbc.Col(html.H5(id='cagr_country_header', className='p-0 m-0'), width='auto'),
                                    align='center', justify='center')),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    dbc.Col(html.H5(id='cagr_country',
                                                    children="<-- the value generated by the call back-->",
                                                    className='p-0 m-0'), width='auto'), align='center',
                                    justify='center')
                            ]
                        ),
                    ], color="primary", outline=True), className='mb-2')], ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='pie_country_header', children='<Market Share>', className='p-0 m-0'),
                                    width='auto'), align='center', justify='center')),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='pie_country')), align='center', justify='center'),

                            ],
                        ),
                    ], color="primary", outline=True), className='mb-2'), ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bar_country_header', children='<Sales>', className='p-0 m-0'),
                                    width='auto'), align='center', justify='center')),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='bar_country')), align='center', justify='center'),

                            ],
                        ),
                    ], color="primary", outline=True), className='mb-2'), ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(children='Country Scoring', className='p-0 m-0'),
                                    width='auto'), align='center', justify='center')),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(id='scoring_country'), align='center', justify='center'),

                            ],
                        ),
                    ], color="primary", outline=True), className='mb-2')


                )
            ], width=6)])
        return [tab_filters, header_cards_2]

    def get_family_tab(self):

        return []

    def get_molecule_tab(self):
        return []

    def get_brand_tab(self):
        return []

    def scoring_country_view(self):
        c_column = self.clean_data.attrs['columns_dict']['Country level']
        df = self.clean_data
        vol_columns = self.clean_data.attrs['columns_dict']['Sales volume']
        val_columns = self.clean_data.attrs['columns_dict']['Sales value']
        df = df[vol_columns+val_columns+[c_column]]
        df = df.groupby(by=[c_column]).sum().reset_index(level=[c_column])
        scoring_columns = []
        if len(vol_columns):
            df['Market size volume'] = df[vol_columns].sum(1)
            scoring_columns.append('Market size volume')
            df['Market share volume'] = df['Market size volume']/df['Market size volume'].sum()
            scoring_columns.append('Market share volume')
            if len(vol_columns) > 1:
                df['Growth in Volume'] = growth(data=df, begin=vol_columns[0], final=vol_columns[-1]).values
                scoring_columns.append('Growth in Volume')
            if len(vol_columns)>2:
                df['CAGR in volume'] = cagr(data=df, begin=vol_columns[0], final=vol_columns[-1],t = len(vol_columns)-1).values
                scoring_columns.append('CAGR in volume')
        if len(val_columns):
            df['Market size value']=df[val_columns].sum(1)
            scoring_columns.append('Market size value')
            df['Market share value'] = df['Market size value'] / df['Market size value'].sum()
            scoring_columns.append('Market share value')
            if len(val_columns) > 1:
                df['Growth in value'] = growth(data=df, begin=val_columns[0], final=val_columns[-1]).values
                scoring_columns.append('Growth in value')
            if len(val_columns)>2:
                df['CAGR in value'] = cagr(data=df, begin=val_columns[0], final=val_columns[-1],
                                      t=len(val_columns) - 1).values
                scoring_columns.append('CAGR in value')
        df['Score'] =StandardScaler().fit_transform(df[scoring_columns]).sum(axis=1)
        df.sort_values('Score', ascending=False, inplace=True)
        self.country_scores = df[[c_column]+scoring_columns+['Score']]

        self.country_scores.attrs['columns'] = {'Country level':c_column,
                                                'Score Column':scoring_columns}



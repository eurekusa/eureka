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
        self.description = [html.H5('This dashboard helps guide decision-making about where to launch and what molecule or product to launch in a specific therapeutic area.  It has 4 views:'),
                            html.Ul([html.Li('1st view gives an idea about the size of opportunity in the region and '
                                             'by country.'),
                                     html.Li('2nd view gives an idea about the performance of the therapeutic '
                                             'families in a specific market.'),
                                     html.Li('3rd view highlights the performance of a specific molecule compared to '
                                             'other molecules  within the same family and in the selected markets.'),
                                     html.Li('4th view is for the forecast and future performance of the chosen '
                                             'molecule in a specific market(s).'),])
                            ,html.H5('Besides the visualization part, this solution provides a set of AI generated '
                                     'insights, social media sensors (optional) and a scoring system to help seize '
                                     'the best opportunities for a successful and strategic product launch.')
                            ]





        self.imgPreview = 'test_preview.jpg'
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
                                className='selectpicker'
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
                                required='required',
                                className='selectpicker'
                            ),
                            width=9,
                        ),
                    ],
                    className="mb-3",
                ))

        form = dcc.Loading(dbc.Container(id='data_form', children=[dbc.Form(children=[html.H5('Select categorical '
                                                                                              'columns type '
                                                                                              ':',
                                                                                              className='file-text'),
                                                                                      html.Hr(
                                                                                          className='form-hr')] + categorical +
                                                                                     [html.H5('Select sales type (in '
                                                                                              'value/volume) '
                                                                                              ':',
                                                                                              className='file-text'),
                                                                                      html.Hr(className='form-hr')] +
                                                                                     numerical + [dbc.Row(
            dbc.Button("Next", className="mr-auto outlined", n_clicks=0, id='next_step'),
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
                            value=idx,
                            className='selectpicker'
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
                            value=idx,
                            className='selectpicker'
                        ),
                        width=9,
                    ),
                ],
                className="mb-3",
            ))
        value_dropdowns = [html.H5('Sales value Timeline: year 0-year n', className='file-text'),
                           html.Hr(className='form-hr')] + value_dropdowns if len(
            value_dropdowns) != 0 else value_dropdowns
        volume_dropdowns = [html.H5('Sales volume'
                                    ' Timeline: year 0-year n', className='file-text'),
                            html.Hr(className='form-hr')] + volume_dropdowns if len(
            volume_dropdowns) != 0 else volume_dropdowns

        form = dbc.Form(children=value_dropdowns + volume_dropdowns + [dbc.Row(
            dbc.Button("Next", className="mr-auto outlined", n_clicks=0, id='next_step', ),
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
            dbc.Button("Next", className="mr-auto outlined", href='/dashboard', id='next_step',
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
        tabs_content = []
        for level in ['Country level', 'Family level', 'Molecule level', 'Brand level']:
            if self.clean_data.attrs['columns_dict'][level] is not None:
                tabs_content.append(dbc.Tab(
                    dbc.Container(children=self.get_tab[level](self), fluid=True, className='product-launch-container',
                                  style={'background-color': 'rgb(234,236,242)', })
                    , label=level, labelClassName="p-0' tab_text", tabClassName='p-0 tab_btn', className='p-0'))

        tabs = dbc.Tabs(
            tabs_content,
            className='p-0'
        )
        dashboard = dbc.Container(
            [dbc.Row(html.H3(self.name, className='ml-3 header_text product-launch-title'), className='g-0'),
             dbc.Row(tabs, className='g-0')], className='p-0  mt-2', fluid=True)
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
            toggleClassName='drowpdowns-filter',

            label='Country',
            menu_variant="light",
            children=[
                dbc.DropdownMenuItem(
                    dbc.Button([html.I(className="bi bi-check2-square"), '(Select All)'], id='select_all_country',
                               style={'width': '100%'}, className='outlined'), toggle=False, className='dropdown-item'),
                dbc.DropdownMenuItem(
                    dbc.Button([html.I(className="bi bi-funnel"), '(Clear All)'], id='clear_all_country',
                               style={'width': '100%'}, className='outlined'), toggle=False, className='dropdown-item'),
                dbc.DropdownMenuItem(divider=True, toggle=False, ),

                dbc.Checklist(
                    input_checked_class_name='checked_box',
                    options=[{"label": country, "value": country} for country in countries],
                    value=countries,
                    id="country_checklist",
                    class_name='p-1 dropdowlist'
                )
            ], class_name='m-0 p-0')
        dropdown_range = dbc.DropdownMenu(
            toggleClassName='drowpdowns-filter',
            label='Timeline',
            menu_variant="light",
            children=[
                dbc.Checklist(
                    input_checked_class_name='checked_box',
                    options=[{"label": column, "value": index} for index, column in enumerate(S_columns)],
                    value=list(range(len(S_columns))),
                    id={'index': 'range_checklist', 'level': 'Country level'},
                    class_name='p-1 dropdowlist'
                )
            ], class_name='m-0 p-0')

        tab_filters = dbc.Row(dbc.Col(
            [

                dbc.Row([dbc.Col(html.P('Filters', className='m-0 import_text'), style={'text-align': 'center'},
                                 width='auto')], justify='center', align='center', className='pb-3'),
                dbc.Row(dbc.Col(dropdown_country, width=8), justify='center', align='center', className='mb-2'),
                dbc.Row(dbc.Col(dropdown_range, width=8), justify='center', align='center', className='mb-2'),
                dbc.Row([dbc.Col(html.H6('Value'), className="mr-auto", width='auto'),
                         dbc.Col(switch, className="mr-auto", width='auto'),
                         dbc.Col(html.H6('Volume'), className="mr-auto", width='auto'), ], justify='center',
                        align='center', className='mb-2'),
                dbc.Row([
                    dbc.Col(dbc.Label("Select top :", html_for={'index': 'top', 'level': 'country'}, width='auto'),
                            width='auto'),
                    dbc.Col(dbc.Input(type="number",
                                      min=0, max=max_input,
                                      id={'index': 'top', 'level': 'country'},
                                      value=5 if max_input > 5 else max_input, step=1, className='selectpicker'),
                            width='auto'), ], justify="between", align='center', className='mb-2'),
                dbc.Row([
                    dbc.Col(dbc.Label('Sales per :', html_for='per', width='auto')),
                    dbc.Col(
                        dbc.Select(id='per', options=[{"label": i, "value": i} for i in columns], required='required',
                                   value=columns[0], className='selectpicker'),
                        width='auto')], justify="between", align='center'),

            ]), align="center", justify='end', className='mb-2')

        header_cards_2 = dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='MS_country_header', children='<Market Size>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(
                                    html.H5(id='MS_country', children="<-- the value generated by the call back-->",
                                            className='p-0 m-0 card-value'), width='auto'), align='center',
                                    justify='center')
                            ],
                        ),
                    ], className='product-launch-card'), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(
                            dbc.Row(dbc.Col(html.H5(id='cagr_country_header', className='p-0 m-0 card-header-text'),
                                            width='auto'),
                                    align='center', justify='center'), className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    dbc.Col(id='cagr_country', width='auto'), align='center',
                                    justify='center')
                            ],
                        ),
                    ], className='product-launch-card'), className='mb-2')], ),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(
                            [dbc.Row(html.H5(id='RS_country_header', className='card-header-text'), justify='center')],
                            className='product-launch-card-header'),

                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(id='RS_country', children="<-- the value generated by the call back-->",
                                                className="card-title"), justify='center', align='center'),
                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader([dbc.Row(html.H5(id='RG_country_header', className='card-header-text'),
                                                justify='center'), ], className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(id='RG_country', children="<-- the value generated by the call back-->",
                                                className="card-title"), justify='center', align='center'),
                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), ]),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='line_country_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='line_country')), align='center', justify='center'),

                            ], className='p-0 product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), )
                , dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bubble_country_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='bubble_country')), align='center', justify='center'),

                            ], className='p-0 product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), )
            ], width=6),

            dbc.Col([
                 dbc.Row(
                   dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(children='Global market summary', className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(id='summary_country'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col')),

                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='pie_country_header', children='<Market Share>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dcc.Graph(id='pie_country'), align='center', justify='center'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col'), ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bar_country_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dcc.Graph(id='bar_country'), align='center', justify='center'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col'), ),
                #dbc.Row(
                #   dbc.Col(dbc.Card([
                #        dbc.CardHeader(dbc.Row(
                #            dbc.Col(html.H5(children='Country Scoring', className='p-0 m-0 card-header-text'),
                #                    width='auto'), align='center', justify='center'),
                #            className='product-launch-card-header'),
                #        dbc.CardBody(
                #            [
                #                dbc.Row(id='scoring_country'),
                #
                #            ], className='product-launch-card-body'
                #        ),
                #    ], className='product-launch-card'), className='mb-2 right-col'))
            ], width=6)])
        return [dbc.Row(
            [dbc.Col(html.Div(tab_filters, className='side_bar'), className='side_col'), dbc.Col(header_cards_2)],
            className="g-0")]

    def get_family_tab(self):
        columns = []
        for level in ['Family level', 'Molecule level', 'Brand level']:
            if self.clean_data.attrs['columns_dict'][level] is not None:
                columns.append(level)

        # definig filters

        families = list(self.clean_data[self.clean_data.attrs['columns_dict']['Family level']].unique())
        max_input = len(families)
        switch_vol_val = 'Sales value' if len(self.clean_data.attrs['columns_dict']['Sales value']) else 'Sales volume'
        S_columns = self.clean_data.attrs['columns_dict'][switch_vol_val]

        country_filter = None
        if self.clean_data.attrs['columns_dict']['Country level'] is not None:
            top_num = self.country_scores[self.clean_data.attrs['columns_dict']['Country level']].unique().shape[0]
            top_num = 5 if top_num > 5 else top_num
            top_countries = list(self.country_scores[self.clean_data.attrs['columns_dict']['Country level']][
                                 :top_num])
            self.scoring_family_view(top_countries)
            country_filter = dbc.Row([
                dbc.Col(
                    dbc.Label('Country :', html_for={'type': 'family_checklist', 'level': 'country'}, width='auto')),
                dbc.Col(
                    dbc.Select(id={'type': 'family_checklist', 'level': 'country'},
                               options=[{"label": i, "value": i} for i in top_countries], required='required',
                               value=top_countries[0], className='selectpicker'),
                    width=8)], justify="between", align='center', className='mb-2')
            families = list(self.clean_data[self.clean_data[self.clean_data.attrs['columns_dict']['Country level']] ==
                                            top_countries[0]][
                                self.clean_data.attrs['columns_dict']['Family level']].unique())
            max_input = len(families)
        else:
            self.scoring_family_view()
            country_filter = dbc.Row([
                dbc.Col(
                    dbc.Label('Country :', html_for={'type': 'family_checklist', 'level': 'country'}, width='auto')),
                dbc.Col(
                    dbc.Select(id={'type': 'family_checklist', 'level': 'country'}, required='required',
                               value=None, className='selectpicker', disabled=True),
                    width='auto')], justify="between", align='center', className='mb-2')

        switch = daq.ToggleSwitch(id={'index': 'sales_toggle', 'level': 'Family level'},
                                  value=False if len(
                                      self.clean_data.attrs['columns_dict']['Sales value']) else True,
                                  disabled=True if not (
                                      len(self.clean_data.attrs['columns_dict']['Sales value'])) or not (
                                      len(self.clean_data.attrs['columns_dict']['Sales volume'])) else False)
        dropdown_family = dbc.DropdownMenu(
            toggleClassName='drowpdowns-filter',
            label='Family',
            menu_variant="light",
            children=[
                dbc.DropdownMenuItem(
                    dbc.Button([html.I(className="bi bi-check2-square"), '(Select All)'], id='select_all_family',
                               style={'width': '100%'}, className='outlined'), toggle=False, className='dropdown-item'),
                dbc.DropdownMenuItem(
                    dbc.Button([html.I(className="bi bi-funnel"), '(Clear All)'], id='clear_all_family',
                               style={'width': '100%'}, className='outlined'), toggle=False, className='dropdown-item'),
                dbc.DropdownMenuItem(divider=True, toggle=False, ),

                dbc.Checklist(
                    input_checked_class_name='checked_box',
                    options=[{"label": family, "value": family} for family in families],
                    value=families,
                    id={'type': 'family_checklist', 'level': 'family'},
                    class_name='p-1 dropdowlist'
                )
            ], class_name='m-0 p-0')

        dropdown_range = dbc.DropdownMenu(
            toggleClassName='drowpdowns-filter',
            label='Timeline',
            menu_variant="light",
            children=[
                dbc.Checklist(
                    input_checked_class_name='checked_box',
                    options=[{"label": column, "value": index} for index, column in enumerate(S_columns)],
                    value=list(range(len(S_columns))),
                    id={'index': 'range_checklist', 'level': 'Family level'},
                    class_name='p-1 dropdowlist'
                )
            ], class_name='m-0 p-0')

        filters_components = [

            dbc.Row([dbc.Col(html.P('Filters', className='m-0 import_text'), style={'text-align': 'center'},
                             width='auto')], justify='center', align='center', className='pb-3'),
            dbc.Row(dbc.Col(dropdown_family, width=8), justify='center', align='center', className='mb-2'),
            dbc.Row(dbc.Col(dropdown_range, width=8), justify='center', align='center', className='mb-2'),
            dbc.Row([dbc.Col(html.H6('Value'), className="mr-auto", width='auto'),
                     dbc.Col(switch, className="mr-auto", width='auto'),
                     dbc.Col(html.H6('Volume'), className="mr-auto", width='auto'), ], justify='center',
                    align='center', className='mb-2'),
            country_filter,
            dbc.Row([
                dbc.Col(dbc.Label("Select top :", html_for={'index': 'top', 'level': 'country'}, width='auto'),
                        width='auto'),
                dbc.Col(dbc.Input(type="number",
                                  min=0, max=max_input,
                                  id={'index': 'top', 'level': 'family'},
                                  value=5 if max_input > 5 else max_input, step=1, className='selectpicker'),
                        width='auto'), ], justify="between", align='center', className='mb-2'),

        ]

        tab_filters = dbc.Row(dbc.Col(filters_components), align="center", justify='end', className='mb-2')

        header_cards_2 = dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='MS_family_header', children='<Market Size>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(
                                    html.H5(id='MS_family', children="<-- the value generated by the call back-->",
                                            className='p-0 m-0 card-value'), width='auto'), align='center',
                                    justify='center')
                            ],
                        ),
                    ], className='product-launch-card'), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(
                            dbc.Row(dbc.Col(html.H5(id='cagr_family_header', className='p-0 m-0 card-header-text'),
                                            width='auto'),
                                    align='center', justify='center'), className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    dbc.Col(id='cagr_family', width='auto'), align='center',
                                    justify='center')
                            ],
                        ),
                    ], className='product-launch-card'), className='mb-2')], ),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(
                            [dbc.Row(html.H5(id='RS_family_header', className='card-header-text'), justify='center')],
                            className='product-launch-card-header'),

                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(id='RS_family', children="<-- the value generated by the call back-->",
                                                className="card-title"), justify='center', align='center'),
                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader([dbc.Row(html.H5(id='RG_family_header', className='card-header-text'),
                                                justify='center'), ], className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(id='RG_family', children="<-- the value generated by the call back-->",
                                                className="card-title"), justify='center', align='center'),
                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), ]),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='line_family_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='line_family')), align='center', justify='center'),

                            ], className='p-0 product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), )
                , dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bubble_family_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='bubble_family')), align='center', justify='center'),

                            ], className='p-0 product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), )
            ], width=6),

            dbc.Col([

                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='pie_family_header', children='<Market Share>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dcc.Graph(id='pie_family'), align='center', justify='center'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col'), ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bar_family_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dcc.Graph(id='bar_family'), align='center', justify='center'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col'), ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(children='Family Scoring', className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(id='scoring_family'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col')

                )
            ], width=6)])
        return [dbc.Row(
            [dbc.Col(html.Div(tab_filters, className='side_bar'), className='side_col'), dbc.Col(header_cards_2)],
            className="g-0")]

    def get_molecule_tab(self):


        columns = []
        for level in ['Family level', 'Molecule level', 'Brand level']:
            if self.clean_data.attrs['columns_dict'][level] is not None:
                columns.append(level)

        # definig filtershgre
        #switch
        switch_vol_val = 'Sales value' if len(self.clean_data.attrs['columns_dict']['Sales value']) else 'Sales volume'
        switch = daq.ToggleSwitch(id={'index': 'sales_toggle', 'level': 'Molecule level'},
                                  value=False if switch_vol_val == 'Sales value' else True,
                                  disabled=True if not (
                                      len(self.clean_data.attrs['columns_dict']['Sales value'])) or not (
                                      len(self.clean_data.attrs['columns_dict']['Sales volume'])) else False)

        switch_row = dbc.Row([dbc.Col(html.H6('Value'), className="mr-auto", width='auto'),
                     dbc.Col(switch, className="mr-auto", width='auto'),
                     dbc.Col(html.H6('Volume'), className="mr-auto", width='auto'), ], justify='center',
                    align='center', className='mb-2')
        # time line
        S_columns = self.clean_data.attrs['columns_dict'][switch_vol_val]

        dropdown_range = dbc.DropdownMenu(
            toggleClassName='drowpdowns-filter',
            label='Timeline',
            menu_variant="light",
            children=[
                dbc.Checklist(
                    input_checked_class_name='checked_box',
                    options=[{"label": column, "value": index} for index, column in enumerate(S_columns)],
                    value=list(range(len(S_columns))),
                    id={'index': 'range_checklist', 'level': 'Molecule level'},
                    class_name='p-1 dropdowlist'
                )
            ], class_name='m-0 p-0')

        dropdown_range_row = dbc.Row(dbc.Col(dropdown_range, width=8), justify='center', align='center', className='mb-2')
        df = self.clean_data
        country_row = None
        family_row = None
        c_column = self.clean_data.attrs['columns_dict']['Country level']
        f_column = self.clean_data.attrs['columns_dict']['Family level']
        family_score = self.family_scores
        if c_column is not None:
            top_num = self.country_scores[self.clean_data.attrs['columns_dict']['Country level']].unique().shape[0]
            top_num = 5 if top_num > 5 else top_num
            top_countries = list(self.country_scores[self.clean_data.attrs['columns_dict']['Country level']][
                                 :top_num])
            df = df[df[c_column] == top_countries[0]]
            family_score = family_score[family_score[c_column]==top_countries[0]]
            country_row = dbc.Row([
                dbc.Col(
                    dbc.Label('Country :', html_for={'type': 'molecule_checklist', 'level': 'country'}, width='auto')),
                dbc.Col(
                    dbc.Select(id={'type': 'molecule_checklist', 'level': 'country'},
                               options=[{"label": i, "value": i} for i in top_countries], required='required',
                               value=top_countries[0], className='selectpicker'),
                    width=8)], justify="between", align='center', className='mb-2')
        else:
            country_row = dbc.Row([
                dbc.Col(
                    dbc.Label('Country :', html_for={'type': 'molecule_checklist', 'level': 'country'}, width='auto')),
                dbc.Col(
                    dbc.Select(id={'type': 'molecule_checklist', 'level': 'country'}, required='required',
                               value=None, className='selectpicker', disabled=True),
                    width='auto')], justify="between", align='center', className='mb-2')

        if f_column is not None:
            top_num = family_score[f_column].unique().shape[0]

            top_num = 5 if top_num > 5 else top_num
            top_families = list(family_score[f_column][:top_num])
            df = df[df[f_column] == top_families[0]]
            family_row = dbc.Row([
                dbc.Col(
                    dbc.Label('Family :', html_for={'type': 'molecule_checklist', 'level': 'family'}, width='auto')),
                dbc.Col(
                    dbc.Select(id={'type': 'molecule_checklist', 'level': 'family'},
                               options=[{"label": i, "value": i} for i in top_families], required='required',
                               value=top_families[0], className='selectpicker'),
                    width=8)], justify="between", align='center', className='mb-2')
        else:
            family_row = dbc.Row([
                dbc.Col(
                    dbc.Label('Family :', html_for={'type': 'molecule_checklist', 'level': 'family'}, width='auto')),
                dbc.Col(
                    dbc.Select(id={'type': 'molecule_checklist', 'level': 'family'}, required='required',
                               value=None, className='selectpicker', disabled=True),
                    width='auto')], justify="between", align='center', className='mb-2')

        molecules = list(df[df.attrs['columns_dict']['Molecule level']].unique())
        max_input = len(molecules)
        dropdown_molecule = dbc.DropdownMenu(
            toggleClassName='drowpdowns-filter',
            label='Molecule',
            menu_variant="light",
            children=[
                dbc.DropdownMenuItem(
                    dbc.Button(children=[html.I(className="bi bi-check2-square"), '(Select All)'], id='select_all_molecule',
                               style={'width': '100%'}, className='outlined'), toggle=False, className='dropdown-item'),
                dbc.DropdownMenuItem(
                    dbc.Button([html.I(className="bi bi-funnel"), '(Clear All)'], id='clear_all_molecule',
                               style={'width': '100%'}, className='outlined'), toggle=False, className='dropdown-item'),
                dbc.DropdownMenuItem(divider=True, toggle=False, ),


                dbc.Checklist(
                    input_checked_class_name='checked_box',
                    options=[{"label": molecule, "value": molecule} for molecule in molecules],
                    value=molecules,
                    id={'type': 'molecule_checklist', 'level': 'molecule'},
                    class_name='p-1 dropdowlist'
                )
            ], class_name='m-0 p-0')

        dropdown_molecule_row= dbc.Row(dbc.Col(dropdown_molecule, width=8), justify='center', align='center', className='mb-2')



        filters_components = [

            dbc.Row([dbc.Col(html.P('Filters', className='m-0 import_text'), style={'text-align': 'center'},
                             width='auto')], justify='center', align='center', className='pb-3'),
            dropdown_molecule_row,
            dropdown_range_row,
            switch_row,
            country_row,
            family_row,
            dbc.Row([
                dbc.Col(dbc.Label("Select top :", html_for={'index': 'top', 'level': 'molecule'}, width='auto'),
                        width='auto'),
                dbc.Col(dbc.Input(type="number",
                                  min=0, max=max_input,
                                  id={'index': 'top', 'level': 'molecule'},
                                  value=5 if max_input > 5 else max_input, step=1, className='selectpicker'),
                        width='auto'), ], justify="between", align='center', className='mb-2'),

        ]

        tab_filters = dbc.Row(dbc.Col(filters_components), align="center", justify='end', className='mb-2')

        header_cards_2 = dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='MS_molecule_header', children='<Market Size>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(
                                    html.H5(id='MS_molecule', children="<-- the value generated by the call back-->",
                                            className='p-0 m-0 card-value'), width='auto'), align='center',
                                    justify='center')
                            ],
                        ),
                    ], className='product-launch-card'), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(
                            dbc.Row(dbc.Col(html.H5(id='cagr_molecule_header', className='p-0 m-0 card-header-text'),
                                            width='auto'),
                                    align='center', justify='center'), className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    dbc.Col(id='cagr_molecule', width='auto'), align='center',
                                    justify='center')
                            ],
                        ),
                    ], className='product-launch-card'), className='mb-2')], ),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(
                            [dbc.Row(html.H5(id='RS_molecule_header', className='card-header-text'), justify='center')],
                            className='product-launch-card-header'),

                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(id='RS_molecule', children="<-- the value generated by the call back-->",
                                                className="card-title"), justify='center', align='center'),
                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader([dbc.Row(html.H5(id='RG_molecule_header', className='card-header-text'),
                                                justify='center'), ], className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(id='RG_molecule', children="<-- the value generated by the call back-->",
                                                className="card-title"), justify='center', align='center'),
                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), ]),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='line_molecule_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='line_molecule')), align='center', justify='center'),

                            ], className='p-0 product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), )
                , dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bubble_molecule_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dbc.Col(dcc.Graph(id='bubble_molecule')), align='center', justify='center'),

                            ], className='p-0 product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2'), )
            ], width=6),

            dbc.Col([

                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='pie_molecule_header', children='<Market Share>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dcc.Graph(id='pie_molecule'), align='center', justify='center'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col'), ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(id='bar_molecule_header', children='<Sales>',
                                            className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(dcc.Graph(id='bar_molecule'), align='center', justify='center'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col'), ),
                dbc.Row(
                    dbc.Col(dbc.Card([
                        dbc.CardHeader(dbc.Row(
                            dbc.Col(html.H5(children='Family Scoring', className='p-0 m-0 card-header-text'),
                                    width='auto'), align='center', justify='center'),
                            className='product-launch-card-header'),
                        dbc.CardBody(
                            [
                                dbc.Row(id='scoring_molecule'),

                            ], className='product-launch-card-body'
                        ),
                    ], className='product-launch-card'), className='mb-2 right-col')

                )
            ], width=6)])
        return [dbc.Row(
            [dbc.Col(html.Div(tab_filters, className='side_bar'), className='side_col'), dbc.Col(header_cards_2)],
            className="g-0")]


    def get_brand_tab(self):
        return []

    def scoring_country_view(self):
        c_column = self.clean_data.attrs['columns_dict']['Country level']
        df = self.clean_data
        vol_columns = self.clean_data.attrs['columns_dict']['Sales volume']
        val_columns = self.clean_data.attrs['columns_dict']['Sales value']
        df = df[vol_columns + val_columns + [c_column]]
        df = df.groupby(by=[c_column]).sum().reset_index(level=[c_column])
        scoring_columns = []
        if len(vol_columns):
            df['Market size volume'] = df[vol_columns].sum(1)
            scoring_columns.append('Market size volume')
            df['Market share volume'] = df['Market size volume'] / df['Market size volume'].sum()
            scoring_columns.append('Market share volume')
            if len(vol_columns) > 1:
                df['Growth in volume'] = growth(data=df, begin=vol_columns[0], final=vol_columns[-1]).values
                scoring_columns.append('Growth in volume')
            if len(vol_columns) > 2:
                df['CAGR in volume'] = cagr(data=df, begin=vol_columns[0], final=vol_columns[-1],
                                            t=len(vol_columns) - 1).values
                scoring_columns.append('CAGR in volume')
        if len(val_columns):
            df['Market size value'] = df[val_columns].sum(1)
            scoring_columns.append('Market size value')
            df['Market share value'] = df['Market size value'] / df['Market size value'].sum()
            scoring_columns.append('Market share value')
            if len(val_columns) > 1:
                df['Growth in value'] = growth(data=df, begin=val_columns[0], final=val_columns[-1]).values
                scoring_columns.append('Growth in value')
            if len(val_columns) > 2:
                df['CAGR in value'] = cagr(data=df, begin=val_columns[0], final=val_columns[-1],
                                           t=len(val_columns) - 1).values
                scoring_columns.append('CAGR in value')
        df['Score'] = StandardScaler().fit_transform(df[scoring_columns]).sum(axis=1)
        df.sort_values('Score', ascending=False, inplace=True)
        self.country_scores = df[[c_column] + scoring_columns + ['Score']]

        self.country_scores.attrs['columns'] = {'Country level': c_column,
                                                'Score Column': scoring_columns}

    def scoring_family_view(self,countries=None):
        level_columns = [self.clean_data.attrs['columns_dict']['Family level']]
        if self.clean_data.attrs['columns_dict']['Country level'] is not None:
            level_columns = [self.clean_data.attrs['columns_dict']['Country level']] + level_columns

        df = self.clean_data
        if countries:
            df = df[df[df.attrs['columns_dict']['Country level']].isin(countries)]
        vol_columns = self.clean_data.attrs['columns_dict']['Sales volume']
        val_columns = self.clean_data.attrs['columns_dict']['Sales value']
        df = df[vol_columns + val_columns + level_columns]
        df = df.groupby(by=level_columns).sum()

        scoring_columns = []
        if len(vol_columns):
            df['Market size volume'] = df[vol_columns].sum(1)
            scoring_columns.append('Market size volume')
            df['Market share volume'] = df['Market size volume'].div(df['Market size volume'].groupby(level=0).sum(),
                                                                     level=0)

            scoring_columns.append('Market share volume')
            if len(vol_columns) > 1:
                df['Growth in volume'] = growth(data=df, begin=vol_columns[0], final=vol_columns[-1]).values
                scoring_columns.append('Growth in volume')
            if len(vol_columns) > 2:
                df['CAGR in volume'] = cagr(data=df, begin=vol_columns[0], final=vol_columns[-1],
                                            t=len(vol_columns) - 1).values
                scoring_columns.append('CAGR in volume')

        if len(val_columns):
            df['Market size value'] = df[val_columns].sum(1)
            scoring_columns.append('Market size value')
            df['Market share value'] = df['Market size value'].div(df['Market size value'].groupby(level=0).sum(),
                                                                     level=0)
            scoring_columns.append('Market share value')

            if len(val_columns) > 1:
                df['Growth in value'] = growth(data=df, begin=val_columns[0], final=val_columns[-1]).values
                scoring_columns.append('Growth in value')
            if len(val_columns) > 2:
                df['CAGR in value'] = cagr(data=df, begin=val_columns[0], final=val_columns[-1],
                                           t=len(val_columns) - 1).values
                scoring_columns.append('CAGR in value')
        df=df.reset_index(level=level_columns)
        df['Score'] = StandardScaler().fit_transform(df[scoring_columns]).sum(axis=1)
        df.sort_values('Score', ascending=False, inplace=True)
        self.family_scores = df[level_columns + scoring_columns + ['Score']]
        level=['Country','Family']

        self.family_scores.attrs['columns'] = {'levels': {level[-i]:level_columns[-i] for i in range(1,len(level_columns)+1)},
                                                'Score Column': scoring_columns}

    def scoring_molecule_view(self):
        return []

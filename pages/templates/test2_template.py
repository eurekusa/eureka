import pandas as pd
from .template_interface import FormalTemplateInterface
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px


class TestTemplate2(FormalTemplateInterface):
    def __init__(self):
        self.name = '<template_name>'
        self.description = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor ' \
                           'incididuntut labore et dolore magna aliqua. Aliquam id diam maecenas ultricies mi eget. ' \
                           'Mi bibendum neque egestas congue quisque egestas diam in arcu. Non curabitur gravida arcu ' \
                           'ac. '
        self.imgPreview = 'test2_preview.webp'
        self.tags = ['marketing', 'operation']
        self.pipline_index = 0
        self.pipline = []
        self.clean_data = None
        self.layout = None

    def check_data_validity(self, df: pd.DataFrame):
        """validate the input dataFrame"""
        return True

    def prepare_data(self, df: pd.DataFrame):
        """Preprocess data for visualization"""
        return df

    def build_dashboard(self, df: pd.DataFrame):
        df = pd.DataFrame({
            "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
            "Amount": [4, 1, 2, 2, 4, 5],
            "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
        })

        fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
        dashboard = dbc.Container([dbc.Row(html.Div(children='''<template_unique_name2>''')),
                                   dbc.Row(dcc.Graph(id='example-graph', figure=fig))])
        return dashboard

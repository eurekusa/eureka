import pandas as pd
from .template_interface import FormalTemplateInterface
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px


class <template_class_name>(FormalTemplateInterface):
    def __init__(self):
        #todo
        #template name"
        self.name = '<template_unique_name2>'
        #template descrition"
        self.description = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor ' \
                           'incididuntut labore et dolore magna aliqua. Aliquam id diam maecenas ultricies mi eget. ' \
                           'Mi bibendum neque egestas congue quisque egestas diam in arcu. Non curabitur gravida arcu ' \
                           'ac. '
        # Img file name , the img must be in the ./assets directory
        self.imgPreview = 'test2_preview.webp'
        #templates tags
        self.tags = ['<tag1>', '<tag2>']

        self.layout = None

    def check_data_validity(self, df: pd.DataFrame):
        """validate the input dataFrame"""
        #todo return True is the given dataframe respcets the template input format else False
        pass

    def prepare_data(self, df: pd.DataFrame):
        """Preprocess data for visualization"""
        #todo prepare data for the visualisation (e.g calculate metrics)
        pass

    def build_dashboard(self, df: pd.DataFrame):
        """"build the template layout"""
        #todo return the template layout
        pass

import pandas as pd
from template_interface import FormalTemplateInterface


class TestTemplate(FormalTemplateInterface):
    def __init__(self):
        self.name = 'test'
        self.description = 'bla bla'
        self.imgPreview = 'test_preview.webp'
        self.tags = None
        self.layout = None

    def check_data_validity(self, df: pd.DataFrame):
        """validate the input dataFrame"""
        pass

    def prepare_data(self, df: pd.DataFrame):
        """Preprocess data for visualization"""
        pass

    def build_dashboard(self, df: pd.DataFrame):
        """build dashboard graphs"""
        pass

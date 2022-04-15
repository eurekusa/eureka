import pandas as pd
from .templates import TestTemplate2, TestTemplate


class Facade(object):
    def __init__(self):
        self.current_template = None
        self.current_layout = None
        self.raw_data = None
        self.preprocessed_data = None
        self.templates_list = [TestTemplate(), TestTemplate2()]

    def get_template_by_name(self, name: str):
        for template in self.templates_list:
            if template.name == name:
                self.current_template = template
                return template

    def set_template(self, name: str):
        if self.current_template is not None:
            self.raw_data = None
            self.preprocessed_data = None
            self.current_layout = None
        self.current_template = self.get_template_by_name(name)

    def check_data_validity(self, df: pd.DataFrame):

        return self.current_template.check_data_validity(df)

    def load_data(self, df: pd.DataFrame):
        self.raw_data = df
        self.preprocessed_data = self.current_template.prepare_data(df)

    def render_layout(self):
        if self.current_layout is None:
            self.current_layout = self.current_template.build_dashboard(self.preprocessed_data)
        return self.current_layout

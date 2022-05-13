import pandas as pd
from .templates import TestTemplate2, TestTemplate


class Facade(object):
    def __init__(self):
        self.current_template = None
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

    def check_data_validity(self, values=None):
        return self.current_template.check_data_validity(self.raw_data, values)

    def pipline_step_back(self):
        self.current_template.pipline_step_back()

    def load_data(self, df: pd.DataFrame):
        self.raw_data = df
        self.current_template.reset_columns()
        self.current_template.pipline_index = 0

    def render_layout(self):
        return self.current_template.render_layout()

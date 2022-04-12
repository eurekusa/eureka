
class Facade(object):
    def __init__(self):
        self.current_template = None
        self.raw_data = None
        self.preprocessed_data = None
        self.templates_list = []

    def set_template(self, name):
        if self.current_template is not None:
            self.raw_data = None
            self.preprocessed_data = None
        for template in self.templates_list:
            if template.name == name:
                self.current_template = template
                break

    def check_data_validity(self, df):
        self.current_template.chech_data_validity(df)

    def load_data(self, df):
        self.raw_data = df
        self.preprocessed_data = self.current_template.prepare_data(df)

    def render_layout(self):
        self.current_template.build_dashboard()



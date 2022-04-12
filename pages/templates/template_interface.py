import abc
import pandas as pd


class FormalTemplateInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'check_data_validation') and
                callable(subclass.check_data_validation) and
                hasattr(subclass, 'prepare_data') and
                callable(subclass.prepare_data) and
                hasattr(subclass, 'build_dashboard') and
                callable(subclass.build_dashboard) or
                NotImplemented)

    @abc.abstractmethod
    def check_data_validation(self, df: pd.DataFrame):
        """validate the input dataFrame"""
        raise NotImplementedError

    @abc.abstractmethod
    def prepare_data(self, df: pd.DataFrame):
        """Preprocess data for visualization"""
        raise NotImplementedError

    @abc.abstractmethod
    def build_dashboard(self, df: pd.DataFrame):
        """build dashboard graphs"""
        raise NotImplementedError

"""
Defines helper function for metrics calculation.
"""
from pandas.api.types import is_numeric_dtype
import pandas as pd

def build_dataframe(args, numerical_columns=True):
    """
    Constructs a dataframe.
    The argument values in `args` can be either strings corresponding to
    existing columns of a dataframe, or data arrays (lists, numpy arrays,
    pandas columns, series).
    Parameters
    ----------
    args : OrderedDict
        arguments passed to the function.
    numerical_columns : bool, default True.
        Whether to check that dataframe values are numerical or not.
    Returns
    ----------
    dataframe : Pandas' DataFrame.
    """
    df_provided = args["data_frame"] is not None
    if df_provided and not isinstance(args["data_frame"], pd.DataFrame):
        args["data_frame"] = pd.DataFrame(args["data_frame"])
    df_input = args["data_frame"]
    if (isinstance(args['x'],str) and isinstance(args['y'],str)):
        if(not df_provided):
            raise ValueError(
                "Missing data parameter."
            )
        else:
            if(args['x'] in df_input.columns) and (args['y'] in df_input.columns):
                args['x']=df_input[args['x']].values
                args['y']=df_input[args['y']].values
            else:
                raise ValueError(
                    "Mentioned columns are not in the dataframe."
                )
    else:
        try:
            args['x']=list(iter(args['x']))
            args['y']=list(iter(args['y']))
        except:
            raise TypeError(
                "When data is not provided, iterable variable must be provided instead."
            )
    if numerical_columns:
        if (is_numeric_dtype(pd.Series(args['x'])) and is_numeric_dtype(pd.Series(args['y']))):
            return pd.DataFrame({args['x_col']:args['x'],args['y_col']:args['y']})
        else:
            raise TypeError(
                "Both columns must be of a numerical dtype."
            )
    else:
        return pd.DataFrame({args['x_col']:args['x'],args['y_col']:args['y']})

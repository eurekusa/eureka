from .formulas import _cagr, _growth, _evolution_index
from ._metrics_helper import build_dataframe
def cagr(
    data=None,
    begin=None,
    final=None,
    t=None,
    fill=None
    ):
    """
    Calculates the Compound Annual Growth Rate (CAGR).
    CAGR is a business and investing specific term for the geometric progression
    ratio that provides a constant rate of return over the time period.
    Parameters
    ----------
    data : Pandas' DataFrame.
        Sales in value/standard unit dataframe.
    begin : str (specifies the column name in the dataframe) or list-like object of floats/ints.
        Beginning values of investments.
    final : str (specifies the column name in the dataframe) or list-like object of floats/ints.
        Final values of investments.
    t : int
        Time in years.
    fill: scalar, dict, Series, or DataFrame.
        Value to use to fill holes (e.g. 0).
    Returns
    -------
    cagr : pandas' Serie.
        Compound Annual Growth Rate.

    Examples
    --------
    >>> from erikusa.metrics import cagr
    >>> df = pd.DataFrame({'2017 Sales': [20, 30, 27, 5],
    ...             '2021 Sales': [28, 15, 36, 57]})
    >>>cagr(data=df, begin='2017 Sales', final='2021 Sales',t=4)
    0    0.087757
    1   -0.159104
    2    0.074570
    3    0.837495
    dtype: float64
    """
    if not isinstance(t, int):
        raise ValueError(
            "The timeframe could must be a postive int."
        )
    args={
    'x':begin,
    'y':final,
    'x_col':'begin',
    'y_col':'final',
    'data_frame':data
    }
    input_data=build_dataframe(args)
    output_data=input_data.apply(lambda row: _cagr(begin=row['begin'],final=row['final'],t=t),axis=1)
    if fill is not None:
        output_data.fillna(value=fill,inplace=True)
    return output_data
def growth(
    data=None,
    begin=None,
    final=None,
    fill=None
    ):
    """
    Calculates the growth of sales.
    Sales growth is a metric that measures the ability of your sales team to
    increase revenue over a fixed period of time. Without revenue growth,
    businesses are at risk of being overtaken by competitors and stagnating.
    Sales growth is a strategic indicator that is used in decision making by
    executives and the board of directors, and influences the formulation and
    execution of business strategy.

    Parameters
    ----------
    data : Pandas' DataFrame.
        Sales in value/standard unit dataframe.
    begin : str (specifies the column name in the dataframe) or list-like object of floats/ints.
        Beginning values of investments.
    final : str (specifies the column name in the dataframe) or list-like object of floats/ints.
        Final values of investments.
    fill: scalar, dict, Series, or DataFrame.
        Value to use to fill holes (e.g. 0).

    Returns
    -------
    growth : pandas' Serie.
        Sales Growth.

    Examples
    --------
    >>> from erikusa.metrics import growth
    >>> df = pd.DataFrame({'2017 Sales': [20, 30, 27, 5],
    ...                    '2021 Sales': [28, 15, 36, 57]})
    >>>growth(data=df, begin='2017 Sales', final='2021 Sales')
    0     0.400000
    1    -0.500000
    2     0.333333
    3    10.400000
    dtype: float64
    """
    args={
    'x':begin,
    'y':final,
    'x_col':'begin',
    'y_col':'final',
    'data_frame':data
    }
    input_data=build_dataframe(args)
    output_data=input_data.apply(lambda row: _growth(begin=row['begin'],final=row['final']),axis=1)
    if fill is not None:
        output_data.fillna(value=fill,inplace=True)
    return output_data
def evolution_index(
    data=None,
    brand=None,
    market=None,
    percent=True,
    fill=None
    ):
    """
    Calcultes the evolution index (EI) of the products.
    The Evolution Index compares the growth of a product to that of the product
    competes in. It ranges between -100 and a positive value, and is used to
    compare the performance of competing products.
    This KPI offers a strategic approach and accuracy of the market competition,
    allowing the company to take flexible decisions and maximize profitability.
    Analyzing the evolution index over time in combination with the current sales
    gives a clear picture how the company products are competing on the market
    against the total market sales.

    Parameters
    ----------
    data : Pandas' DataFrame.
        Sales in value/standard unit growth dataframe.
    brand : str (specifies the column name in the dataframe) or list-like object of floats/ints.
        The growth of the owned products.
    market : str (specifies the column name in the dataframe) or list-like object of floats/ints.
        The growth of the whole corresponding markets.
    percent : bool, default True.
        Specifies whether the given growth rate in percent or not.
    fill: scalar, dict, Series, or DataFrame.
        Value to use to fill holes (e.g. 0).

    Returns
    -------
    evolution index : pandas' Serie.

    Examples
    --------
    >>> from erikusa.metrics import evolution_index
    >>> df = pd.DataFrame({'brand growth': [0.4, -0.5,0.33, 10.4],
    ...                    'market growth': [0.2, 0.3, 0.7, 7]})
    >>>evolution_index(data=df, brand='brand growth', market='market growth', percent=False)
    0    1.166667
    1    0.384615
    2    0.782353
    3    1.425000
    dtype: float64
    """
    args={
    'x':brand,
    'y':market,
    'x_col':'brand',
    'y_col':'market',
    'data_frame':data
    }
    input_data=build_dataframe(args)
    output_data=input_data.apply(lambda row: _evolution_index(brand=row['brand'],market=row['market'],percent=percent),axis=1)
    if fill is not None:
        output_data.fillna(value=fill,inplace=True)
    return output_data

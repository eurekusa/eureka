import numpy as np
np.seterr(divide='raise')


def _cagr(
    begin=None,
    final=None,
    t=None,
    ):
    """
    Calculates the Compound Annual Growth Rate (CAGR).
    CAGR is a business and investing specific term for the geometric progression
    ratio that provides a constant rate of return over the time period.
    Parameters
    ----------
    begin : float, int
        Beginning value of investments.
    final : float, int
        Final value of investments.
    t : int
        Time in years.
    Returns
    -------
    cagr : float
        Compound Annual Growth Rate.

    Examples
    --------
    >>> from erikusa.metrics import formulas
    >>> formulas._cagr(begin=10, final=15,t=4)
    0.10668191970032148
    """
    if t==0 or begin==0:
        return 0
    try:
        return (final/begin)**(1/t)-1
    except:
        return 0

def _growth(
    begin=None,
    final=None
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
    begin : float, int
        Beginning value/standard unit of sales.
    final : float, int
        Final value/standard unit of sales.

    Returns
    -------
    growth : float
        Sales Growth.

    Examples
    --------
    >>> from erikusa.metrics import formulas
    >>> formulas._growth(begin=10, final=15)
    0.5
    """
    if begin:
        result= (final-begin)/begin
    else:
        result= 0
    return result

def _evolution_index(
    brand=None,
    market=None,
    percent=True
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
    brand : float, int
        The growth of the owned product.
    market : float, int
        The growth of the whole market.
    percent : bool, default True.
        Specifies whether the given growth rate in percent or not.

    Returns
    -------
    evolution index : float.

    Examples
    --------
    >>> from erikusa.metrics import formulas
    >>> formulas._evolution_index(brand=0.5, market=0.3, percent=False)
    1.1538461538461537
    """

    try:
        if percent:
            return (brand+100)/(market+100)
        else:
            return ((brand*100)+100)/((market*100)+100)
    except:
        return np.NaN
def _irr(cashflows=None):
    return np.irr(cashflows)

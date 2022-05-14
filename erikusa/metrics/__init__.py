"""
Metrcis to assess sales performance using dataframes.
"""
from ._sales_marketing_metrics import cagr
from ._sales_marketing_metrics import growth
from ._sales_marketing_metrics import evolution_index

__all__=[
    'cagr',
    'growth',
    'evolution_index',
]

import pandas as pd

def filter(orders: pd.DataFrame, sku: pd.DataFrame) -> pd.DataFrame:
    return sku[sku['SKU'].isin(orders['SKU'].unique())]
# app/utils/decimal_converter.py
from decimal import Decimal
from typing import Any

def convert_floats_to_decimal(item: Any) -> Any:
    """
    Recursively convert floats in the data to Decimal.
    """
    if isinstance(item, float):
        # Convert float to Decimal using string conversion to preserve precision
        return Decimal(str(item))
    elif isinstance(item, list):
        return [convert_floats_to_decimal(i) for i in item]
    elif isinstance(item, dict):
        return {k: convert_floats_to_decimal(v) for k, v in item.items()}
    else:
        return item
    
def convert_decimal_to_float(item: Any) -> Any:
    """
    Recursively convert Decimal objects to floats for prompt building or passing to React Flow.
    """
    if isinstance(item, Decimal):
        return float(item)
    elif isinstance(item, list):
        return [convert_decimal_to_float(i) for i in item]
    elif isinstance(item, dict):
        return {k: convert_decimal_to_float(v) for k, v in item.items()}
    return item



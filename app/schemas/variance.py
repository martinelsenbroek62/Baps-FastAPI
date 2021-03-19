import datetime as dt
from typing import List, Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods


class VarianceBase(BaseModel):
    date: dt.date
    sku: str
    demand_1: Optional[float]
    demand_2: Optional[float]
    revision_id_1: Optional[float]
    revision_id_2: Optional[float]
    month: int
    quarter: str
    year: int
    is_actual_1: Optional[bool]
    is_actual_2: Optional[bool]


class VarianceActual(VarianceBase):
    difference: float
    difference_percentage: float


class VarianceForecast(VarianceBase):
    accuracy: float
    bias: float
    mad: float
    mse: float
    mape: float
    smape: float
    wmape: float


class VarianceSummary(BaseModel):
    actual: List[VarianceActual]
    forecast: List[VarianceForecast]

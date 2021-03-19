import datetime as dt
from typing import Optional, List

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .demand_revision import DemandRevision
from .demand_center import DemandCenter

# pylint: disable=too-few-public-methods


class DemandBase(BaseModel):
    date: Optional[dt.date]
    demand: int
    revision_id: int
    sku: str


class DemandCreate(DemandBase):
    demand_center_id: int


class DemandUpdate(DemandBase):
    demand_center_id: int


class Demand(DemandBase):
    demand_center_id: int
    month: int
    quarter: str
    year: int
    is_actual: bool

    class Config:
        orm_mode = True


class DemandFull(Demand):
    revision: DemandRevision
    demand_center: DemandCenter


class DemandQuarter(DemandBase):
    quarter: str
    year: int
    is_actual: bool


class DemandYear(DemandBase):
    year: int
    is_actual: bool


class DemandSummary(BaseModel):
    monthly: List[Demand]
    quarterly: List[DemandQuarter]
    yearly: List[DemandYear]

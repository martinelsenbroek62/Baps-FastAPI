import logging
from typing import TYPE_CHECKING

from sqlalchemy import Date, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base

if TYPE_CHECKING:
    from .demand_center import DemandCenter
    from .demand_revision import DemandRevision

logger = logging.getLogger(__name__)


class Demand(Base):
    __tablename__ = "demand"

    revision_id = Column(Integer, ForeignKey("demand_revision.id"), primary_key=True)
    sku = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    demand = Column(Integer, nullable=False)
    demand_center_id = Column(Integer, ForeignKey("demand_center.id"), nullable=False)

    revision = relationship("DemandRevision", back_populates="demand")
    demand_center = relationship("DemandCenter")

    @property
    def year(self):
        return self.date.year

    @property
    def month(self):
        return self.date.month

    @property
    def quarter(self):
        qtr = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]
        year = str(self.year)[2:]
        return f"Q{qtr[self.month - 1]}{year}"

    @property
    def is_actual(self):
        if self.date.year > self.revision.revision_date.year:
            return False

        if (
            self.date.year == self.revision.revision_date.year
            and self.date.month >= self.revision.revision_date.month
        ):
            return False

        return True

    def __repr__(self) -> str:
        return (
            f"Demand(revision_id={self.revision_id}, sku={self.sku}, "
            f"date={self.date}, year={self.year}, qtr={self.quarter}, "
            f"month={self.month}, demand={self.demand}, "
            f"demand_center_id={self.demand_center_id}, "
            f"is_actual={self.is_actual})"
        )

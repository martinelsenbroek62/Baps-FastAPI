from typing import TYPE_CHECKING

from sqlalchemy import Date, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base

if TYPE_CHECKING:
    from .demand import Demand
    from .user import User


class DemandRevision(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "demand_revision"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    revision_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="demand_revisions")
    demand = relationship("Demand")

    def __repr__(self) -> str:
        return (
            f"DemandRevision(id={self.id}, name={self.name}, "
            f"description={self.description}, revision_date={self.revision_date}, "
            f"user_id={self.user_id}"
        )

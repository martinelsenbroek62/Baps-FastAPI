from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base

if TYPE_CHECKING:
    from .demand_revision import DemandRevision


class User(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)

    demand_revisions = relationship("DemandRevision")

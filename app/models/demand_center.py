from sqlalchemy import Column, Integer, String

from app.database.database import Base


class DemandCenter(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "demand_center"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # need check constraint
    country = Column(String)
    state_province = Column(String)
    city = Column(String)

    def __repr__(self) -> str:
        return (
            f"DemandCenter(id={self.id}, name={self.name}, "
            f"type={self.type}, country={self.country}, "
            f"state_province={self.state_province}, "
            f"city={self.city})"
        )

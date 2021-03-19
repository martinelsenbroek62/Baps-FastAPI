from datetime import date

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .user import User

# pylint: disable=too-few-public-methods


class DemandRevisionBase(BaseModel):
    name: str
    description: str
    revision_date: date
    user_id: int


class DemandRevisionCreate(DemandRevisionBase):
    pass


class DemandRevisionUpdate(DemandRevisionBase):
    pass


class DemandRevision(DemandRevisionBase):
    id: int

    class Config:
        orm_mode = True


class DemandRevisionFull(DemandRevision):
    id: int
    user: User

    class Config:
        orm_mode = True

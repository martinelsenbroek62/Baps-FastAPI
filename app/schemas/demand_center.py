from pydantic import BaseModel  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods


class DemandCenterBase(BaseModel):
    name: str
    type: str
    country: str
    state_province: str
    city: str


class DemandCenterCreate(DemandCenterBase):
    pass


class DemandCenterUpdate(DemandCenterBase):
    pass


class DemandCenter(DemandCenterBase):
    id: int

    class Config:
        orm_mode = True

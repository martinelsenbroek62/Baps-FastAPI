from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

# pylint: disable=too-few-public-methods


class UserBase(BaseModel):
    username: str


# Properties to receive via API on creation
class UserCreate(UserBase):
    pass


# Properties to receive via API on update
class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    pass

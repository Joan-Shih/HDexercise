from pydantic import BaseModel
from typing import Optional, Union

class UserIn(BaseModel):
    username: str
    password: str
    is_auth: Optional[bool] = False

class UserOut(BaseModel):
    username: str
    password: str
    is_auth: Union[bool, int]

class RecordOut(BaseModel):
    record_id: int
    username: str
    create_date: str
    exercise: float

class RecordIn(BaseModel):
    username: str
    create_date: str
    exercise: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    is_auth: Union[bool, int]
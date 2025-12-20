# auth/schemas.py
from typing import Optional

from pydantic import BaseModel, EmailStr
from src.auth.models import User

class SystemUser(BaseModel):

    id: int
    username: str
    email: EmailStr
    photo: Optional[str] = None
    status: bool = True

    model_config = {'from_attributes': True}



class Token(BaseModel):
    access_token: str
    token_type: str




class UserInDB(User):
    hashed_password: str


class CreateAccount(BaseModel):

    username: str
    email: EmailStr
    password: str
    photo: Optional[str] | None = None
    status: bool = True

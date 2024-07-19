from datetime import date

from pydantic import BaseModel


class UserData(BaseModel):
    full_name: str
    phone: str
    email: str
    password1: str
    password2: str
    image_id: int

class UserInDb(BaseModel):
    full_name:str
    phone:str
    email:str
    password:str
    image_id:int
    is_active:bool
    register_at:date


class UserInfo(BaseModel):
    full_name:str
    phone:str
    email:str


class UserLogin(BaseModel):
    email: str
    password: str


class Category_get(BaseModel):
    id:int
    name:str


from typing import Optional

from pydantic import BaseModel


class Add_Product(BaseModel):
    name:str
    count:int
    price:float
    category_id:int
    image_id:int


class Edit_Product(BaseModel):
    name:Optional[str]=None
    count:Optional[int]=None
    price:Optional[float]=None
    category_id:Optional[int]=None
    image_id:Optional[int]=None


class ImageSchema(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode = True

class CategorySchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    id: int
    full_name: str
    phone: str
    email: str

    class Config:
        orm_mode = True

class ProductSchema(BaseModel):
    id: int
    name: str
    count: int
    price: float
    category: Optional[CategorySchema]
    image: Optional[ImageSchema]
    owner: Optional[UserSchema]

    class Config:
        orm_mode = True

from datetime import datetime
from sqlalchemy import (MetaData,
                        Column,
                        Integer,
                        String,
                        ForeignKey,
                        TIMESTAMP, Text, Float, CheckConstraint, Boolean)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

metadata = MetaData()
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    metadata = metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String)
    phone = Column(String, unique=True)
    email = Column(String,unique=True)
    password = Column(Text)
    image_id=Column(Integer,ForeignKey("images.id"))
    is_active=Column(Boolean,default=True)
    register_at = Column(TIMESTAMP, default=datetime.utcnow)

    images = relationship('Images', back_populates='user')
    products = relationship('Products', back_populates='user')


class Category(Base):
    __tablename__ = "category"
    metadata=metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    products = relationship("Products",back_populates="category")


class Products(Base):
    __tablename__="products"
    metadata=metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    count=Column(Integer)
    price = Column(Float)
    category_id=Column(Integer,ForeignKey("category.id"))
    image_id = Column(Integer,ForeignKey("images.id"))
    owner_id = Column(Integer,ForeignKey("user.id"))

    images = relationship('Images', back_populates='products')
    category  = relationship('Category', back_populates='products')
    user  = relationship('User', back_populates='products')





class Images(Base):
    __tablename__ =  "images"
    metadata=metadata
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text)

    user = relationship('User', back_populates='images')
    products = relationship('Products', back_populates='images')



from typing import List, Dict
import aiofiles
from datetime import datetime
from database import get_async_session
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, HTTPException, FastAPI, UploadFile, File
from dotenv import load_dotenv
from passlib.context import CryptContext
import os
from .schemes import UserData, UserInDb, UserInfo, UserLogin, Category_get
from models.models import User, Images, Category
from .utils import generate_token
import bcrypt

load_dotenv()
register_router = APIRouter()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@register_router.post('/upload_image')
async def upload_image(
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        directory = 'images'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the uploaded image
        filename = image.filename
        url = os.path.join(directory, filename)
        async with aiofiles.open(url, 'wb') as f:
            content = await image.read()
            await f.write(content)
        print(url)
        # Insert the image and flush to get the image_id
        image_query = insert(Images).values(url=url).returning(Images.id)
        image_result = await session.execute(image_query)
        image_id = image_result.scalar()

        await session.commit()

        return {
            "success": True,
            "data": {"image_id": image_id},
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": str(e),
                "message": "Internal server error",
                "code": 500
            }
        }


@register_router.post('/register')
async def register(user: UserData, session: AsyncSession = Depends(get_async_session)):
    if user.password1 != user.password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        if user.password1 != user.password2:
            return {
                "success": False,
                "data": None,
                "error": {
                    "exception": "Passwords are not the same",
                    "message": "Passwords are not the same",
                    "code": 400
                }
            }

        check = select(User).where(User.phone == user.phone or User.email == user.email)
        check_exists = await session.execute(check)
        if check_exists.scalar_one_or_none():
            return {
                "success": False,
                "data": None,
                "error": {
                    "exception": "Email or phone number already used",
                    "message": "Email or phone number already used",
                    "code": 400
                }
            }

        password = pwd_context.hash(user.password2)
        user_in_db = UserInDb(**dict(user), password=password, register_at=datetime.utcnow().date(), is_active=True)
        query = insert(User).values(**dict(user_in_db))
        await session.execute(query)
        await session.commit()
        user_info = UserInfo(**dict(user_in_db))
        return {
            "success": True,
            "data": user_info,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": str(e),
                "message": "Internal server error",
                "code": 500
            }
        }


@register_router.post('/login')
async def login(model: UserLogin, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(User).where(User.email == model.email).limit(1)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            print(user.id)
            token = generate_token(user.id)
            return {
                "success": True,
                "data": {"user_id": user.id,
                         "access": token["access"],
                         "refresh": token["refresh"],
                         },
                "error": None
            }
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": "Driver not found",
                "message": "Driver not found",
                "code": 400
            }
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": str(e),
                "message": "Internal server error",
                "code": 500
            }
        }


@register_router.post("/Category")
async def add_category(name: str,
                       session: AsyncSession = Depends(get_async_session)):
    try:
        query = insert(Category).values(name=name)
        await session.execute(query)
        await session.commit()
        return {
            "success": True,
            "data": {"message": "Added"},
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": str(e),
                "message": "Internal server error",
                "code": 500
            }
        }


@register_router.get("/Category",response_model=List[Category_get])
async def get_category(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Category)
        res = await session.execute(query)
        result = res.scalars().all()
        return result
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": str(e),
                "message": "Internal server error",
                "code": 500
            }
        }

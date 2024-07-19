from typing import List

from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from auth.utils import verify_token
from database import get_async_session
from models.models import Products
from products.schemes import Add_Product, ProductSchema, Edit_Product
from config import BASE_URL

product_router = APIRouter()


@product_router.get("/products/{product_id}")
async def get_products(product_id: int,
                       session: AsyncSession = Depends(get_async_session)
                       ):
    try:
        query = (
            select(Products)
            .options(
                joinedload(Products.category),
                joinedload(Products.images),
                joinedload(Products.user)
            )
            .where(Products.id == product_id)
        )
        result = await session.execute(query)
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        def to_get_category(category):
            return {
                "id": category.id,
                "name": category.name
            }

        def to_get_image(image):
            return {
                "id": image.id,
                "url": f"{BASE_URL}{image.url}"
            }

        result = {
            "id": product.id,
            "name": product.name,
            "count": product.count,
            "price": product.price,
            "category": to_get_category(product.category),
            "image": to_get_image(product.images),
            "owner": product.owner_id
        }
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

@product_router.get("/products", response_model=dict)
async def get_all_products(session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(Products)
            .options(
                joinedload(Products.category),
                joinedload(Products.images),
                joinedload(Products.user)
            )
        )
        result = await session.execute(query)
        products = result.scalars().all()

        if not products:
            raise HTTPException(status_code=404, detail="No products found")

        def to_get_category(category):
            return {
                "id": category.id,
                "name": category.name
            }

        def to_get_image(image):
            return {
                "id": image.id,
                "url": f"{BASE_URL}{image.url}"
            }

        def to_product_schema(product):
            return {
                "id": product.id,
                "name": product.name,
                "count": product.count,
                "price": product.price,
                "category": to_get_category(product.category) if product.category else None,
                "images": to_get_image(product.images) if product.images else None,
                "user": product.owner_id
            }

        result = [to_product_schema(product) for product in products]
        return {
            "success": True,
            "data": result,
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
@product_router.post("/products", response_model=dict)
async def create_product(product: Add_Product,
                         token: dict = Depends(verify_token),
                         session: AsyncSession = Depends(get_async_session)
                         ):
    try:
        user_id = token.get("user_id")
        query = insert(Products).values(**dict(product), owner_id=user_id)
        await session.execute(query)
        await session.commit()
        return {
            "success": True,
            "data": {"message": "Product added successfully"},
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

@product_router.put("/products/{product_id}")
async def update_product(product_id: int, product: Edit_Product, session: AsyncSession = Depends(get_async_session)):
    try:
        update_data = {k: v for k, v in product.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        query = update(Products).where(Products.id == product_id).values(**update_data).execution_options(synchronize_session="fetch")
        await session.execute(query)
        await session.commit()

        return {
            "success": True,
            "data": {"message": "Updated"},
            "error": None
        }
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": str(e),
                "message": "Internal server error",
                "code": 500
            }
        }
@product_router.delete("/products/{product_id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Products).where(Products.id == product_id)
        result = await session.execute(query)
        db_product = result.scalar_one_or_none()

        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        # Delete the product
        await session.delete(db_product)
        await session.commit()

        return {
            "success": True,
            "data": None,
            "error": None,
            "message": "Product deleted"
        }
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "data": None,
            "error": {
                "exception": str(e),
                "message": "Internal server error",
                "code": 500
            }
        }

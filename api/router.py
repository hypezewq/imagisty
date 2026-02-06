from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from curl_fetch2py import CurlFetch2Py
from api.schemas import RequestData
from api.utils import execute_request
from typing import List
from data.database import *
from models.AutoPart import AutoPart

router = APIRouter(prefix='', tags=['API'])
templates = Jinja2Templates(directory='templates')


@router.get('/')
async def get_main_page(request: Request):
    return templates.TemplateResponse(name='index.html', context={'request': request})

@router.get("/products")
async def get_products(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20),
    search: str | None = None,
    category: str | None = None,
):
    stmt = select(AutoParts)

    if search:
        stmt = stmt.where(
            AutoParts.name.ilike(f"%{search}%")
        )

    if category:
        stmt = stmt.where(
            AutoParts.category == category
        )

    stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    products = result.scalars().all()

    return [
        {
            "id": autopart.id,
            "title": autopart.name,
            "price": autopart.cost,
            "category": autopart.category,
        } for autopart in products
    ]
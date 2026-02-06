import asyncio

from sqlalchemy import select, func

from config import db_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.testing.schema import mapped_column

async_session_maker = async_sessionmaker(create_async_engine(db_url),
                                         expire_on_commit=False)
ru_to_eng = {
    "Автоинструмент и принадлежности": "AutoTool",
    "Автозапчасти ВАЗ": "VAZtools",
    "Автохимия и масла": "Oilchemistry"
}

eng_to_ru = {
    "AutoTool": "Автоинструмент и принадлежности",
    "VAZtools": "Автозапчасти ВАЗ",
    "Oilchemistry": "Автохимия и масла",
}

async def get_db():
    async with async_session_maker() as session:
        yield session


def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return wrapper


class Base(DeclarativeBase, AsyncAttrs):
    pass


class AutoParts(Base):
    __tablename__ = 'autoparts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    code: Mapped[int] = mapped_column(nullable=True)
    production: Mapped[str] = mapped_column(nullable=True)
    article: Mapped[int] = mapped_column(nullable=True)
    cost: Mapped[float] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=True)
    
    def __repr__(self):
        return f"{self.id} {self.name}: {self.category} - {self.cost}"


@connection
async def get_autoparts_by_category(category: str, session: AsyncSession):
    autoparts = await session.execute(select(AutoParts).where(AutoParts.category == category))
    return autoparts.scalars().all()


@connection
async def get_categories(session: AsyncSession):
    categories = await session.execute(select(AutoParts.category))
    return categories.scalars().unique().all()

@connection
async def get_autoparts(session: AsyncSession):
    autoparts = await session.execute(select(AutoParts))
    return autoparts.scalars().all()


@connection
async def get_autopart(id: int, session: AsyncSession):
    autopart = await session.execute(select(AutoParts).where(AutoParts.id == id))
    return autopart.scalars().first()


@connection
async def get_autoparts_by_name(name: str, session: AsyncSession):
    autoparts = await session.execute(select(AutoParts).where(
        AutoParts.name.contains(name.lower()) | AutoParts.name.contains(name.capitalize()) | AutoParts.name.contains(
        name.upper())))
    return autoparts.scalars().all()

@connection
async def get_cart(ids: list[int], session: AsyncSession):
    return [await get_autopart(id) for id in ids]



async def main():
    ...


if __name__ == '__main__':
    asyncio.run(main())

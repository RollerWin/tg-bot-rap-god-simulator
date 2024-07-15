from database.models import Item
from database.database_manager import async_session
from sqlalchemy import select, update, delete


async def add_item(name, price, is_legal, description=None):
    async with async_session() as session:
        session.add(Item(name=name, price=price, description=description, is_legal=is_legal))
        await session.commit()


async def get_items():
    async with async_session() as session:
        items = await session.scalars(select(Item))
        return items


async def get_item(id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == id))
        return item

from database.models import UserItemAssociation, Item
from database.database_manager import async_session
from sqlalchemy import select, delete


async def add_association(player_id: int, item_id: int):
    async with async_session() as session:
        session.add(UserItemAssociation(player_id=player_id, item_id=item_id))
        await session.commit()


async def get_items(player_id):
    async with async_session() as session:
        items = await session.scalars(select(Item).where(UserItemAssociation.item_id == Item.id and
                                                         UserItemAssociation.player_id == player_id))
        return items


async def is_user_got_item(player_id: int, item_name: str):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.name == item_name and
                                                       UserItemAssociation.item_id == Item.id and
                                                       UserItemAssociation.player_id == player_id))
        if item:
            return True
        else:
            return False


async def remove_illegal_associations(player_id):
    async with async_session() as session:
        await session.execute(
            delete(UserItemAssociation)
            .where(UserItemAssociation.player_id == player_id and
                   select(Item).where(Item.is_legal is False) == UserItemAssociation.item_id)
        )
        await session.commit()

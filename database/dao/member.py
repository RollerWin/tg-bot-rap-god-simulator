from database.models import Player, StatsPlayer, Track, Label, Member
from database.database_manager import async_session
from sqlalchemy import select, update, delete

from game_configuration import DefaultPlayerState, DefaultGameConfiguration


async def add_member(tg_id, label_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))

        session.add(Label(
            label_id=label_id,
            player_founder_id=player.id
        ))
        await session.commit()


async def remove_member(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        await session.execute(
            delete(Member)
            .where(Member.player_id == player.id)
        )
        await session.commit()


async def is_user_member(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        result = await session.scalar(select(Member).where(Member.player_id == player.id))

        if result:
            return True
        else:
            return False

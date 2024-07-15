from database.models import Player, StatsPlayer, Track, Label
from database.database_manager import async_session
from sqlalchemy import select, update, delete

from game_configuration import DefaultPlayerState, DefaultGameConfiguration
from database.dao.member import add_member


async def add_label(tg_id, label_name):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))

        session.add(Label(
            label_name=label_name,
            player_founder_id=player.id
        ))
        await session.commit()


async def is_user_founder(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        is_founder = await session.scalar(select(Label).where(Label.player_founder_id == player.id))

        if is_founder:
            return True
        else:
            return False

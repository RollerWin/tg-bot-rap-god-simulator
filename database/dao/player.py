from database.models import Player
from database.database_manager import async_session
from sqlalchemy import select, update, delete


async def add_player(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))

        if not player:
            session.add(Player(tg_id=tg_id))
            await session.commit()
        elif player:
            return True
        else:
            return False


async def edit_player(tg_id, username):
    async with async_session() as session:
        await session.execute(
            update(Player)
            .where(Player.tg_id == tg_id)
            .values(username=username)
        )
        await session.commit()


async def get_player_count():
    async with async_session() as session:
        players = await session.scalars(select(Player))
        players_count = players.count()
        return players_count


async def get_player(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        return player


async def get_players():
    async with async_session() as session:
        players = await session.scalars(select(Player))
        return players

from database.models import Player, StatsPlayer
from database.database_manager import async_session
from sqlalchemy import select, update, delete

from game_configuration import DefaultPlayerState, DefaultGameConfiguration


async def add_stats_player(skin_color_type, tg_id, balance_bonus=0, fame_bonus=0, respect_bonus=0):
    async with async_session() as session:
        if skin_color_type is DefaultPlayerState.WHITE_SKIN_COLOR_INDEX:
            criminal = DefaultPlayerState.WHITE_SKIN_CRIMINAL_RATE
            balance = DefaultPlayerState.WHITE_SKIN_BALANCE
            fame = DefaultPlayerState.WHITE_SKIN_FAME
            respect = DefaultPlayerState.WHITE_SKIN_RESPECT
        else:
            criminal = DefaultPlayerState.BLACK_SKIN_CRIMINAL_RATE
            balance = DefaultPlayerState.BLACK_SKIN_BALANCE
            fame = DefaultPlayerState.BLACK_SKIN_FAME
            respect = DefaultPlayerState.BLACK_SKIN_RESPECT

        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))

        if player.id <= DefaultGameConfiguration.NUMBER_OF_OG_PLAYERS:
            status = "OG"
        else:
            status = None

        session.add(StatsPlayer(
            skin_color=skin_color_type,
            criminal_rate=criminal,
            balance=balance + balance_bonus,
            fame=fame + fame_bonus,
            respect=respect + respect_bonus,
            status=status,
            player_id=player.id
        ))
        await session.commit()


async def edit_stats_player_by_refferal_code(tg_id, balance, fame, respect):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        await session.execute(update(StatsPlayer)
                              .where(StatsPlayer.player_id == player.id)
                              .values(
                                  balance=StatsPlayer.balance + balance,
                                  fame=StatsPlayer.fame + fame,
                                  respect=StatsPlayer.respect + respect
                              ))
        await session.commit()


async def get_stats_player(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        stats = await session.scalar(select(StatsPlayer).where(StatsPlayer.player_id == player.id))
        return stats


async def get_balance(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        stats = await session.scalar(select(StatsPlayer).where(StatsPlayer.player_id == player.id))
        return int(stats.balance)


async def get_criminal_rate(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        stats = await session.scalar(select(StatsPlayer).where(StatsPlayer.player_id == player.id))
        return int(stats.criminal_rate)


async def spend_money(tg_id, price):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        await session.execute(
            update(StatsPlayer)
            .where(StatsPlayer.player_id == player.id)
            .values(balance=StatsPlayer.balance - price)
        )
        await session.commit()


async def add_money(tg_id, price):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        await session.execute(
            update(StatsPlayer)
            .where(StatsPlayer.player_id == player.id)
            .values(balance=StatsPlayer.balance + price)
        )
        await session.commit()


async def added_criminal_rate(tg_id, rate):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        await session.execute(
            update(StatsPlayer)
            .where(StatsPlayer.player_id == player.id)
            .values(criminal_rate=StatsPlayer.criminal_rate + rate)
        )
        await session.commit()


async def add_fame(tg_id, fame):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        await session.execute(
            update(StatsPlayer)
            .where(StatsPlayer.player_id == player.id)
            .values(fame=StatsPlayer.fame + fame)
        )
        await session.commit()


async def add_respect(tg_id, respect):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        await session.execute(
            update(StatsPlayer)
            .where(StatsPlayer.player_id == player.id)
            .values(respect=StatsPlayer.respect + respect)
        )
        await session.commit()

from database.models import Player, PlayerInGame
from database.database_manager import async_session
from sqlalchemy import select, delete, update
import random


async def add_player_game(player_id, game_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == player_id))

        session.add(PlayerInGame(player_id=player.id, game_id=game_id))
        await session.commit()


async def get_player_in_game(game_id, player_id):
    async with async_session() as session:
        current_player = await session.scalar(select(Player).where(Player.tg_id == player_id))

        players = await session.scalars(select(PlayerInGame)
                                        .where(PlayerInGame.game_id == game_id and
                                               PlayerInGame.player_id != current_player.id))
        players_list = [player.player_id for player in players]
        if not players_list:
            return None
        chosen_player_id = random.choice(players_list)

        return await session.scalar(select(Player).where(Player.id == chosen_player_id))


async def update_game_result(player_id, game_result):
    async with async_session() as session:
        current_player = await session.scalar(select(Player).where(Player.tg_id == player_id))
        await session.execute(update(PlayerInGame)
                              .where(PlayerInGame.player_id == current_player.id)
                              .values(game_result=game_result))
        await session.commit()


async def remove_player_in_game(player_id, game_id):
    async with async_session() as session:
        current_player = await session.scalar(select(Player).where(Player.tg_id == player_id))

        await session.execute(delete(PlayerInGame)
                              .where(PlayerInGame.game_id == game_id and
                                     PlayerInGame.player_id == current_player.id))
        await session.commit()



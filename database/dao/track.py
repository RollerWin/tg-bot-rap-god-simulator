from database.models import Player, StatsPlayer, Track
from database.database_manager import async_session
from sqlalchemy import select, update, delete

from game_configuration import DefaultPlayerState, DefaultGameConfiguration


async def add_track(tg_id, track_name):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))

        session.add(Track(
            player_id=player.id,
            track_name=track_name,
            number_of_listeners=0
        ))
        await session.commit()


async def get_all_tracks():
    async with async_session() as session:
        tracks = await session.scalars(select(Track))
        return tracks


async def get_tracks_by_author(tg_id):
    async with async_session() as session:
        player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
        tracks = await session.scalars(select(Track).where(Track.player_id == player.id))
        return tracks


async def get_track_info(track_id):
    async with async_session() as session:
        track = await session.scalar(select(Track).where(Track.id == track_id))
        return track


async def increase_track_listeners(track_id, number_of_listeners):
    async with async_session() as session:
        track = await session.scalar(select(Track).where(Track.id == track_id))
        track.number_of_listeners += number_of_listeners
        await session.commit()


async def get_author_by_track(track_id):
    async with async_session() as session:
        track = await session.scalar(select(Track).where(Track.id == track_id))
        player = await session.scalar(select(Player).where(Player.id == track.player_id))
        return player


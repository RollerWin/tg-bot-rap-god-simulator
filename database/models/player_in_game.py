from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class PlayerInGame(Base):
    __tablename__ = 'players_in_game'

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(nullable=False)
    player_id = mapped_column(BigInteger, ForeignKey("players.id"))
    game_result: Mapped[int] = mapped_column(nullable=True)

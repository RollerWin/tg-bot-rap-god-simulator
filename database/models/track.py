from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Track(Base):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(primary_key=True)
    track_name: Mapped[str] = mapped_column(nullable=False)
    number_of_listeners: Mapped[int] = mapped_column(nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))

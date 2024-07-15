from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Album(Base):
    __tablename__ = 'albums'

    id: Mapped[int] = mapped_column(primary_key=True)
    album_name: Mapped[str] = mapped_column(nullable=False)
    number_of_listeners: Mapped[int] = mapped_column(nullable=False)
    player_author_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    label_id: Mapped[int] = mapped_column(ForeignKey("labels.id"))

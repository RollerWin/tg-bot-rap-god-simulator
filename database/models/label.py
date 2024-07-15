from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Label(Base):
    __tablename__ = 'labels'

    id: Mapped[int] = mapped_column(primary_key=True)
    label_name: Mapped[str] = mapped_column(nullable=False)
    player_founder_id: Mapped[int] = mapped_column(ForeignKey("players.id"))

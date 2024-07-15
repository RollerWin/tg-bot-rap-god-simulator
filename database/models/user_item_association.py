from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class UserItemAssociation(Base):
    __tablename__ = 'user_item_associations'

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

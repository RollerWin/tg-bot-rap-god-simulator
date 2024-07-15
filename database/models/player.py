from sqlalchemy import BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, unique=False)
    username: Mapped[str] = mapped_column(nullable=True)

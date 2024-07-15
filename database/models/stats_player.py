from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class StatsPlayer(Base):
    __tablename__ = "stats_players"

    id: Mapped[int] = mapped_column(primary_key=True)
    skin_color: Mapped[int] = mapped_column(nullable=False)
    criminal_rate: Mapped[int] = mapped_column(nullable=False)
    balance: Mapped[int] = mapped_column(nullable=False)
    fame: Mapped[int] = mapped_column(nullable=False)
    respect: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))

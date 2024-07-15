from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class DonateOrderHistory(Base):
    __tablename__ = 'donate_order_history'

    id: Mapped[int] = mapped_column(primary_key=True)

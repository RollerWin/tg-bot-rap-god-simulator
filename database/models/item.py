from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[int] = mapped_column(nullable=False)
    is_legal: Mapped[bool] = mapped_column(default=True)
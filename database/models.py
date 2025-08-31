from sqlalchemy import DateTime, Integer, Float, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData

metadata = MetaData(schema='public')

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = {'schema': 'public'}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    index: Mapped[int] = mapped_column(Integer(), nullable=False)
    #index: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)


from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Serializer(object):

    @property
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class Base(DeclarativeBase):
    ...


class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    postcode: Mapped[str] = mapped_column(String(50), nullable=False)


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    shipped_date: Mapped[datetime] = mapped_column(DateTime)
    delivered_date: Mapped[datetime] = mapped_column(DateTime)
    coupon_code: Mapped[str] = mapped_column(String(50))


# class Order(Base):
#     __tablename__ = 'order'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#
#     member_id = mapped_column(ForeignKey("member.id"))
#     member: Mapped['Member'] = relationship(back_populates='orders')
#
#
# class Member(Base, Serializer):
#     __tablename__ = 'member'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#
#     username: Mapped[str] = mapped_column(String(30), unique=True)
#     password: Mapped[str] = mapped_column(String(50))
#     email: Mapped[str] = mapped_column(String(50))
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.now())
#
#     orders: Mapped[list["Order"]] = relationship(back_populates='member')
#
#     @property
#     def serialize(self):
#         serialize: dict = super().serialize
#         del serialize['password']
#         return serialize
#
#     def __repr__(self):
#         return (
#             f'{type(self).__name__}({self.id=}, {self.username=}, {self.password=}, {self.email=}, {self.created_at=})'
#         )

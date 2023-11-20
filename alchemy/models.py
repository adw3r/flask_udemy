import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    ...


class TestModel(Base):
    __tablename__ = 'test_model'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Serializer(object):

    @property
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    member_id = mapped_column(ForeignKey("member.id"))
    member: Mapped['Member'] = relationship(back_populates='orders')


class Member(Base, Serializer):
    __tablename__ = 'member'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now())

    orders: Mapped[list["Order"]] = relationship(back_populates='member')

    @property
    def serialize(self):
        serialize: dict = super().serialize
        del serialize['password']
        return serialize

    def __repr__(self):
        return (
            f'{type(self).__name__}({self.id=}, {self.username=}, {self.password=}, {self.email=}, {self.created_at=})'
        )

from sqlalchemy import MetaData, ARRAY, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr,
)

from core.config import settings
from utils import camel_case_to_snake_case


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls):
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    def dict(self, cast=False):
        if not cast:
            return {
                c.name: getattr(self, c.name)
                for c in self.__table__.columns.__iter__()
            }
        else:
            return {
                c.name: str(getattr(self, c.name))
                for c in self.__table__.columns.__iter__()
            }

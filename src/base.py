import re
import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):

    __abstract__: bool = True

    @classmethod
    @declared_attr
    def __tablename__(cls):
        class_name = cls.__name__
        words = [word.lower() for word in re.findall("[A-Z][a-z0-9]*", class_name)]
        table_name = "_".join(words) + "s"
        return table_name

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attributes = ", ".join(
            f"{attr}={getattr(self, attr)}" for attr in self.__mapper__.column_attrs.keys()
        )
        return f"<{class_name}({attributes})>"


class BaseIDMixin:

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)


class BaseTimeMixin:

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

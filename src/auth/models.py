import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import TIMESTAMP, ForeignKey, false, true
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..database import Base
from ..patient.models import Patient


uniq_str_param = Annotated[str, mapped_column(nullable=False, unique=True)]
datetime_tz_param = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True), server_default=func.now())]


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[uniq_str_param]
    created_at: Mapped[datetime_tz_param]

    role: Mapped[str] = mapped_column(nullable=True, default="explorer", server_default="explorer")
    is_superuser: Mapped[bool] = mapped_column(default=False, server_default=false())
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())

    patients: Mapped[list["Patient"]] = relationship("Patient", back_populates="therapist")

    def __str__(self):
        return self.username


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    expires_in: Mapped[int]
    created_at: Mapped[datetime_tz_param]

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"))

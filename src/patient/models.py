import uuid
from typing import Annotated

from sqlalchemy import UUID, ForeignKey, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, BaseIDMixin
from ..patient_records.models import PatientRecord


str_null = Annotated[str, mapped_column(nullable=True)]
str_not_null = Annotated[str, mapped_column(nullable=False)]


class Patient(Base, BaseIDMixin):

    gender: Mapped[str_not_null]
    birthday: Mapped[str_null]
    full_name: Mapped[str_not_null]
    living_place: Mapped[str_null]
    job_title: Mapped[str_null]
    inhabited_locality: Mapped[str_null]

    bp: Mapped[bool] = mapped_column(default=False, server_default=false())
    ischemia: Mapped[bool] = mapped_column(default=False, server_default=false())
    dep: Mapped[bool] = mapped_column(default=False, server_default=false())

    therapist_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"))

    records: Mapped[list["PatientRecord"]] = relationship("PatientRecord", back_populates="patient")
    therapist = relationship("User", back_populates="patients")

    def __str__(self):
        return self.full_name

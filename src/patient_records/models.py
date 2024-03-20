import uuid
from typing import Annotated

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, BaseIDMixin


str_null = Annotated[str, mapped_column(nullable=True)]
str_not_null = Annotated[str, mapped_column(nullable=False)]


class PatientRecord(Base, BaseIDMixin):

    diagnosis: Mapped[str_null]
    visit: Mapped[str]
    treatment: Mapped[str_null]

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("patients.id", ondelete="CASCADE"), nullable=True
    )
    therapist_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)

    patient = relationship("Patient", back_populates="records")

    def __str__(self):
        return str(self.visit)

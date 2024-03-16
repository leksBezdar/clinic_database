import uuid
from typing import Annotated

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

str_null = Annotated[str, mapped_column(nullable=True)]
str_not_null = Annotated[str, mapped_column(nullable=False)]


class PatientRecord(Base):
    __tablename__ = "patient_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    diagnosis: Mapped[str_null]
    visit: Mapped[str]
    treatment: Mapped[str_null]

    patient_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("patients.id"))
    therapist_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)

    patient = relationship("Patient", back_populates="records")

    def __str__(self):
        return str(self.visit)

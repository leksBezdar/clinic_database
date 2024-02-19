import uuid
from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import  Mapped, mapped_column

from ..database import Base


class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    age: Mapped[int] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=False)
    birthday: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=False)
    living_place: Mapped[str] = mapped_column(nullable=True)
    job_title: Mapped[str] = mapped_column(nullable=True)
    diagnosis: Mapped[str] = mapped_column(nullable=True)
    first_visit: Mapped[str] = mapped_column(nullable=True)
    last_visit: Mapped[str] = mapped_column(nullable=True)
    treatment: Mapped[str] = mapped_column(nullable=True)
    inhabited_locality: Mapped[str] = mapped_column(nullable=True)
    
    bp: Mapped[str] = mapped_column(nullable=False)
    ischemia: Mapped[str] = mapped_column(nullable=False)
    dep: Mapped[str] = mapped_column(nullable=False)
    
    therapist_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)


from datetime import date

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    age: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    birthday: Mapped[date] = mapped_column(nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    living_place: Mapped[str] = mapped_column(nullable=True)
    job_title: Mapped[str] = mapped_column(nullable=True)
    diagnosis: Mapped[str] = mapped_column(nullable=True)
    first_visit: Mapped[date] = mapped_column(nullable=True)
    last_visit: Mapped[date] = mapped_column(nullable=True)
    treatment: Mapped[str] = mapped_column(nullable=True)
    inhabited_locality: Mapped[str] = mapped_column(nullable=True)
    
    therapist_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)


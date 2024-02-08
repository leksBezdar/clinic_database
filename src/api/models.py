from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    age: Mapped[int] = mapped_column(nullable=False)
    birthday: Mapped[datetime] = mapped_column(nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    living_place: Mapped[str] = mapped_column(nullable=False)
    job_title: Mapped[str] = mapped_column(nullable=False)
    diagnosis: Mapped[str] = mapped_column(nullable=False)
    first_visit: Mapped[datetime] = mapped_column(nullable=False)
    last_visit: Mapped[datetime] = mapped_column(nullable=False)
    treatment: Mapped[str] = mapped_column(nullable=False)
    inhabited_locality: Mapped[str] = mapped_column(nullable=False)
    
    therapist_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    
    
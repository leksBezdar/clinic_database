from .models import Patient
from .schemas import PatientCreate, PatientUpdate

from ..dao import BaseDAO


class PatientDAO(BaseDAO[Patient, PatientCreate, PatientUpdate]):
    model = Patient

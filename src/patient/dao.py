from ..dao import BaseDAO
from .models import Patient
from .schemas import PatientCreateDB, PatientUpdate


class PatientDAO(BaseDAO[Patient, PatientCreateDB, PatientUpdate]):
    model = Patient

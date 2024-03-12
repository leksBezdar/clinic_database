from .models import Patient
from .schemas import PatientCreateDB, PatientUpdate

from ..dao import BaseDAO


class PatientDAO(BaseDAO[Patient, PatientCreateDB, PatientUpdate]):
    model = Patient

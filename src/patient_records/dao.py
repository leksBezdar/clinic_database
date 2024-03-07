from .models import PatientRecord
from .schemas import PatientRecordsCreate, PatientRecordsUpdate

from ..dao import BaseDAO


class PatientRecordsDAO(BaseDAO[PatientRecord, PatientRecordsCreate, PatientRecordsUpdate]):
    model = PatientRecord

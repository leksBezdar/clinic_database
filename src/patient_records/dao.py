from ..dao import BaseDAO
from .models import PatientRecord
from .schemas import PatientRecordsCreate, PatientRecordsUpdate


class PatientRecordsDAO(BaseDAO[PatientRecord, PatientRecordsCreate, PatientRecordsUpdate]):
    model = PatientRecord

from sqladmin import  ModelView

from ..auth.models import User
from ..patient.models import Patient
from ..patient_records.models import PatientRecord


class UserAdmin(ModelView, model=User):
    column_list = [User.username, User.role, User.is_superuser, User.patients]
    
    can_delete = False
    can_edit = False
    can_export = False
    page_size = 100
    icon = "fa-solid fa-user-doctor"
    column_searchable_list = [User.username, User.role]
    column_sortable_list = [User.role, User.is_superuser]
    column_labels = {User.username : "ФИО", User.role : "Роль"}
    
class PatientAdmin(ModelView, model=Patient):
    column_list = [Patient.full_name, Patient.therapist, Patient.records]
    
    can_delete = False
    can_edit = False
    can_export = False
    page_size = 100
    icon = "fa-solid fa-user"
    column_searchable_list = [Patient.full_name, Patient.therapist]
    column_sortable_list = [Patient.therapist, Patient.gender]
    
    
class PatientRecordAdmin(ModelView, model=PatientRecord):
    column_list = [PatientRecord.patient, PatientRecord.visit]
    
    can_delete = False
    can_edit = False
    can_export = False
    page_size = 100
    icon = "fa-solid fa-file-medical"
    column_searchable_list = [PatientRecord.patient, PatientRecord.visit]
    column_sortable_list = [PatientRecord.visit]
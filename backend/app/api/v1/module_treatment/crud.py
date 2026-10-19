"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import MedicalRecord, Prescription
from .schema import MedicalRecordSchema, MedicalRecordCreateSchema, MedicalRecordUpdateSchema, PrescriptionSchema, PrescriptionCreateSchema, PrescriptionUpdateSchema



class MedicalRecordCRUD(CRUDBase[MedicalRecord, MedicalRecordCreateSchema, MedicalRecordUpdateSchema]):
    """MedicalRecord 数据层"""

    pass


class PrescriptionCRUD(CRUDBase[Prescription, PrescriptionCreateSchema, PrescriptionUpdateSchema]):
    """Prescription 数据层"""

    pass


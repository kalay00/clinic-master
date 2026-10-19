"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Diagnosis, TCMDiagnosis, TCMFourExaminations, TCMTreatment, TCMPrescription, TCMPrescriptionItem, TCMFormula, TCMDecoctionService
from .schema import DiagnosisSchema, DiagnosisCreateSchema, DiagnosisUpdateSchema, TCMDiagnosisSchema, TCMDiagnosisCreateSchema, TCMDiagnosisUpdateSchema, TCMFourExaminationsSchema, TCMFourExaminationsCreateSchema, TCMFourExaminationsUpdateSchema, TCMTreatmentSchema, TCMTreatmentCreateSchema, TCMTreatmentUpdateSchema, TCMPrescriptionSchema, TCMPrescriptionCreateSchema, TCMPrescriptionUpdateSchema, TCMPrescriptionItemSchema, TCMPrescriptionItemCreateSchema, TCMPrescriptionItemUpdateSchema, TCMFormulaSchema, TCMFormulaCreateSchema, TCMFormulaUpdateSchema, TCMDecoctionServiceSchema, TCMDecoctionServiceCreateSchema, TCMDecoctionServiceUpdateSchema



class DiagnosisCRUD(CRUDBase[Diagnosis, DiagnosisCreateSchema, DiagnosisUpdateSchema]):
    """Diagnosis 数据层"""

    pass


class TCMDiagnosisCRUD(CRUDBase[TCMDiagnosis, TCMDiagnosisCreateSchema, TCMDiagnosisUpdateSchema]):
    """TCMDiagnosis 数据层"""

    pass


class TCMFourExaminationsCRUD(CRUDBase[TCMFourExaminations, TCMFourExaminationsCreateSchema, TCMFourExaminationsUpdateSchema]):
    """TCMFourExaminations 数据层"""

    pass


class TCMTreatmentCRUD(CRUDBase[TCMTreatment, TCMTreatmentCreateSchema, TCMTreatmentUpdateSchema]):
    """TCMTreatment 数据层"""

    pass


class TCMPrescriptionCRUD(CRUDBase[TCMPrescription, TCMPrescriptionCreateSchema, TCMPrescriptionUpdateSchema]):
    """TCMPrescription 数据层"""

    pass


class TCMPrescriptionItemCRUD(CRUDBase[TCMPrescriptionItem, TCMPrescriptionItemCreateSchema, TCMPrescriptionItemUpdateSchema]):
    """TCMPrescriptionItem 数据层"""

    pass


class TCMFormulaCRUD(CRUDBase[TCMFormula, TCMFormulaCreateSchema, TCMFormulaUpdateSchema]):
    """TCMFormula 数据层"""

    pass


class TCMDecoctionServiceCRUD(CRUDBase[TCMDecoctionService, TCMDecoctionServiceCreateSchema, TCMDecoctionServiceUpdateSchema]):
    """TCMDecoctionService 数据层"""

    pass


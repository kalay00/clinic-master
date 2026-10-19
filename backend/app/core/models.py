"""
集中导入所有 ORM 模型，确保它们被注册到 Base.metadata。

- create_all / autogenerate 都依赖 Base.metadata 包含全部表；
- 仅靠路由链导入模型不可靠（例如 module_patient 的路由只导入 controller/service，
  并不会导入 Patient 模型，导致 create_all 报 NoReferencedTableError）。
- 统一在此处导入，alembic/env.py 与 app/scripts/initialize.py 共用，避免重复维护。
"""
from app.api.v1.module_tenant.model import Tenant, UserTenant
from app.api.v1.module_platform.model import PlatformAdmin, BackupRecord
from app.api.v1.module_user.model import User
from app.api.v1.module_role.model import Role, Permission, UserRole, RolePermission
from app.api.v1.module_patient.model import Patient, PatientPhoto
from app.api.v1.module_department.model import Department
from app.api.v1.module_doctor.model import Doctor
from app.api.v1.module_registration.model import Schedule, Registration
from app.api.v1.module_treatment.model import MedicalRecord, Prescription
from app.api.v1.module_payment.model import Bill, Payment, BillItem
from app.api.v1.module_pharmacy.model import Drug, Inventory, Dispense, DrugCategory, PriceAdjustment, PriceAdjustmentItem
from app.api.v1.module_third_party_config.model import ThirdPartyConfig
from app.api.v1.module_member.model import MemberLevel, MemberTransaction
from app.api.v1.module_commission.model import CommissionPlan
from app.api.v1.module_project.model import ProjectCategory, Project, PatientProject, ProjectVerification
from app.api.v1.module_technician.model import Technician
from app.api.v1.module_treatment.model import MedicalRecord, Prescription, PrescriptionServiceItem
from app.api.v1.module_inventory.model import (
    Supplier, PurchaseOrder, PurchaseOrderItem,
    InventoryTransaction, InventoryCheck, InventoryCheckItem,
    ReturnOrder, ReturnOrderItem,
)
from app.api.v1.module_tcm.model import (
    Diagnosis, TCMDiagnosis, TCMFourExaminations, TCMTreatment,
    TCMPrescription, TCMPrescriptionItem, TCMFormula, TCMDecoctionService,
)
from app.api.v1.module_log.model import OperationLog, AuditLog
from app.api.v1.module_notification.model import Notification
from app.api.v1.module_print_template.model import PrintTemplate
from app.api.v1.module_integration.model import (
    MedicalInsuranceSettlement,
    MedicalInsuranceViolation,
    MedicalInsurancePolicy,
)

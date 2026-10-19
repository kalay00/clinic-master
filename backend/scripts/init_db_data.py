#!/usr/bin/env python3
"""
数据库初始化数据脚本
"""
import sys
from pathlib import Path

# 添加项目路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.core.database import SessionLocal, engine
# 导入所有模型以确保它们被注册到 Base.metadata（单一数据源：各 module_* 模块）
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
from app.api.v1.module_pharmacy.model import Drug, Inventory, Dispense
from app.api.v1.module_third_party_config.model import ThirdPartyConfig
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
from app.core.security import get_password_hash
from app.core.init_db import init_database

def main():
    """初始化数据库数据"""
    print("="*60)
    print("开始初始化数据库数据")
    print("="*60)
    
    # 初始化数据库（创建表、初始化数据）
    init_database()
    
    print("\n✅ 数据库初始化完成！")
    print("\n默认管理员账号:")
    print("  - 平台管理员: platform_admin / 111111")
    print("  - 租户管理员: admin / 111111")
    print("  - 租户代码: TEST001 或 TEST002")

if __name__ == "__main__":
    main()


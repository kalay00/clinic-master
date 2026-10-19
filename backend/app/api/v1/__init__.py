"""
API v1 路由（对齐 FastapiAdmin 的 module_* 结构，Python 3.12+）

新架构模块（module_*/，async + AuthSchema + SuccessResponse + CRUDBase）：
- 每个模块目录包含 controller / service / crud / model / schema / param 六类文件。
- 旧版扁平 api 文件（registrations.py / treatments.py / ...）已下线，
  其业务逻辑由对应 module_* 接管。
- auth 仍沿用旧版（登录 / 令牌 / 刷新），保持 /auth 前缀。
"""
from fastapi import APIRouter

router = APIRouter()

# 新架构模块
from app.api.v1.module_patient import router as patient_router
from app.api.v1.module_registration import router as registration_router
from app.api.v1.module_treatment import router as treatment_router
from app.api.v1.module_payment import router as payment_router, payments_router
from app.api.v1.module_pharmacy import router as pharmacy_router, category_router as drug_category_router, price_router as drug_price_router
from app.api.v1.module_inventory import router as inventory_router, purchase_router, check_router, return_router
from app.api.v1.module_member import router as member_router
from app.api.v1.module_member import member_router as member_manage_router
from app.api.v1.module_commission import router as commission_router
from app.api.v1.module_project import router as project_router
from app.api.v1.module_technician import router as technician_router
from app.api.v1.module_treatment import router as treatment_router, prescription_service_router
from app.api.v1.module_dictionary import router as dictionary_router
from app.api.v1.module_notification import router as notification_router
from app.api.v1.module_third_party_config import router as third_party_config_router
from app.api.v1.module_tenant import router as tenant_router
from app.api.v1.module_role import router as role_router
from app.api.v1.module_department import router as department_router
from app.api.v1.module_doctor import router as doctor_router
from app.api.v1.module_tcm import router as tcm_router
from app.api.v1.module_log import router as log_router
from app.api.v1.module_print_template import router as print_template_router
from app.api.v1.module_platform import router as platform_router
from app.api.v1.module_user import router as user_router
from app.api.v1.module_report import router as report_router
from app.api.v1.module_integration import router as integration_router
from app.api.v1.module_upload import router as upload_router
from app.api.v1.module_fee import router as fee_router
from app.api.v1.module_dashboard import router as dashboard_router

# 旧版（认证相关，暂保留）
from app.api.v1 import auth

router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(patient_router, prefix="/patients", tags=["患者"])
router.include_router(registration_router, prefix="/registrations", tags=["挂号"])
router.include_router(treatment_router, prefix="/treatments", tags=["诊疗"])
router.include_router(payment_router, prefix="/payments/bills", tags=["收费账单"])
router.include_router(payments_router, prefix="/payments/payments", tags=["支付记录"])
router.include_router(pharmacy_router, prefix="/pharmacy/drugs", tags=["药品"])
router.include_router(drug_category_router, prefix="/pharmacy/drug-categories", tags=["药品分类"])
router.include_router(member_router, prefix="/member/levels", tags=["会员等级"])
router.include_router(member_manage_router, prefix="/member", tags=["会员管理"])
router.include_router(commission_router, prefix="/commission/plans", tags=["提成方案"])
router.include_router(project_router, prefix="/projects", tags=["项目管理"])
router.include_router(technician_router, prefix="/technicians", tags=["技师管理"])
router.include_router(prescription_service_router, prefix="/prescriptions", tags=["处方服务项目"])
router.include_router(inventory_router, prefix="/inventory/suppliers", tags=["供应商"])
router.include_router(purchase_router, prefix="/inventory", tags=["采购单"])
router.include_router(check_router, prefix="/inventory", tags=["盘点单"])
router.include_router(return_router, prefix="/inventory", tags=["退货单"])
router.include_router(notification_router, prefix="/notifications", tags=["通知"])
router.include_router(third_party_config_router, prefix="/third-party/configs", tags=["第三方服务配置"])
router.include_router(tenant_router, prefix="/tenant", tags=["租户配置"])
router.include_router(role_router, prefix="/roles", tags=["角色"])
router.include_router(department_router, prefix="/departments", tags=["科室"])
router.include_router(doctor_router, prefix="/doctors", tags=["医生"])
router.include_router(tcm_router, prefix="/tcm", tags=["中医"])
router.include_router(log_router, prefix="/logs", tags=["操作日志"])
router.include_router(print_template_router, prefix="/print-templates", tags=["打印模板管理"])
router.include_router(platform_router, prefix="/platform", tags=["平台管理"])
router.include_router(user_router, prefix="/users", tags=["用户"])
router.include_router(report_router, prefix="/reports", tags=["报表"])
router.include_router(integration_router, prefix="/integrations", tags=["对接"])
router.include_router(upload_router, prefix="/upload", tags=["文件上传"])
router.include_router(dictionary_router, prefix="/dictionaries", tags=["通用字典"])
router.include_router(fee_router, prefix="/fees", tags=["费用设置"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["仪表盘统计"])

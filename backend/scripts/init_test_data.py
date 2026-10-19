"""
测试数据初始化脚本
初始化所有测试数据，所有用户密码设置为111111

用法（在 backend 目录下）：
    python scripts/init_test_data.py
"""
import sys
import os

# 添加 backend 项目根目录到路径（脚本位于 backend/scripts/ 下）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

# 注意：database.py 里 engine 别名指向 async_engine；inspect() 是同步操作，必须用 sync_engine
from app.core.database import SessionLocal, sync_engine as engine
from app.core.security import get_password_hash

from app.api.v1.module_tenant.model import Tenant
from app.api.v1.module_user.model import User
from app.api.v1.module_role.model import Role, Permission, UserRole, RolePermission
from app.api.v1.module_tenant.model import UserTenant
from app.api.v1.module_platform.model import PlatformAdmin
from app.api.v1.module_patient.model import Patient
from app.api.v1.module_registration.model import Schedule, Registration
from app.api.v1.module_department.model import Department
from app.api.v1.module_doctor.model import Doctor
from app.api.v1.module_treatment.model import MedicalRecord, Prescription
from app.api.v1.module_payment.model import Bill, Payment
from app.api.v1.module_pharmacy.model import Drug, DrugCategory, Inventory, Dispense
from app.api.v1.module_member.model import MemberLevel
from app.core.logger import logger


def generate_patient_no(tenant_code: str, index: int) -> str:
    """生成病历号"""
    return f"{tenant_code}P{str(index).zfill(6)}"


def generate_registration_no(tenant_code: str, index: int) -> str:
    """生成挂号单号"""
    today = datetime.now().strftime("%Y%m%d")
    return f"{tenant_code}R{today}{str(index).zfill(4)}"


def generate_prescription_no(tenant_code: str, index: int) -> str:
    """生成处方单号"""
    today = datetime.now().strftime("%Y%m%d")
    return f"{tenant_code}RX{today}{str(index).zfill(4)}"


def generate_bill_no(tenant_code: str, index: int) -> str:
    """生成账单号"""
    today = datetime.now().strftime("%Y%m%d")
    return f"{tenant_code}B{today}{str(index).zfill(4)}"


def generate_payment_no(tenant_code: str, index: int) -> str:
    """生成支付单号"""
    today = datetime.now().strftime("%Y%m%d")
    return f"{tenant_code}PY{today}{str(index).zfill(4)}"


def init_test_data():
    """初始化所有测试数据"""
    db = SessionLocal()
    
    try:
        logger.info("开始初始化测试数据...")
        
        # 1. 创建或获取租户
        logger.info("创建或获取租户数据...")
        tenant1 = db.query(Tenant).filter(Tenant.code == "TEST001").first()
        if not tenant1:
            tenant1 = Tenant(
                name="测试门诊一",
                code="TEST001",
                type="clinic",
                contact_name="张三",
                contact_phone="13800138001",
                contact_email="test1@example.com",
                address="北京市朝阳区测试路1号",
                status="active",
                subscription_plan="premium",
                domain="test001.his.example.com",  # 租户域名
            )
            db.add(tenant1)
            db.flush()
            logger.info(f"✓ 创建租户: {tenant1.name} (ID: {tenant1.id})")
        else:
            logger.info(f"✓ 租户已存在: {tenant1.name} (ID: {tenant1.id})")
        
        tenant2 = db.query(Tenant).filter(Tenant.code == "TEST002").first()
        if not tenant2:
            tenant2 = Tenant(
                name="测试门诊二",
                code="TEST002",
                type="clinic",
                contact_name="李四",
                contact_phone="13800138002",
                contact_email="test2@example.com",
                address="上海市浦东新区测试路2号",
                status="active",
                subscription_plan="standard",
                domain="test002.his.example.com",  # 租户域名
            )
            db.add(tenant2)
            db.flush()
            logger.info(f"✓ 创建租户: {tenant2.name} (ID: {tenant2.id})")
        else:
            logger.info(f"✓ 租户已存在: {tenant2.name} (ID: {tenant2.id})")
        
        # 2. 创建角色和权限
        logger.info("创建角色和权限数据...")
        
        # 权限定义：code 必须与各模块 controller.py 中 AuthPermission 要求的码完全一致。
        # 约定（全局唯一、不带租户前缀）：{resource}:{list|create|get|update|delete}
        # 说明：原实现给权限码加租户前缀（如 TEST001_treatment:view）且用 view/create/edit 动作，
        # 但路由要求无前缀的 REST 动作码（treatment:list 等），导致 AuthPermission 永远不匹配 => 403。
        # Permission.code 为全局 unique，故权限作为“系统级”定义（tenant_id=None）只创建一次，
        # 各租户角色通过 RolePermission 引用，既避免跨租户唯一冲突，也避免前缀不匹配。
        permissions_def = {
            "user": "用户",
            "patient": "患者",
            "doctor": "医生",
            "registration": "挂号",
            "treatment": "诊疗",
            "payment": "收费",
            "pharmacy": "药品",
    "drug": "药品分类",
            "report": "报表",
            "role": "角色",
            "department": "科室",
            "inventory": "进销存",
            "tcm": "中医",
            "print_template": "打印模板",
            "system": "系统",
            "member": "会员",
            "commission": "提成",
            "project": "项目",
            "technician": "技师",
            "dictionary": "字典",
            "fee": "费用设置",
            "dashboard": "仪表盘统计",
        }

        # 生成标准 CRUD 权限（action 对齐路由：list/create/get/update/delete）
        permissions_data = []
        for _res, _label in permissions_def.items():
            for _act, _act_label in (
                ("list", "列表"),
                ("create", "创建"),
                ("get", "详情"),
                ("update", "更新"),
                ("delete", "删除"),
            ):
                permissions_data.append({
                    "code": f"{_res}:{_act}",
                    "resource": _res,
                    "action": _act,
                    "name": f"{_label}{_act_label}",
                    "description": f"{_label}{_act_label}",
                })
        # 药品发药为额外业务权限
        permissions_data.append({
            "code": "pharmacy:dispense",
            "resource": "pharmacy",
            "action": "dispense",
            "name": "发药",
            "description": "处方发药",
        })
        # 仪表盘查看（首页数据），路由使用 :view 动作码（非标准 CRUD）
        permissions_data.append({
            "code": "dashboard:view",
            "resource": "dashboard",
            "action": "view",
            "name": "仪表盘查看",
            "description": "仪表盘统计查看",
        })
        
        # 系统级权限只创建一次（tenant_id=None），供各租户角色共用，code 不带租户前缀
        permissions_by_code = {}
        for perm_data in permissions_data:
            existing_perm = db.query(Permission).filter(
                Permission.code == perm_data["code"],
                Permission.deleted_at.is_(None),
            ).first()
            if existing_perm:
                logger.info(f"✓ 权限已存在: {perm_data['name']}")
                permissions_by_code[perm_data["code"]] = existing_perm
            else:
                perm = Permission(
                    tenant_id=None,
                    code=perm_data["code"],
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    name=perm_data["name"],
                    description=perm_data["description"],
                )
                db.add(perm)
                db.flush()
                logger.info(f"✓ 创建权限: {perm_data['name']}")
                permissions_by_code[perm_data["code"]] = perm
        
        # 角色列表（权限码使用上面的标准码，对齐路由 AuthPermission 要求）
        roles_data = [
            {
                "code": "admin",
                "name": "系统管理员",
                "description": "系统管理员，拥有所有权限",
                "permissions": [p["code"] for p in permissions_data],
            },
            {
                "code": "doctor",
                "name": "医生",
                "description": "医生角色，可以查看和创建病历、处方",
                "permissions": [
                    "patient:list", "patient:create", "patient:get", "patient:update",
                    "registration:list", "registration:create",
                    "treatment:list", "treatment:create", "treatment:get", "treatment:update",
                    "payment:list",
                    "dashboard:view",
                ],
            },
            {
                "code": "nurse",
                "name": "护士",
                "description": "护士角色，可以查看和创建患者、挂号",
                "permissions": [
                    "patient:list", "patient:create", "patient:get", "patient:update",
                    "registration:list", "registration:create",
                    "dashboard:view",
                ],
            },
            {
                "code": "pharmacist",
                "name": "药师",
                "description": "药师角色，可以管理药品和发药",
                "permissions": [
                    "pharmacy:list", "pharmacy:create", "pharmacy:get", "pharmacy:update",
                    "pharmacy:dispense",
                    "treatment:list", "treatment:get",
                    "dashboard:view",
                ],
            },
            {
                "code": "cashier",
                "name": "收费员",
                "description": "收费员角色，可以查看和创建账单",
                "permissions": [
                    "patient:list",
                    "registration:list",
                    "payment:list", "payment:create",
                    "dashboard:view",
                ],
            },
        ]
        
        # 为每个租户创建角色
        roles_by_tenant = {}
        for tenant in [tenant1, tenant2]:
            roles_by_tenant[tenant.id] = []
            for role_data in roles_data:
                # 检查角色是否已存在
                existing_role = db.query(Role).filter(
                    Role.code == role_data["code"],
                    Role.tenant_id == tenant.id,
                    Role.deleted_at.is_(None)
                ).first()
                
                if existing_role:
                    logger.info(f"✓ 角色已存在: {role_data['name']} (租户: {tenant.code})")
                    roles_by_tenant[tenant.id].append(existing_role)
                    role = existing_role
                else:
                    role = Role(
                        tenant_id=tenant.id,
                        code=role_data["code"],
                        name=role_data["name"],
                        description=role_data["description"],
                        is_system=True,
                    )
                    db.add(role)
                    db.flush()
                    logger.info(f"✓ 创建角色: {role_data['name']} (租户: {tenant.code})")
                
                # 分配权限（按标准码从系统级权限字典中查找，无需租户前缀）
                for perm_code in role_data["permissions"]:
                    perm = permissions_by_code.get(perm_code)
                    if not perm:
                        logger.warning(f"⚠ 角色 {role_data['name']} 的权限码未在权限表中定义: {perm_code}")
                        continue
                    # 检查角色权限关联是否已存在
                    existing_role_perm = db.query(RolePermission).filter(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm.id
                    ).first()

                    if not existing_role_perm:
                        role_perm = RolePermission(
                            role_id=role.id,
                            permission_id=perm.id,
                        )
                        db.add(role_perm)
                        logger.debug(f"✓ 为角色 {role_data['name']} 分配权限: {perm.name} ({perm_code})")
                    else:
                        logger.debug(f"✓ 角色 {role_data['name']} 已拥有权限: {perm.name} ({perm_code})")
                
                roles_by_tenant[tenant.id].append(role)
        
        logger.info("✓ 角色和权限创建完成")
        
        # 3. 创建用户（所有密码都是111111）
        logger.info("创建用户数据...")
        password_hash = get_password_hash("111111")
        
        users_data = [
            {
                "username": "admin",
                "real_name": "系统管理员",
                "phone": "13800000001",
                "email": "admin@example.com",
                "roles": ["admin"],
            },
            {
                "username": "doctor1",
                "real_name": "张医生",
                "phone": "13800000002",
                "email": "doctor1@example.com",
                "roles": ["doctor"],
            },
            {
                "username": "doctor2",
                "real_name": "李医生",
                "phone": "13800000003",
                "email": "doctor2@example.com",
                "roles": ["doctor"],
            },
            {
                "username": "nurse1",
                "real_name": "王护士",
                "phone": "13800000004",
                "email": "nurse1@example.com",
                "roles": ["nurse"],
            },
            {
                "username": "pharmacist1",
                "real_name": "赵药师",
                "phone": "13800000005",
                "email": "pharmacist1@example.com",
                "roles": ["pharmacist"],
            },
            {
                "username": "cashier1",
                "real_name": "钱收费员",
                "phone": "13800000006",
                "email": "cashier1@example.com",
                "roles": ["cashier"],
            },
        ]
        
        users_by_tenant = {}
        for tenant in [tenant1, tenant2]:
            users_by_tenant[tenant.id] = []
            for user_data in users_data:
                username = f"{user_data['username']}{tenant.code[-1]}"  # 区分不同租户
                # 检查用户是否已存在
                existing_user = db.query(User).filter(
                    User.username == username,
                    User.tenant_id == tenant.id,
                    User.deleted_at.is_(None)
                ).first()
                
                if existing_user:
                    logger.info(f"✓ 用户已存在: {username} (租户: {tenant.code})")
                    users_by_tenant[tenant.id].append(existing_user)
                    continue
                
                user = User(
                    tenant_id=tenant.id,
                    username=username,
                    password_hash=password_hash,
                    real_name=user_data["real_name"],
                    phone=user_data["phone"],
                    email=user_data["email"],
                    status="active",
                )
                db.add(user)
                db.flush()
                
                # 分配角色
                for role_code in user_data["roles"]:
                    role = next(
                        (r for r in roles_by_tenant[tenant.id] if r.code == role_code),
                        None
                    )
                    if role:
                        # 检查角色是否已分配
                        existing_user_role = db.query(UserRole).filter(
                            UserRole.user_id == user.id,
                            UserRole.role_id == role.id
                        ).first()
                        if not existing_user_role:
                            user_role = UserRole(
                                user_id=user.id,
                                role_id=role.id,
                            )
                            db.add(user_role)
                
                users_by_tenant[tenant.id].append(user)
        
        logger.info(f"✓ 为每个租户创建了 {len(users_data)} 个用户")
        
        # 3.5 创建平台管理员
        logger.info("创建平台管理员...")
        existing_platform_admin = db.query(PlatformAdmin).filter(
            PlatformAdmin.username == "platform_admin",
            PlatformAdmin.deleted_at.is_(None)
        ).first()
        
        if existing_platform_admin:
            logger.info(f"✓ 平台管理员已存在: {existing_platform_admin.username}")
        else:
            platform_admin = PlatformAdmin(
                username="platform_admin",
                password_hash=get_password_hash("111111"),
                real_name="平台管理员",
                email="platform@his.example.com",
                status="active",
            )
            db.add(platform_admin)
            db.flush()
            logger.info(f"✓ 创建平台管理员: {platform_admin.username} (密码: 111111)")
        
        # 3.6 创建用户多租户关联（创建一个用户属于两个租户）
        # 注意：如果user_tenants表不存在，跳过此步骤
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            if 'user_tenants' in inspector.get_table_names():
                logger.info("创建用户多租户关联...")
                # 选择租户1的第一个管理员用户
                multi_tenant_user = users_by_tenant[tenant1.id][0]
                
                # 检查关联是否已存在
                existing_user_tenant1 = db.query(UserTenant).filter(
                    UserTenant.user_id == multi_tenant_user.id,
                    UserTenant.tenant_id == tenant1.id
                ).first()
                
                if not existing_user_tenant1:
                    # 创建用户与租户1的关联（主要租户）
                    user_tenant1 = UserTenant(
                        user_id=multi_tenant_user.id,
                        tenant_id=tenant1.id,
                        is_primary=True,
                    )
                    db.add(user_tenant1)
                
                existing_user_tenant2 = db.query(UserTenant).filter(
                    UserTenant.user_id == multi_tenant_user.id,
                    UserTenant.tenant_id == tenant2.id
                ).first()
                
                if not existing_user_tenant2:
                    # 创建用户与租户2的关联（次要租户）
                    user_tenant2 = UserTenant(
                        user_id=multi_tenant_user.id,
                        tenant_id=tenant2.id,
                        is_primary=False,
                    )
                    db.add(user_tenant2)
                
                db.flush()
                logger.info(f"✓ 用户 {multi_tenant_user.username} 现在属于两个租户")
                logger.info(f"  - 主要租户: {tenant1.name} ({tenant1.code})")
                logger.info(f"  - 次要租户: {tenant2.name} ({tenant2.code})")
            else:
                logger.info("跳过用户多租户关联（user_tenants表不存在）")
        except Exception as e:
            logger.warning(f"跳过用户多租户关联: {str(e)}")
        
        # 先提交用户数据，确保用户已创建
        db.commit()
        logger.info("✓ 用户数据已提交")
        
        # 4. 创建患者数据（如果表存在）
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            if 'patients' not in inspector.get_table_names():
                logger.warning("跳过患者数据创建（patients表不存在）")
                patients_by_tenant = {}
            else:
                logger.info("创建患者数据...")
                patients_data = [
                    {
                        "name": "王小明",
                        "id_card": "110101199001011234",
                        "gender": "M",
                        "birthday": date(1990, 1, 1),
                        "phone": "13810001001",
                        "address": "北京市朝阳区测试街1号",
                    },
                    {
                        "name": "李小红",
                        "id_card": "110101199002021235",
                        "gender": "F",
                        "birthday": date(1990, 2, 2),
                        "phone": "13810001002",
                        "address": "北京市海淀区测试街2号",
                    },
                    {
                        "name": "张大明",
                        "id_card": "110101198503031236",
                        "gender": "M",
                        "birthday": date(1985, 3, 3),
                        "phone": "13810001003",
                        "address": "北京市西城区测试街3号",
                    },
                    {
                        "name": "赵小芳",
                        "id_card": "110101199504041237",
                        "gender": "F",
                        "birthday": date(1995, 4, 4),
                        "phone": "13810001004",
                        "address": "北京市东城区测试街4号",
                    },
                    {
                        "name": "刘小华",
                        "id_card": "110101199505051238",
                        "gender": "M",
                        "birthday": date(1995, 5, 5),
                        "phone": "13810001005",
                        "address": "北京市丰台区测试街5号",
                    },
                ]
                
                patients_by_tenant = {}
                for idx, tenant in enumerate([tenant1, tenant2]):
                    patients_by_tenant[tenant.id] = []
                    for i, patient_data in enumerate(patients_data):
                        # 检查患者是否已存在（按租户+身份证哈希唯一约束），避免重复启动重复插入
                        existing_patient = db.query(Patient).filter(
                            Patient.tenant_id == tenant.id,
                            Patient.id_card == patient_data["id_card"],
                            Patient.deleted_at.is_(None),
                        ).first()
                        if existing_patient:
                            logger.info(f"✓ 患者已存在: {patient_data['name']} (租户: {tenant.code})")
                            patients_by_tenant[tenant.id].append(existing_patient)
                            continue
                        patient = Patient(
                            tenant_id=tenant.id,
                            patient_no=generate_patient_no(tenant.code, i + 1),
                            name=patient_data["name"],
                            id_card=patient_data["id_card"],
                            gender=patient_data["gender"],
                            birthday=patient_data["birthday"],
                            phone=patient_data["phone"],
                            address=patient_data["address"],
                        )
                        db.add(patient)
                        db.flush()
                        patients_by_tenant[tenant.id].append(patient)
                
                logger.info(f"✓ 为每个租户创建了 {len(patients_data)} 个患者")
        except Exception as e:
            logger.warning(f"跳过患者数据创建: {str(e)}")
            patients_by_tenant = {}

        # 4.2 创建会员等级（默认普通会员 + 示例等级）
        try:
            levels_by_tenant = {}
            for tenant in [tenant1, tenant2]:
                levels_by_tenant[tenant.id] = []
                levels_data = [
                    {"name": "普通会员", "discount_rate": 1.0, "upgrade_threshold": 0, "sort": 0, "is_default": True},
                    {"name": "银卡会员", "discount_rate": 0.95, "upgrade_threshold": 2000, "sort": 1, "is_default": False},
                    {"name": "金卡会员", "discount_rate": 0.90, "upgrade_threshold": 5000, "sort": 2, "is_default": False},
                ]
                default_level = None
                for ld in levels_data:
                    existing = db.query(MemberLevel).filter(
                        MemberLevel.tenant_id == tenant.id,
                        MemberLevel.name == ld["name"],
                        MemberLevel.deleted_at.is_(None),
                    ).first()
                    if existing:
                        levels_by_tenant[tenant.id].append(existing)
                        if existing.is_default:
                            default_level = existing
                        continue
                    lvl = MemberLevel(
                        tenant_id=tenant.id,
                        name=ld["name"],
                        discount_rate=ld["discount_rate"],
                        upgrade_threshold=ld["upgrade_threshold"],
                        sort=ld["sort"],
                        is_default=ld["is_default"],
                        status="active",
                    )
                    db.add(lvl)
                    db.flush()
                    levels_by_tenant[tenant.id].append(lvl)
                    if ld["is_default"]:
                        default_level = lvl
                # 给该租户下未设置等级的患者默认归属普通会员
                if default_level:
                    db.query(Patient).filter(
                        Patient.tenant_id == tenant.id,
                        Patient.member_level_id.is_(None),
                        Patient.deleted_at.is_(None),
                    ).update({Patient.member_level_id: str(default_level.id), Patient.consumption_total: 0})
            logger.info("✓ 会员等级初始化完成")
        except Exception as e:
            logger.warning(f"跳过会员等级数据创建: {str(e)}")
        
        # 4.5 创建科室与医生数据（如果表存在）
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            if "departments" not in inspector.get_table_names() or "doctors" not in inspector.get_table_names():
                logger.warning("跳过科室/医生数据创建（departments 或 doctors 表不存在）")
            else:
                logger.info("创建科室与医生数据...")

                # 科室定义（每个租户都会创建一份）
                departments_data = [
                    {"code": "INTERNAL", "name": "内科", "description": "心血管、呼吸、消化等内科疾病诊治", "sort_order": 1},
                    {"code": "SURGERY", "name": "外科", "description": "普外、骨科、泌尿等外科疾病诊治", "sort_order": 2},
                    {"code": "PEDIATRICS", "name": "儿科", "description": "儿童常见病、多发病诊治", "sort_order": 3},
                    {"code": "GYNECOLOGY", "name": "妇产科", "description": "妇科疾病与孕产保健", "sort_order": 4},
                    {"code": "STOMATOLOGY", "name": "口腔科", "description": "口腔疾病诊治与牙齿保健", "sort_order": 5},
                    {"code": "OPHTHALMOLOGY", "name": "眼科", "description": "眼部疾病诊治", "sort_order": 6},
                    {"code": "DERMATOLOGY", "name": "皮肤科", "description": "皮肤疾病诊治", "sort_order": 7},
                    {"code": "TCM", "name": "中医科", "description": "中医辨证施治与针灸推拿", "sort_order": 8},
                ]

                # 医生定义：user_ref 关联 users_data 的 username（带租户后缀）；
                # department 关联 departments_data 的 code。
                doctors_data = [
                    {"user_ref": "doctor1", "name": "张医生", "employee_no": "D001", "department": "INTERNAL",
                     "title": "主任医师", "specialty": "心血管内科", "registration_fee": "10.00",
                     "phone": "13800000002", "email": "doctor1@example.com", "bio": "擅长高血压、冠心病诊治"},
                    {"user_ref": "doctor2", "name": "李医生", "employee_no": "D002", "department": "SURGERY",
                     "title": "副主任医师", "specialty": "普外科", "registration_fee": "15.00",
                     "phone": "13800000003", "email": "doctor2@example.com", "bio": "擅长微创手术"},
                    {"user_ref": None, "name": "王医生", "employee_no": "D003", "department": "PEDIATRICS",
                     "title": "主治医师", "specialty": "小儿呼吸", "registration_fee": "12.00",
                     "phone": "13800000007", "email": "doctor3@example.com", "bio": "擅长小儿呼吸道感染"},
                    {"user_ref": None, "name": "赵医生", "employee_no": "D004", "department": "GYNECOLOGY",
                     "title": "主治医师", "specialty": "妇科内分泌", "registration_fee": "12.00",
                     "phone": "13800000008", "email": "doctor4@example.com", "bio": "擅长月经不调诊治"},
                    {"user_ref": None, "name": "刘医生", "employee_no": "D005", "department": "TCM",
                     "title": "主任医师", "specialty": "中医内科", "registration_fee": "20.00",
                     "phone": "13800000009", "email": "doctor5@example.com", "bio": "擅长脾胃病中医调理"},
                    {"user_ref": None, "name": "陈医生", "employee_no": "D006", "department": "OPHTHALMOLOGY",
                     "title": "主治医师", "specialty": "白内障", "registration_fee": "15.00",
                     "phone": "13800000010", "email": "doctor6@example.com", "bio": "擅长白内障超声乳化"},
                ]

                departments_by_tenant = {}
                for tenant in [tenant1, tenant2]:
                    departments_by_tenant[tenant.id] = {}
                    for dep_data in departments_data:
                        existing_dep = db.query(Department).filter(
                            Department.tenant_id == tenant.id,
                            Department.code == dep_data["code"],
                            Department.deleted_at.is_(None),
                        ).first()
                        if existing_dep:
                            logger.info(f"✓ 科室已存在: {dep_data['name']} (租户: {tenant.code})")
                            departments_by_tenant[tenant.id][dep_data["code"]] = existing_dep
                            continue
                        dep = Department(
                            tenant_id=tenant.id,
                            name=dep_data["name"],
                            code=dep_data["code"],
                            description=dep_data["description"],
                            status="active",
                            sort_order=dep_data["sort_order"],
                        )
                        db.add(dep)
                        db.flush()
                        departments_by_tenant[tenant.id][dep_data["code"]] = dep
                        logger.info(f"✓ 创建科室: {dep_data['name']} (租户: {tenant.code})")

                # 医生需要 users_by_tenant 中的用户对象来关联 user_id
                user_map_by_tenant = {}
                for tenant in [tenant1, tenant2]:
                    user_map_by_tenant[tenant.id] = {}
                    for u in users_by_tenant.get(tenant.id, []):
                        user_map_by_tenant[tenant.id][u.username] = u

                for tenant in [tenant1, tenant2]:
                    for doc_data in doctors_data:
                        employee_no = f"{doc_data['employee_no']}{tenant.code[-1]}"
                        existing_doc = db.query(Doctor).filter(
                            Doctor.tenant_id == tenant.id,
                            Doctor.employee_no == employee_no,
                            Doctor.deleted_at.is_(None),
                        ).first()
                        if existing_doc:
                            logger.info(f"✓ 医生已存在: {doc_data['name']} (租户: {tenant.code})")
                            continue
                        dep = departments_by_tenant[tenant.id].get(doc_data["department"])
                        user = None
                        if doc_data["user_ref"]:
                            user = user_map_by_tenant[tenant.id].get(
                                f"{doc_data['user_ref']}{tenant.code[-1]}"
                            )
                        doc = Doctor(
                            tenant_id=tenant.id,
                            user_id=user.id if user else None,
                            name=doc_data["name"],
                            employee_no=employee_no,
                            department_id=dep.id if dep else None,
                            title=doc_data["title"],
                            specialty=doc_data["specialty"],
                            phone=doc_data["phone"],
                            email=doc_data["email"],
                            registration_fee=doc_data["registration_fee"],
                            bio=doc_data["bio"],
                            status="active",
                        )
                        db.add(doc)
                        logger.info(f"✓ 创建医生: {doc_data['name']} (租户: {tenant.code}, 科室: {dep.name if dep else '无'})")

                # 生成示例排班：未来一周（含今天往前一天以覆盖前端默认查询区间），
                # 每个医生每天上午/下午各一条，便于排班页直接展示。
                slot_defs = [
                    ("morning", time(8, 0), time(12, 0)),
                    ("afternoon", time(13, 30), time(17, 30)),
                ]
                for tenant in [tenant1, tenant2]:
                    docs = db.query(Doctor).filter(
                        Doctor.tenant_id == tenant.id,
                        Doctor.deleted_at.is_(None),
                    ).all()
                    for d in docs:
                        base_fee = float(d.registration_fee) if d.registration_fee else 0.0
                        for day_offset in range(-1, 8):
                            sched_date = date.today() + timedelta(days=day_offset)
                            for slot, st, et in slot_defs:
                                exists = db.query(Schedule).filter(
                                    Schedule.doctor_id == d.id,
                                    Schedule.schedule_date == sched_date,
                                    Schedule.time_slot == slot,
                                    Schedule.deleted_at.is_(None),
                                ).first()
                                if exists:
                                    continue
                                sched = Schedule(
                                    tenant_id=tenant.id,
                                    doctor_id=d.id,
                                    department_id=d.department_id,
                                    schedule_date=sched_date,
                                    time_slot=slot,
                                    start_time=st,
                                    end_time=et,
                                    total_quota=30,
                                    used_quota=0,
                                    price=base_fee,
                                    status="active",
                                )
                                db.add(sched)
                        logger.info(f"✓ 为医生 {d.name} (租户: {tenant.code}) 生成示例排班")

                logger.info("✓ 科室与医生数据创建完成")
        except Exception as e:
            logger.warning(f"跳过科室/医生数据创建: {str(e)}")

        # 5. 创建药品数据（如果表存在）
        drug_categories_by_tenant = {}
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            if 'drugs' not in inspector.get_table_names():
                logger.warning("跳过药品数据创建（drugs表不存在）")
                drugs_by_tenant = {}
            else:
                logger.info("创建药品数据...")

                # 5.1 创建药品分类（字典维护-药品分类页数据源：/pharmacy/drug-categories，按租户隔离，幂等）
                drug_categories_by_tenant = {}
                try:
                    if 'drug_categories' in inspector.get_table_names():
                        logger.info("创建药品分类...")
                        drug_categories_data = [
                            {"name": "西药", "category_type": "western", "sort": 1, "remark": "抗生素、解热镇痛等化学药品"},
                            {"name": "中成药", "category_type": "chinese_patent", "sort": 2, "remark": "中药成方制剂"},
                            {"name": "中药", "category_type": "herb", "sort": 3, "remark": "中药材/草药"},
                        ]
                        for tenant in [tenant1, tenant2]:
                            _users = users_by_tenant.get(tenant.id) or []
                            admin_id = _users[0].id if _users else None
                            drug_categories_by_tenant[tenant.id] = {}
                            for cat_data in drug_categories_data:
                                existing_cat = db.query(DrugCategory).filter(
                                    DrugCategory.tenant_id == tenant.id,
                                    DrugCategory.name == cat_data["name"],
                                    DrugCategory.deleted_at.is_(None),
                                ).first()
                                if existing_cat:
                                    drug_categories_by_tenant[tenant.id][cat_data["name"]] = existing_cat.id
                                    continue
                                cat = DrugCategory(
                                    tenant_id=tenant.id,
                                    name=cat_data["name"],
                                    category_type=cat_data["category_type"],
                                    sort=cat_data["sort"],
                                    remark=cat_data["remark"],
                                    status="active",
                                    created_by=admin_id,
                                )
                                db.add(cat)
                                db.flush()
                                drug_categories_by_tenant[tenant.id][cat_data["name"]] = cat.id
                            logger.info(f"✓ 药品分类创建完成 (租户: {tenant.code})")
                except Exception as e:
                    logger.warning(f"跳过药品分类创建: {str(e)}")
                    drug_categories_by_tenant = {}

                # 注意：这里需要医生和科室，但我们先创建占位符
                # 实际系统中应该有医生和科室表，这里先跳过外键约束
                
                drugs_data = [
            # 西药
            {"code": "W001", "name": "阿莫西林胶囊", "generic_name": "阿莫西林", "specification": "0.25g*24粒", "unit": "盒", "category": "西药", "manufacturer": "华北制药", "price": 25.50},
            {"code": "W002", "name": "布洛芬缓释胶囊", "generic_name": "布洛芬", "specification": "0.3g*20粒", "unit": "盒", "category": "西药", "manufacturer": "中美天津史克", "price": 18.80},
            {"code": "W003", "name": "头孢克肟片", "generic_name": "头孢克肟", "specification": "0.1g*12片", "unit": "盒", "category": "西药", "manufacturer": "白云山制药", "price": 32.00},
            # 中药
            {"code": "T001", "name": "板蓝根颗粒", "generic_name": "板蓝根", "specification": "10g*20袋", "unit": "盒", "category": "中药", "manufacturer": "同仁堂", "price": 15.60},
            {"code": "T002", "name": "感冒清热颗粒", "generic_name": "感冒清热", "specification": "12g*10袋", "unit": "盒", "category": "中药", "manufacturer": "太极集团", "price": 22.50},
            {"code": "T003", "name": "复方甘草片", "generic_name": "复方甘草", "specification": "50片", "unit": "瓶", "category": "中药", "manufacturer": "哈药集团", "price": 8.90},
            # 中成药
            {"code": "C001", "name": "六味地黄丸", "generic_name": "六味地黄", "specification": "9g*10丸", "unit": "盒", "category": "中成药", "manufacturer": "同仁堂", "price": 28.00},
                    {"code": "C002", "name": "逍遥丸", "generic_name": "逍遥", "specification": "9g*10丸", "unit": "盒", "category": "中成药", "manufacturer": "太极集团", "price": 19.80},
                ]
                
                drugs_by_tenant = {}
                for tenant in [tenant1, tenant2]:
                    drugs_by_tenant[tenant.id] = []
                    category_ids = drug_categories_by_tenant.get(tenant.id, {})
                    for drug_data in drugs_data:
                        # 关联药品分类（保留旧分类名字段兼容前端回退）
                        category_id = category_ids.get(drug_data["category"])
                        # 检查药品是否已存在（按租户+药品编码），避免重复启动重复插入
                        existing_drug = db.query(Drug).filter(
                            Drug.tenant_id == tenant.id,
                            Drug.drug_code == drug_data["code"],
                            Drug.deleted_at.is_(None),
                        ).first()
                        if existing_drug:
                            logger.info(f"✓ 药品已存在: {drug_data['name']} (租户: {tenant.code})")
                            # 幂等：为历史数据（只有旧分类名）补充分类关联
                            if existing_drug.category_id is None and category_id is not None:
                                existing_drug.category_id = category_id
                                db.flush()
                            drugs_by_tenant[tenant.id].append(existing_drug)
                            continue
                        drug = Drug(
                            tenant_id=tenant.id,
                            drug_code=drug_data["code"],
                            name=drug_data["name"],
                            generic_name=drug_data["generic_name"],
                            specification=drug_data["specification"],
                            unit=drug_data["unit"],
                            category=drug_data["category"],
                            category_id=category_id,
                            manufacturer=drug_data["manufacturer"],
                            price=drug_data["price"],
                            status="active",
                        )
                        db.add(drug)
                        db.flush()
                        drugs_by_tenant[tenant.id].append(drug)
                        
                        # 创建库存
                        inventory = Inventory(
                            tenant_id=tenant.id,
                            drug_id=drug.id,
                            quantity=100,
                            min_quantity=10,
                            max_quantity=500,
                            unit_price=drug_data["price"],
                            batch_no=f"BATCH{datetime.now().strftime('%Y%m%d')}",
                            expiry_date=(datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
                        )
                        db.add(inventory)
                
                logger.info(f"✓ 为每个租户创建了 {len(drugs_data)} 个药品")
        except Exception as e:
            logger.warning(f"跳过药品数据创建: {str(e)}")
            drugs_by_tenant = {}
        
        # 5.5 创建字典种子数据（病历/药品用法/检查项目/患者来源等）
        try:
            from app.api.v1.module_dictionary.model import Dictionary
            from sqlalchemy import inspect as _inspect
            _insp = _inspect(engine)
            if 'dictionaries' in _insp.get_table_names():
                logger.info("创建字典种子数据...")
                dict_seed = {
                    "medical_record": {
                        "diagnosis": ["上呼吸道感染", "急性支气管炎", "高血压病", "2型糖尿病", "慢性胃炎"],
                        "doctor_advice": ["多饮水注意休息", "清淡饮食", "按时服药", "定期复查", "不适随诊"],
                        "chief_complaint": ["发热咳嗽3天", "头痛头晕1周", "腹痛腹泻2天", "胸闷气短1天"],
                        "present_illness": ["患者于3天前无明显诱因出现发热", "既往体健，否认药物过敏史"],
                        "past_history": ["高血压病史5年", "糖尿病病史3年", "否认手术史"],
                        "allergy_history": ["青霉素过敏", "头孢类过敏", "否认药物过敏"],
                        "personal_history": ["吸烟20年", "偶有饮酒", "否认疫区接触史"],
                        "auxiliary_exam": ["血常规", "胸部CT", "心电图", "腹部B超"],
                        "treatment_opinion": ["门诊治疗", "留观", "收入院进一步诊治"],
                    },
                    "drug": {
                        "drug_usage": ["口服", "外用", "肌肉注射", "静脉滴注", "雾化吸入"],
                        "drug_frequency": ["每日一次", "每日两次", "每日三次", "睡前一次", "必要时"],
                        "drug_unit": ["盒", "瓶", "袋", "支", "片"],
                    },
                    "inspection": {
                        "inspection_item": ["血常规", "尿常规", "肝功能", "肾功能", "血脂"],
                        "inspection_part": ["胸部", "腹部", "头部", "腰椎", "膝关节"],
                    },
                    "patient": {
                        "patient_source": ["门诊", "急诊", "转诊", "体检", "网络预约"],
                        "patient_type": ["初诊", "复诊", "急诊", "慢性病", "特殊人群"],
                    },
                }
                for tenant in [tenant1, tenant2]:
                    admin_id = users_by_tenant[tenant.id][0].id
                    sort_counter = {}
                    for category, subs in dict_seed.items():
                        for sub_type, items in subs.items():
                            for content in items:
                                key = f"{category}:{sub_type}:{content}"
                                existing = db.query(Dictionary).filter(
                                    Dictionary.tenant_id == tenant.id,
                                    Dictionary.category == category,
                                    Dictionary.sub_type == sub_type,
                                    Dictionary.content == content,
                                    Dictionary.deleted_at.is_(None),
                                ).first()
                                if existing:
                                    continue
                                sort_counter[key] = sort_counter.get(key, 0) + 1
                                db.add(Dictionary(
                                    tenant_id=tenant.id,
                                    created_by=admin_id,
                                    category=category,
                                    sub_type=sub_type,
                                    content=content,
                                    sort=sort_counter[key],
                                    status="active",
                                ))
                    logger.info("✓ 字典种子数据创建完成")
        except Exception as e:
            logger.warning(f"跳过字典种子数据创建: {str(e)}")

        # 5.6 创建费用设置数据（系统设置-费用设置：挂号费/治疗费/附加费/其它，按租户隔离，幂等）
        try:
            from app.api.v1.module_fee.model import Fee
            from sqlalchemy import inspect as _inspect_fee
            if 'fees' in _inspect_fee(engine).get_table_names():
                logger.info("创建费用设置数据...")
                fees_data = [
                    # 挂号费
                    {"fee_type": "registration", "name": "普通挂号", "code": "GH001", "amount": 10.00, "cost_price": 0, "unit": "次", "remark": "普通门诊挂号"},
                    {"fee_type": "registration", "name": "专家挂号", "code": "GH002", "amount": 20.00, "cost_price": 0, "unit": "次", "remark": "专家/主任医师门诊挂号"},
                    {"fee_type": "registration", "name": "急诊挂号", "code": "GH003", "amount": 30.00, "cost_price": 0, "unit": "次", "remark": "急诊挂号"},
                    # 治疗费
                    {"fee_type": "treatment", "name": "针灸治疗", "code": "ZL001", "amount": 50.00, "cost_price": 10.00, "unit": "次", "remark": "针灸治疗费"},
                    {"fee_type": "treatment", "name": "推拿治疗", "code": "ZL002", "amount": 60.00, "cost_price": 12.00, "unit": "次", "remark": "推拿治疗费"},
                    {"fee_type": "treatment", "name": "拔罐治疗", "code": "ZL003", "amount": 30.00, "cost_price": 6.00, "unit": "次", "remark": "拔罐治疗费"},
                    {"fee_type": "treatment", "name": "艾灸治疗", "code": "ZL004", "amount": 40.00, "cost_price": 8.00, "unit": "次", "remark": "艾灸治疗费"},
                    # 附加费
                    {"fee_type": "extra", "name": "材料费", "code": "FJ001", "amount": 5.00, "cost_price": 2.00, "unit": "项", "remark": "一次性材料费"},
                    {"fee_type": "extra", "name": "治疗室使用费", "code": "FJ002", "amount": 10.00, "cost_price": 0, "unit": "次", "remark": "治疗室使用费"},
                    {"fee_type": "extra", "name": "煎药费", "code": "FJ003", "amount": 8.00, "cost_price": 3.00, "unit": "付", "remark": "代煎中药服务费"},
                    # 其它
                    {"fee_type": "other", "name": "诊疗费", "code": "QT001", "amount": 15.00, "cost_price": 0, "unit": "次", "remark": "医生诊疗服务费"},
                    {"fee_type": "other", "name": "检查费", "code": "QT002", "amount": 20.00, "cost_price": 0, "unit": "项", "remark": "常规检查费"},
                    {"fee_type": "other", "name": "化验费", "code": "QT003", "amount": 25.00, "cost_price": 0, "unit": "项", "remark": "常规化验费"},
                ]
                for tenant in [tenant1, tenant2]:
                    _users = users_by_tenant.get(tenant.id) or []
                    admin_id = _users[0].id if _users else None
                    sort_counter = 0
                    for fee_data in fees_data:
                        existing_fee = db.query(Fee).filter(
                            Fee.tenant_id == tenant.id,
                            Fee.fee_type == fee_data["fee_type"],
                            Fee.name == fee_data["name"],
                            Fee.deleted_at.is_(None),
                        ).first()
                        if existing_fee:
                            continue
                        sort_counter += 1
                        db.add(Fee(
                            tenant_id=tenant.id,
                            fee_type=fee_data["fee_type"],
                            name=fee_data["name"],
                            code=fee_data["code"],
                            amount=fee_data["amount"],
                            cost_price=fee_data["cost_price"],
                            unit=fee_data["unit"],
                            sort=sort_counter,
                            status=True,
                            remark=fee_data["remark"],
                            created_by=admin_id,
                        ))
                    logger.info(f"✓ 费用设置数据创建完成 (租户: {tenant.code})")
        except Exception as e:
            logger.warning(f"跳过费用设置数据创建: {str(e)}")

        # 设置租户默认配置
        logger.info("设置租户默认配置...")
        from app.services.tenant_service import TenantService
        tenant_service = TenantService(db)
        
        # 为每个租户设置默认配置（药师审核开启）
        for tenant in [tenant1, tenant2]:
            tenant_service.update_tenant_config(
                tenant_id=str(tenant.id),
                config_updates={"pharmacist_review_enabled": True},
                updater_id=str(users_by_tenant[tenant.id][0].id)  # 使用管理员ID
            )
        
        logger.info("✓ 租户配置设置完成")
        
        # 提交所有数据
        db.commit()
        logger.info("✓ 所有测试数据初始化完成！")
        
        # 打印摘要
        print("\n" + "="*60)
        print("测试数据初始化摘要")
        print("="*60)
        print(f"租户数量: 2")
        print(f"  - {tenant1.name} (代码: {tenant1.code})")
        print(f"  - {tenant2.name} (代码: {tenant2.code})")
        print(f"\n每个租户的用户数量: {len(users_data)}")
        print("  所有用户密码: 111111")
        print("  用户列表:")
        for user_data in users_data:
            print(f"    - {user_data['username']}1 (租户1) / {user_data['username']}2 (租户2)")
        print(f"\n平台管理员:")
        print(f"  - platform_admin (密码: 111111)")
        print(f"\n多租户用户:")
        print(f"  - admin1 属于两个租户（TEST001和TEST002）")
        patients_count = len(patients_by_tenant.get(tenant1.id, [])) if patients_by_tenant else 0
        drugs_count = len(drugs_by_tenant.get(tenant1.id, [])) if drugs_by_tenant else 0
        print(f"\n每个租户的患者数量: {patients_count}")
        print(f"每个租户的药品数量: {drugs_count}")
        drug_categories_count = len(drug_categories_by_tenant.get(tenant1.id, {})) if drug_categories_by_tenant else 0
        print(f"每个租户的药品分类数量: {drug_categories_count} (西药/中成药/中药，可在字典维护-药品分类中查看)")
        try:
            from app.api.v1.module_fee.model import Fee
            fees_count = db.query(Fee).filter(
                Fee.tenant_id == tenant1.id,
                Fee.deleted_at.is_(None),
            ).count()
        except Exception:
            fees_count = 0
        print(f"每个租户的费用设置数量: {fees_count} (挂号费/治疗费/附加费/其它，可在系统设置-费用设置中查看)")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        logger.error(f"初始化测试数据失败: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_test_data()


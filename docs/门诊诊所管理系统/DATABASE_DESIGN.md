# 数据库设计文档

## 一、设计原则

### 1.1 多租户设计
- **策略**: 行级隔离（Row-level Security）
- **实现**: 所有业务表包含`tenant_id`字段
- **索引**: `tenant_id` + 业务字段建立联合索引

### 1.2 命名规范
- **表名**: 小写+下划线，复数形式，如`patients`、`medical_records`
- **字段名**: 小写+下划线，如`patient_name`、`created_at`
- **主键**: 统一使用UUID（`id`字段）
- **外键**: `{table}_id`格式，如`patient_id`、`doctor_id`

### 1.3 通用字段
所有业务表包含以下字段：
- `id`: UUID主键
- `tenant_id`: UUID，租户ID（多租户隔离）
- `created_at`: TIMESTAMP，创建时间
- `updated_at`: TIMESTAMP，更新时间
- `deleted_at`: TIMESTAMP，删除时间（软删除，可为NULL）
- `created_by`: UUID，创建人ID
- `updated_by`: UUID，更新人ID

## 二、核心表设计

### 2.1 租户管理表

#### 2.1.1 tenants（租户表）
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,                    -- 机构名称
    code VARCHAR(50) UNIQUE NOT NULL,              -- 机构编码
    type VARCHAR(20) NOT NULL,                     -- 机构类型：clinic/hospital
    contact_name VARCHAR(50),                      -- 联系人
    contact_phone VARCHAR(20),                     -- 联系电话
    contact_email VARCHAR(100),                    -- 联系邮箱
    address TEXT,                                  -- 地址
    status VARCHAR(20) DEFAULT 'active',          -- 状态：active/inactive
    subscription_plan VARCHAR(20),                 -- 订阅计划
    expires_at TIMESTAMP,                          -- 到期时间
    config JSONB,                                  -- 配置信息（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tenants_code ON tenants(code);
CREATE INDEX idx_tenants_status ON tenants(status);
```

### 2.2 用户权限表

#### 2.2.1 users（用户表）
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    username VARCHAR(50) NOT NULL,                 -- 用户名
    password_hash VARCHAR(255) NOT NULL,           -- 密码哈希
    real_name VARCHAR(50),                         -- 真实姓名
    phone VARCHAR(20),                             -- 手机号（加密）
    email VARCHAR(100),                            -- 邮箱
    avatar_url VARCHAR(255),                       -- 头像URL
    status VARCHAR(20) DEFAULT 'active',          -- 状态：active/inactive/locked
    last_login_at TIMESTAMP,                       -- 最后登录时间
    last_login_ip VARCHAR(50),                     -- 最后登录IP
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, username)
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
```

#### 2.2.2 roles（角色表）
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(50) NOT NULL,                     -- 角色名称
    code VARCHAR(50) NOT NULL,                     -- 角色编码
    description TEXT,                              -- 角色描述
    is_system BOOLEAN DEFAULT FALSE,               -- 是否系统角色
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_roles_tenant_id ON roles(tenant_id);
```

#### 2.2.3 permissions（权限表）
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,                                -- NULL表示系统权限
    name VARCHAR(50) NOT NULL,                     -- 权限名称
    code VARCHAR(100) NOT NULL UNIQUE,             -- 权限编码
    resource VARCHAR(50) NOT NULL,                 -- 资源：patient/registration/treatment等
    action VARCHAR(50) NOT NULL,                  -- 操作：create/read/update/delete
    description TEXT,                              -- 权限描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_permissions_code ON permissions(code);
CREATE INDEX idx_permissions_resource ON permissions(resource);
```

#### 2.2.4 user_roles（用户角色关联表）
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
```

#### 2.2.5 role_permissions（角色权限关联表）
```sql
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(id),
    permission_id UUID NOT NULL REFERENCES permissions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
```

### 2.3 基础数据表

#### 2.3.1 departments（科室表）
```sql
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(50) NOT NULL,                     -- 科室名称
    code VARCHAR(20),                               -- 科室编码
    parent_id UUID REFERENCES departments(id),      -- 父科室ID
    sort_order INTEGER DEFAULT 0,                   -- 排序
    description TEXT,                               -- 描述
    status VARCHAR(20) DEFAULT 'active',           -- 状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_departments_tenant_id ON departments(tenant_id);
CREATE INDEX idx_departments_parent_id ON departments(parent_id);
```

#### 2.3.2 doctors（医生表）
```sql
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),              -- 关联用户
    name VARCHAR(50) NOT NULL,                      -- 医生姓名
    code VARCHAR(20),                               -- 工号
    department_id UUID REFERENCES departments(id),  -- 科室ID
    title VARCHAR(20),                              -- 职称
    specialty VARCHAR(100),                         -- 专长
    phone VARCHAR(20),                              -- 电话（加密）
    status VARCHAR(20) DEFAULT 'active',         -- 状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_doctors_tenant_id ON doctors(tenant_id);
CREATE INDEX idx_doctors_user_id ON doctors(user_id);
CREATE INDEX idx_doctors_department_id ON doctors(department_id);
```

### 2.4 患者管理表

#### 2.4.1 patients（患者表）
```sql
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    patient_no VARCHAR(50) NOT NULL,                -- 病历号
    name_encrypted VARCHAR(255) NOT NULL,          -- 姓名（加密）
    id_card_encrypted VARCHAR(255),                 -- 身份证（加密）
    id_card_hash VARCHAR(64),                      -- 身份证哈希（用于查询）
    gender VARCHAR(10),                             -- 性别：male/female
    birthday DATE,                                   -- 生日
    phone_encrypted VARCHAR(255),                   -- 手机号（加密）
    phone_hash VARCHAR(64),                        -- 手机号哈希（用于查询）
    address TEXT,                                   -- 地址
    emergency_contact VARCHAR(50),                  -- 紧急联系人
    emergency_phone VARCHAR(20),                    -- 紧急联系电话
    blood_type VARCHAR(10),                        -- 血型
    allergy_history TEXT,                           -- 过敏史
    chronic_disease TEXT,                           -- 慢性病史
    remark TEXT,                                    -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, patient_no)
);

CREATE INDEX idx_patients_tenant_id ON patients(tenant_id);
CREATE INDEX idx_patients_patient_no ON patients(tenant_id, patient_no);
CREATE INDEX idx_patients_id_card_hash ON patients(tenant_id, id_card_hash);
CREATE INDEX idx_patients_phone_hash ON patients(tenant_id, phone_hash);
```

### 2.5 挂号管理表

#### 2.5.1 schedules（排班表）
```sql
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    doctor_id UUID NOT NULL REFERENCES doctors(id),
    department_id UUID REFERENCES departments(id),
    schedule_date DATE NOT NULL,                    -- 排班日期
    time_slot VARCHAR(20) NOT NULL,                 -- 时段：morning/afternoon/evening
    start_time TIME NOT NULL,                       -- 开始时间
    end_time TIME NOT NULL,                         -- 结束时间
    total_quota INTEGER DEFAULT 0,                   -- 总号源
    used_quota INTEGER DEFAULT 0,                   -- 已用号源
    price DECIMAL(10,2) DEFAULT 0,                 -- 挂号费
    status VARCHAR(20) DEFAULT 'active',            -- 状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_schedules_tenant_id ON schedules(tenant_id);
CREATE INDEX idx_schedules_doctor_id ON schedules(doctor_id);
CREATE INDEX idx_schedules_date ON schedules(tenant_id, schedule_date);
```

#### 2.5.2 registrations（挂号表）
```sql
CREATE TABLE registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    registration_no VARCHAR(50) NOT NULL,          -- 挂号单号
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID REFERENCES doctors(id),
    department_id UUID REFERENCES departments(id),
    schedule_id UUID REFERENCES schedules(id),
    registration_date DATE NOT NULL,                -- 挂号日期
    registration_time TIME,                         -- 挂号时间
    visit_time TIMESTAMP,                           -- 就诊时间
    registration_type VARCHAR(20) NOT NULL,        -- 类型：onsite/appointment/wechat
    status VARCHAR(20) DEFAULT 'pending',           -- 状态：pending/completed/cancelled
    price DECIMAL(10,2) DEFAULT 0,                 -- 挂号费
    paid_amount DECIMAL(10,2) DEFAULT 0,           -- 已支付金额
    payment_status VARCHAR(20) DEFAULT 'unpaid',   -- 支付状态
    remark TEXT,                                    -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, registration_no)
);

CREATE INDEX idx_registrations_tenant_id ON registrations(tenant_id);
CREATE INDEX idx_registrations_patient_id ON registrations(tenant_id, patient_id);
CREATE INDEX idx_registrations_doctor_id ON registrations(tenant_id, doctor_id);
CREATE INDEX idx_registrations_date ON registrations(tenant_id, registration_date);
CREATE INDEX idx_registrations_status ON registrations(tenant_id, status);
```

### 2.6 诊疗管理表

#### 2.6.1 medical_records（病历表）
```sql
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    record_no VARCHAR(50) NOT NULL,                -- 病历号
    patient_id UUID NOT NULL REFERENCES patients(id),
    registration_id UUID REFERENCES registrations(id),
    doctor_id UUID NOT NULL REFERENCES doctors(id),
    department_id UUID REFERENCES departments(id),
    visit_date DATE NOT NULL,                       -- 就诊日期
    medical_type VARCHAR(20) DEFAULT 'western',    -- 医疗类型：western/tcm/integrated
    chief_complaint TEXT,                           -- 主诉
    present_illness TEXT,                           -- 现病史
    past_history TEXT,                              -- 既往史
    physical_exam TEXT,                             -- 体格检查
    auxiliary_exam TEXT,                            -- 辅助检查
    diagnosis TEXT,                                 -- 诊断
    treatment_plan TEXT,                            -- 治疗方案
    remark TEXT,                                    -- 备注
    status VARCHAR(20) DEFAULT 'draft',            -- 状态：draft/completed/archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, record_no)
);

CREATE INDEX idx_medical_records_tenant_id ON medical_records(tenant_id);
CREATE INDEX idx_medical_records_patient_id ON medical_records(tenant_id, patient_id);
CREATE INDEX idx_medical_records_doctor_id ON medical_records(tenant_id, doctor_id);
CREATE INDEX idx_medical_records_visit_date ON medical_records(tenant_id, visit_date);
```

#### 2.6.2 diagnoses（诊断表）
```sql
CREATE TABLE diagnoses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    medical_record_id UUID NOT NULL REFERENCES medical_records(id),
    icd_code VARCHAR(20),                         -- ICD编码
    diagnosis_name VARCHAR(200) NOT NULL,        -- 诊断名称
    diagnosis_type VARCHAR(20),                  -- 类型：primary/secondary
    description TEXT,                            -- 描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_diagnoses_tenant_id ON diagnoses(tenant_id);
CREATE INDEX idx_diagnoses_medical_record_id ON diagnoses(medical_record_id);
```

#### 2.6.3 prescriptions（处方表）
```sql
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    prescription_no VARCHAR(50) NOT NULL,         -- 处方号
    medical_record_id UUID REFERENCES medical_records(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES doctors(id),
    prescription_date DATE NOT NULL,              -- 处方日期
    total_amount DECIMAL(10,2) DEFAULT 0,         -- 总金额
    status VARCHAR(20) DEFAULT 'pending',        -- 状态：pending/dispensed/cancelled
    remark TEXT,                                  -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, prescription_no)
);

CREATE INDEX idx_prescriptions_tenant_id ON prescriptions(tenant_id);
CREATE INDEX idx_prescriptions_patient_id ON prescriptions(tenant_id, patient_id);
CREATE INDEX idx_prescriptions_doctor_id ON prescriptions(tenant_id, doctor_id);
CREATE INDEX idx_prescriptions_status ON prescriptions(tenant_id, status);
```

#### 2.6.4 prescription_items（处方明细表）
```sql
CREATE TABLE prescription_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id),
    drug_id UUID NOT NULL REFERENCES drugs(id),
    drug_name VARCHAR(100) NOT NULL,              -- 药品名称
    specification VARCHAR(50),                   -- 规格
    unit VARCHAR(20),                            -- 单位
    quantity DECIMAL(10,2) NOT NULL,             -- 数量
    unit_price DECIMAL(10,2) NOT NULL,           -- 单价
    total_price DECIMAL(10,2) NOT NULL,          -- 总价
    usage_method VARCHAR(100),                   -- 用法
    frequency VARCHAR(50),                       -- 频次
    duration VARCHAR(50),                        -- 疗程
    drug_type VARCHAR(20) DEFAULT 'western',     -- 药品类型：western/chinese/chinese_patent
    remark TEXT,                                 -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_prescription_items_tenant_id ON prescription_items(tenant_id);
CREATE INDEX idx_prescription_items_prescription_id ON prescription_items(prescription_id);
CREATE INDEX idx_prescription_items_drug_id ON prescription_items(drug_id);
```

#### 2.6.5 tcm_diagnosis（中医诊断表）
```sql
CREATE TABLE tcm_diagnosis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    medical_record_id UUID NOT NULL REFERENCES medical_records(id),
    syndrome_type VARCHAR(100),                   -- 证型
    pathogenesis TEXT,                           -- 病机
    disease_name VARCHAR(100),                    -- 病名
    constitution_type VARCHAR(50),                -- 体质类型（九种体质）
    constitution_desc TEXT,                      -- 体质描述
    tongue_state TEXT,                           -- 舌象
    pulse_state TEXT,                            -- 脉象
    tcm_diagnosis TEXT,                          -- 中医诊断
    treatment_principle TEXT,                    -- 治则
    treatment_method TEXT,                        -- 治法
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tcm_diagnosis_tenant_id ON tcm_diagnosis(tenant_id);
CREATE INDEX idx_tcm_diagnosis_medical_record_id ON tcm_diagnosis(medical_record_id);
```

#### 2.6.6 tcm_four_examinations（中医四诊表）
```sql
CREATE TABLE tcm_four_examinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    medical_record_id UUID NOT NULL REFERENCES medical_records(id),
    inspection TEXT,                             -- 望诊
    listening_smelling TEXT,                     -- 闻诊
    inquiry TEXT,                                -- 问诊
    pulse_feeling TEXT,                          -- 切诊（脉诊）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tcm_four_examinations_tenant_id ON tcm_four_examinations(tenant_id);
CREATE INDEX idx_tcm_four_examinations_medical_record_id ON tcm_four_examinations(medical_record_id);
```

#### 2.6.7 tcm_treatments（中医治疗方法表）
```sql
CREATE TABLE tcm_treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    medical_record_id UUID NOT NULL REFERENCES medical_records(id),
    treatment_type VARCHAR(50) NOT NULL,         -- 治疗类型：acupuncture/massage/cupping/moxibustion
    treatment_name VARCHAR(100) NOT NULL,        -- 治疗方法名称
    treatment_points TEXT,                      -- 治疗穴位/部位
    treatment_duration INTEGER,                   -- 治疗时长（分钟）
    treatment_frequency VARCHAR(50),             -- 治疗频次
    treatment_course INTEGER,                     -- 疗程（次数）
    remark TEXT,                                 -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tcm_treatments_tenant_id ON tcm_treatments(tenant_id);
CREATE INDEX idx_tcm_treatments_medical_record_id ON tcm_treatments(medical_record_id);
```

#### 2.6.8 tcm_prescriptions（中药处方表）
```sql
CREATE TABLE tcm_prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    prescription_id UUID REFERENCES prescriptions(id), -- 关联通用处方
    medical_record_id UUID REFERENCES medical_records(id),
    prescription_no VARCHAR(50) NOT NULL,         -- 处方号
    prescription_type VARCHAR(50),                -- 处方类型：classical/empirical/agreed
    prescription_name VARCHAR(100),               -- 方剂名称
    decoction_method TEXT,                       -- 煎服法
    dosage_days INTEGER,                         -- 服药天数
    total_dose DECIMAL(10,2),                    -- 总剂量
    decoction_service BOOLEAN DEFAULT FALSE,     -- 是否代煎
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, prescription_no)
);

CREATE INDEX idx_tcm_prescriptions_tenant_id ON tcm_prescriptions(tenant_id);
CREATE INDEX idx_tcm_prescriptions_prescription_id ON tcm_prescriptions(prescription_id);
```

#### 2.6.9 tcm_prescription_items（中药处方明细表）
```sql
CREATE TABLE tcm_prescription_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    tcm_prescription_id UUID NOT NULL REFERENCES tcm_prescriptions(id),
    drug_id UUID NOT NULL REFERENCES drugs(id),
    drug_name VARCHAR(100) NOT NULL,             -- 药品名称
    specification VARCHAR(50),                   -- 规格
    unit VARCHAR(20),                            -- 单位（克、两、钱等）
    quantity DECIMAL(10,2) NOT NULL,            -- 数量
    dosage_unit VARCHAR(20),                     -- 剂量单位
    processing_method VARCHAR(50),                -- 炮制方法
    role_in_prescription VARCHAR(50),            -- 方中作用（君、臣、佐、使）
    remark TEXT,                                 -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tcm_prescription_items_tenant_id ON tcm_prescription_items(tenant_id);
CREATE INDEX idx_tcm_prescription_items_tcm_prescription_id ON tcm_prescription_items(tcm_prescription_id);
CREATE INDEX idx_tcm_prescription_items_drug_id ON tcm_prescription_items(drug_id);
```

#### 2.6.10 tcm_formulas（中医方剂表）
```sql
CREATE TABLE tcm_formulas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,                              -- NULL表示系统方剂
    formula_name VARCHAR(100) NOT NULL,            -- 方剂名称
    formula_type VARCHAR(50),                    -- 方剂类型：classical/empirical/agreed
    source VARCHAR(200),                          -- 来源
    composition TEXT,                            -- 组成
    functions TEXT,                              -- 功效
    indications TEXT,                           -- 主治
    contraindications TEXT,                      -- 禁忌
    usage_method TEXT,                          -- 用法
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tcm_formulas_tenant_id ON tcm_formulas(tenant_id);
CREATE INDEX idx_tcm_formulas_formula_name ON tcm_formulas(formula_name);
```

### 2.7 收费管理表

#### 2.7.1 charge_items（收费项目表）
```sql
CREATE TABLE charge_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    code VARCHAR(50) NOT NULL,                    -- 项目编码
    name VARCHAR(100) NOT NULL,                   -- 项目名称
    category VARCHAR(50),                         -- 类别：registration/examination/medicine
    unit VARCHAR(20),                             -- 单位
    price DECIMAL(10,2) NOT NULL,                -- 价格
    insurance_price DECIMAL(10,2),                -- 医保价格
    status VARCHAR(20) DEFAULT 'active',         -- 状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_charge_items_tenant_id ON charge_items(tenant_id);
CREATE INDEX idx_charge_items_category ON charge_items(tenant_id, category);
```

#### 2.7.2 bills（账单表）
```sql
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    bill_no VARCHAR(50) NOT NULL,                -- 账单号
    patient_id UUID NOT NULL REFERENCES patients(id),
    registration_id UUID REFERENCES registrations(id),
    medical_record_id UUID REFERENCES medical_records(id),
    prescription_id UUID REFERENCES prescriptions(id),
    bill_type VARCHAR(20) NOT NULL,              -- 类型：registration/treatment/medicine
    total_amount DECIMAL(10,2) NOT NULL,         -- 总金额
    discount_amount DECIMAL(10,2) DEFAULT 0,      -- 优惠金额
    insurance_amount DECIMAL(10,2) DEFAULT 0,     -- 医保金额
    self_pay_amount DECIMAL(10,2) NOT NULL,      -- 自付金额
    paid_amount DECIMAL(10,2) DEFAULT 0,         -- 已支付金额
    status VARCHAR(20) DEFAULT 'unpaid',         -- 状态：unpaid/paid/partial/refunded
    payment_method VARCHAR(20),                   -- 支付方式
    paid_at TIMESTAMP,                            -- 支付时间
    remark TEXT,                                  -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, bill_no)
);

CREATE INDEX idx_bills_tenant_id ON bills(tenant_id);
CREATE INDEX idx_bills_patient_id ON bills(tenant_id, patient_id);
CREATE INDEX idx_bills_status ON bills(tenant_id, status);
CREATE INDEX idx_bills_date ON bills(tenant_id, created_at);
```

#### 2.7.3 bill_items（账单明细表）
```sql
CREATE TABLE bill_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    bill_id UUID NOT NULL REFERENCES bills(id),
    charge_item_id UUID REFERENCES charge_items(id),
    item_name VARCHAR(100) NOT NULL,              -- 项目名称
    quantity DECIMAL(10,2) NOT NULL,            -- 数量
    unit_price DECIMAL(10,2) NOT NULL,           -- 单价
    total_price DECIMAL(10,2) NOT NULL,         -- 总价
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_bill_items_tenant_id ON bill_items(tenant_id);
CREATE INDEX idx_bill_items_bill_id ON bill_items(bill_id);
```

#### 2.7.4 payments（支付记录表）
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    payment_no VARCHAR(50) NOT NULL,             -- 支付单号
    bill_id UUID NOT NULL REFERENCES bills(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    amount DECIMAL(10,2) NOT NULL,              -- 支付金额
    payment_method VARCHAR(20) NOT NULL,         -- 支付方式：cash/wechat/alipay/bankcard/insurance
    payment_channel VARCHAR(50),                 -- 支付渠道
    transaction_id VARCHAR(100),                 -- 第三方交易号
    status VARCHAR(20) DEFAULT 'pending',       -- 状态：pending/success/failed/refunded
    paid_at TIMESTAMP,                           -- 支付时间
    remark TEXT,                                 -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, payment_no)
);

CREATE INDEX idx_payments_tenant_id ON payments(tenant_id);
CREATE INDEX idx_payments_bill_id ON payments(bill_id);
CREATE INDEX idx_payments_patient_id ON payments(tenant_id, patient_id);
CREATE INDEX idx_payments_status ON payments(tenant_id, status);
CREATE INDEX idx_payments_date ON payments(tenant_id, paid_at);
```

### 2.8 药房管理表

#### 2.8.1 drugs（药品表）
```sql
CREATE TABLE drugs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    code VARCHAR(50) NOT NULL,                    -- 药品编码
    name VARCHAR(100) NOT NULL,                   -- 药品名称
    generic_name VARCHAR(100),                   -- 通用名
    specification VARCHAR(50),                    -- 规格
    unit VARCHAR(20),                             -- 单位
    category VARCHAR(50),                         -- 类别
    drug_type VARCHAR(20) DEFAULT 'western',      -- 药品类型：western/chinese/chinese_patent
    manufacturer VARCHAR(100),                     -- 生产厂家
    approval_number VARCHAR(50),                  -- 批准文号
    purchase_price DECIMAL(10,2),                 -- 进价
    sale_price DECIMAL(10,2),                     -- 售价
    insurance_price DECIMAL(10,2),                -- 医保价
    min_stock INTEGER DEFAULT 0,                  -- 最低库存
    max_stock INTEGER DEFAULT 0,                  -- 最高库存
    -- 中药特有字段
    tcm_category VARCHAR(50),                    -- 中药分类（解表、清热、补益等）
    tcm_nature VARCHAR(20),                      -- 药性（寒、热、温、凉、平）
    tcm_flavor VARCHAR(20),                      -- 五味（酸、苦、甘、辛、咸）
    tcm_meridian VARCHAR(100),                   -- 归经
    tcm_efficacy TEXT,                          -- 功效
    tcm_processing_method VARCHAR(50),           -- 炮制方法
    expiry_months INTEGER,                       -- 保质期（月）
    status VARCHAR(20) DEFAULT 'active',         -- 状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_drugs_tenant_id ON drugs(tenant_id);
CREATE INDEX idx_drugs_code ON drugs(tenant_id, code);
CREATE INDEX idx_drugs_name ON drugs(tenant_id, name);
CREATE INDEX idx_drugs_drug_type ON drugs(tenant_id, drug_type);
CREATE INDEX idx_drugs_tcm_category ON drugs(tenant_id, tcm_category);
```

#### 2.8.1a tcm_decoction_service（中药煎药服务表）
```sql
CREATE TABLE tcm_decoction_service (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    tcm_prescription_id UUID NOT NULL REFERENCES tcm_prescriptions(id),
    service_type VARCHAR(20) DEFAULT 'decoction', -- 服务类型：decoction/grinding
    status VARCHAR(20) DEFAULT 'pending',        -- 状态：pending/processing/completed
    decoction_method VARCHAR(50),                -- 煎药方法
    decoction_start_time TIMESTAMP,              -- 开始煎药时间
    decoction_complete_time TIMESTAMP,           -- 完成煎药时间
    operator_id UUID REFERENCES users(id),       -- 操作人
    remark TEXT,                                -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_tcm_decoction_service_tenant_id ON tcm_decoction_service(tenant_id);
CREATE INDEX idx_tcm_decoction_service_prescription_id ON tcm_decoction_service(tcm_prescription_id);
```

#### 2.8.2 inventory（库存表）
```sql
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    drug_id UUID NOT NULL REFERENCES drugs(id),
    quantity DECIMAL(10,2) NOT NULL DEFAULT 0,   -- 当前库存
    unit_cost DECIMAL(10,2),                     -- 单位成本
    location VARCHAR(50),                         -- 存放位置
    batch_no VARCHAR(50),                         -- 批次号
    expiry_date DATE,                             -- 有效期
    last_in_date DATE,                            -- 最后入库日期
    last_out_date DATE,                           -- 最后出库日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, drug_id)
);

CREATE INDEX idx_inventory_tenant_id ON inventory(tenant_id);
CREATE INDEX idx_inventory_drug_id ON inventory(drug_id);
CREATE INDEX idx_inventory_expiry_date ON inventory(tenant_id, expiry_date);
```

#### 2.8.3 inventory_transactions（库存流水表）
```sql
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    drug_id UUID NOT NULL REFERENCES drugs(id),
    transaction_no VARCHAR(50) NOT NULL,          -- 流水号
    transaction_type VARCHAR(20) NOT NULL,        -- 类型：in/out/adjust
    quantity DECIMAL(10,2) NOT NULL,             -- 数量（正数入库，负数出库）
    unit_price DECIMAL(10,2),                    -- 单价
    total_amount DECIMAL(10,2),                  -- 总金额
    batch_no VARCHAR(50),                        -- 批次号
    expiry_date DATE,                            -- 有效期
    related_id UUID,                             -- 关联单据ID（如处方ID）
    related_type VARCHAR(50),                    -- 关联类型
    operator_id UUID REFERENCES users(id),         -- 操作人
    remark TEXT,                                  -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, transaction_no)
);

CREATE INDEX idx_inventory_transactions_tenant_id ON inventory_transactions(tenant_id);
CREATE INDEX idx_inventory_transactions_drug_id ON inventory_transactions(drug_id);
CREATE INDEX idx_inventory_transactions_type ON inventory_transactions(tenant_id, transaction_type);
CREATE INDEX idx_inventory_transactions_date ON inventory_transactions(tenant_id, created_at);
```

#### 2.8.4 prescription_dispensing（处方发药表）
```sql
CREATE TABLE prescription_dispensing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id),
    prescription_item_id UUID REFERENCES prescription_items(id),
    drug_id UUID NOT NULL REFERENCES drugs(id),
    quantity DECIMAL(10,2) NOT NULL,             -- 发药数量
    dispensed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 发药时间
    dispenser_id UUID REFERENCES users(id),       -- 发药人
    status VARCHAR(20) DEFAULT 'dispensed',      -- 状态
    remark TEXT,                                 -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_prescription_dispensing_tenant_id ON prescription_dispensing(tenant_id);
CREATE INDEX idx_prescription_dispensing_prescription_id ON prescription_dispensing(prescription_id);
```

### 2.9 系统日志表

#### 2.9.1 operation_logs（操作日志表）
```sql
CREATE TABLE operation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    operation_type VARCHAR(50) NOT NULL,          -- 操作类型：create/update/delete/query
    resource_type VARCHAR(50) NOT NULL,          -- 资源类型：patient/registration等
    resource_id UUID,                             -- 资源ID
    operation_desc TEXT,                          -- 操作描述
    request_data JSONB,                           -- 请求数据
    response_data JSONB,                          -- 响应数据
    ip_address VARCHAR(50),                      -- IP地址
    user_agent TEXT,                              -- 用户代理
    status VARCHAR(20),                           -- 状态：success/failed
    error_message TEXT,                           -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operation_logs_tenant_id ON operation_logs(tenant_id);
CREATE INDEX idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_resource ON operation_logs(tenant_id, resource_type, resource_id);
CREATE INDEX idx_operation_logs_date ON operation_logs(tenant_id, created_at);
```

### 2.10 通知表

#### 2.10.1 notifications（通知表）
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    notification_type VARCHAR(50) NOT NULL,      -- 类型：sms/wechat/email
    recipient_type VARCHAR(20) NOT NULL,         -- 接收者类型：patient/user
    recipient_id UUID NOT NULL,                  -- 接收者ID
    recipient_info VARCHAR(255),                 -- 接收者信息（手机号、微信号等）
    title VARCHAR(200),                          -- 标题
    content TEXT NOT NULL,                       -- 内容
    template_id VARCHAR(50),                     -- 模板ID
    status VARCHAR(20) DEFAULT 'pending',        -- 状态：pending/sent/failed
    sent_at TIMESTAMP,                           -- 发送时间
    error_message TEXT,                          -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_tenant_id ON notifications(tenant_id);
CREATE INDEX idx_notifications_recipient ON notifications(tenant_id, recipient_type, recipient_id);
CREATE INDEX idx_notifications_status ON notifications(tenant_id, status);
CREATE INDEX idx_notifications_date ON notifications(tenant_id, created_at);
```

## 三、数据加密说明

### 3.1 加密字段
以下字段需要加密存储：
- `patients.name_encrypted`: 患者姓名
- `patients.id_card_encrypted`: 身份证号
- `patients.phone_encrypted`: 手机号
- `doctors.phone`: 医生电话
- `users.phone`: 用户手机号

### 3.2 哈希字段
以下字段需要哈希存储（用于查询）：
- `patients.id_card_hash`: 身份证哈希
- `patients.phone_hash`: 手机号哈希

### 3.3 加密实现
- **算法**: AES-256-GCM
- **密钥管理**: 使用密钥管理服务（KMS）
- **密钥轮换**: 定期轮换加密密钥

## 四、索引优化建议

### 4.1 联合索引
- `(tenant_id, patient_no)`: 患者查询
- `(tenant_id, registration_date)`: 挂号查询
- `(tenant_id, visit_date)`: 病历查询
- `(tenant_id, created_at)`: 时间范围查询

### 4.2 单列索引
- `tenant_id`: 所有表的租户隔离
- `status`: 状态查询
- `deleted_at`: 软删除过滤

## 五、数据迁移策略

### 5.1 版本管理
- 使用数据库迁移工具（Alembic）
- 版本化数据库变更
- 支持回滚操作

### 5.2 数据初始化
- 系统权限数据初始化
- 基础字典数据初始化
- 默认角色和用户创建

## 六、备份策略

### 6.1 备份方式
- **全量备份**: 每日全量备份
- **增量备份**: 每小时增量备份
- **事务日志**: 实时事务日志备份

### 6.2 备份存储
- 备份数据加密存储
- 多地域备份
- 定期恢复测试


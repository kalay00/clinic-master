"""
创建核心业务表（用于补全缺失的表）
"""
from app.core.database import engine
from sqlalchemy import text

def create_core_tables():
    """创建核心业务表"""
    with engine.begin() as conn:
        # 1. 创建患者表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS patients (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    patient_no VARCHAR(50),
                    name VARCHAR(255) NOT NULL,
                    gender VARCHAR(10),
                    birthday DATE,
                    id_card VARCHAR(18) NOT NULL,
                    phone VARCHAR(20),
                    address TEXT,
                    emergency_contact VARCHAR(50),
                    emergency_phone VARCHAR(20),
                    blood_type VARCHAR(10),
                    allergy_history TEXT,
                    chronic_disease TEXT,
                    remark TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_patients_tenant_id ON patients(tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_patients_patient_no ON patients(patient_no)"))
            # 严格唯一：同一租户下、未软删除的患者身份证号不可重复（DB 层兜底）
            conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_patients_tenant_id_card "
                "ON patients (tenant_id, id_card) WHERE deleted_at IS NULL"
            ))
            print("✅ 创建patients表")
        except Exception as e:
            print(f"⚠️  patients表: {str(e)}")
        
        # 2. 创建医生表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    user_id UUID REFERENCES users(id),
                    name VARCHAR(50) NOT NULL,
                    employee_no VARCHAR(50) NOT NULL,
                    department_id UUID REFERENCES departments(id),
                    title VARCHAR(50),
                    specialty VARCHAR(100),
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_doctors_tenant_id ON doctors(tenant_id)"))
            print("✅ 创建doctors表")
        except Exception as e:
            print(f"⚠️  doctors表: {str(e)}")
        
        # 3. 创建排班表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    doctor_id UUID NOT NULL REFERENCES doctors(id),
                    department_id UUID REFERENCES departments(id),
                    schedule_date DATE NOT NULL,
                    time_slot VARCHAR(20) NOT NULL,
                    start_time TIME,
                    end_time TIME,
                    total_quota INTEGER NOT NULL,
                    used_quota INTEGER DEFAULT 0,
                    price NUMERIC(10, 2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_schedules_tenant_id ON schedules(tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_schedules_doctor_id ON schedules(doctor_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_schedules_schedule_date ON schedules(schedule_date)"))
            print("✅ 创建schedules表")
        except Exception as e:
            print(f"⚠️  schedules表: {str(e)}")
        
        # 4. 创建挂号表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    registration_no VARCHAR(50) NOT NULL UNIQUE,
                    patient_id UUID NOT NULL REFERENCES patients(id),
                    doctor_id UUID REFERENCES doctors(id),
                    department_id UUID REFERENCES departments(id),
                    schedule_id UUID REFERENCES schedules(id),
                    registration_date DATE NOT NULL,
                    registration_time TIME,
                    visit_time TIMESTAMP WITH TIME ZONE,
                    registration_type VARCHAR(20) NOT NULL DEFAULT 'onsite',
                    status VARCHAR(20) DEFAULT 'pending',
                    price NUMERIC(10, 2) DEFAULT 0,
                    paid_amount NUMERIC(10, 2) DEFAULT 0,
                    payment_status VARCHAR(20) DEFAULT 'unpaid',
                    remark TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_registrations_tenant_id ON registrations(tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_registrations_patient_id ON registrations(patient_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_registrations_registration_no ON registrations(registration_no)"))
            print("✅ 创建registrations表")
        except Exception as e:
            print(f"⚠️  registrations表: {str(e)}")
        
        # 5. 创建病历表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS medical_records (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    registration_id UUID NOT NULL REFERENCES registrations(id),
                    patient_id UUID NOT NULL REFERENCES patients(id),
                    doctor_id UUID NOT NULL REFERENCES doctors(id),
                    chief_complaint TEXT,
                    present_illness TEXT,
                    past_history TEXT,
                    physical_examination TEXT,
                    diagnosis TEXT,
                    treatment_plan TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_medical_records_tenant_id ON medical_records(tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_medical_records_patient_id ON medical_records(patient_id)"))
            print("✅ 创建medical_records表")
        except Exception as e:
            print(f"⚠️  medical_records表: {str(e)}")
        
        # 6. 创建处方表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    prescription_no VARCHAR(50) NOT NULL UNIQUE,
                    medical_record_id UUID REFERENCES medical_records(id),
                    patient_id UUID NOT NULL REFERENCES patients(id),
                    doctor_id UUID NOT NULL REFERENCES doctors(id),
                    prescription_type VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_prescriptions_tenant_id ON prescriptions(tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_prescriptions_patient_id ON prescriptions(patient_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_prescriptions_prescription_no ON prescriptions(prescription_no)"))
            print("✅ 创建prescriptions表")
        except Exception as e:
            print(f"⚠️  prescriptions表: {str(e)}")
        
        # 7. 创建账单表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bills (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    bill_no VARCHAR(50) NOT NULL UNIQUE,
                    patient_id UUID NOT NULL REFERENCES patients(id),
                    registration_id UUID REFERENCES registrations(id),
                    medical_record_id UUID REFERENCES medical_records(id),
                    prescription_id UUID REFERENCES prescriptions(id),
                    bill_type VARCHAR(20) NOT NULL,
                    total_amount NUMERIC(10, 2) DEFAULT 0,
                    paid_amount NUMERIC(10, 2) DEFAULT 0,
                    discount_amount NUMERIC(10, 2) DEFAULT 0,
                    insurance_amount NUMERIC(10, 2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'unpaid',
                    payment_method VARCHAR(20),
                    payment_time TIMESTAMP WITH TIME ZONE,
                    items JSONB,
                    remark TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_bills_tenant_id ON bills(tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_bills_bill_no ON bills(bill_no)"))
            print("✅ 创建bills表")
        except Exception as e:
            print(f"⚠️  bills表: {str(e)}")
        
        # 8. 创建支付表
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL REFERENCES tenants(id),
                    payment_no VARCHAR(50) NOT NULL UNIQUE,
                    bill_id UUID NOT NULL REFERENCES bills(id),
                    patient_id UUID NOT NULL REFERENCES patients(id),
                    payment_method VARCHAR(20) NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    transaction_id VARCHAR(100),
                    remark TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_tenant_id ON payments(tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_payments_payment_no ON payments(payment_no)"))
            print("✅ 创建payments表")
        except Exception as e:
            print(f"⚠️  payments表: {str(e)}")
        
        print("\n✅ 核心业务表创建完成！")

if __name__ == "__main__":
    create_core_tables()


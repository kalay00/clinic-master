"""
患者模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Date, Text, ForeignKey, Integer, Boolean, Index, text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Patient(BaseModel):
    """患者模型"""
    __tablename__ = "patients"
    
    patient_no = Column(String(50), nullable=False, comment="档案号")
    # 基本信息（明文存储，不再加密）
    name = Column(String(255), nullable=False, comment="患者姓名")
    gender = Column(String(10), comment="性别：male/female")
    birthday = Column(Date, comment="生日")
    id_card = Column(String(18), nullable=False, comment="身份证号")
    phone = Column(String(20), comment="手机号")
    address = Column(Text, comment="地址")
    emergency_contact = Column(String(50), comment="紧急联系人")
    emergency_phone = Column(String(20), comment="紧急联系电话")
    blood_type = Column(String(10), comment="血型")
    allergy_history = Column(Text, comment="过敏史")
    chronic_disease = Column(Text, comment="慢性病史")
    remark = Column(Text, comment="备注")
    # 会员相关
    member_level_id = Column(UUID(as_uuid=True), ForeignKey("member_levels.id", ondelete="SET NULL"), comment="会员等级ID")
    consumption_total = Column(Numeric(12, 2), default=0, comment="累计消费金额（用于自动升级）")
    # 会员资产
    balance = Column(Numeric(12, 2), default=0, comment="账户余额")
    points = Column(Integer, default=0, comment="积分")
    # 会员扩展
    member_status = Column(String(20), default="active", comment="会员状态：active/inactive/expired")
    expire_date = Column(Date, comment="会员到期时间")
    stored_total = Column(Numeric(12, 2), default=0, comment="累计储值金额")
    gift_total = Column(Numeric(12, 2), default=0, comment="累计赠送金额")

    member_level = relationship("MemberLevel", uselist=False)
    
    __table_args__ = (
        # 严格唯一：同一租户下，未软删除的患者身份证号不可重复。
        # 采用部分唯一索引（仅对 deleted_at IS NULL 生效），软删除记录不占用唯一性。
        Index(
            "uq_patients_tenant_id_card",
            "tenant_id",
            "id_card",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "患者表"},
    )


class FamilyMember(BaseModel):
    """患者家庭成员模型"""
    __tablename__ = "family_members"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, comment="患者ID")
    relation = Column(String(50), nullable=False, comment="家庭关系")
    name = Column(String(255), nullable=False, comment="姓名")
    gender = Column(String(10), comment="性别：male/female")
    birthday = Column(Date, comment="出生日期")
    age = Column(Integer, comment="年龄")
    phone = Column(String(20), comment="手机号码")


class PatientPhoto(BaseModel):
    """患者照片模型"""
    __tablename__ = "patient_photos"
    
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True, comment="患者ID")
    photo_url = Column(String(500), nullable=False, comment="照片URL")
    photo_path = Column(String(500), nullable=False, comment="照片存储路径")
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_size = Column(Integer, comment="文件大小（字节）")
    file_type = Column(String(50), comment="文件类型（image/jpeg, image/png等）")
    width = Column(Integer, comment="图片宽度（像素）")
    height = Column(Integer, comment="图片高度（像素）")
    is_primary = Column(Boolean, default=False, nullable=False, index=True, comment="是否为主照片")
    description = Column(Text, comment="照片描述")
    
    # 关系
    patient = relationship("Patient", backref="photos")
    
    __table_args__ = (
        {"comment": "患者照片表（v2.0新增）"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<PatientPhoto(id={self.id}, patient_id={self.patient_id}, file_name={self.file_name})>"

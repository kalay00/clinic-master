"""
项目模块 ORM 模型
"""
from sqlalchemy import Column, String, Numeric, Integer, Boolean, Text, ForeignKey, Date, DateTime, func
from app.core.database import BaseModel


class ProjectCategory(BaseModel):
    """项目分类"""
    __tablename__ = "project_categories"

    name = Column(String(50), nullable=False, comment="分类名称")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="active", comment="状态 active/inactive")
    remark = Column(Text, comment="备注")

    __table_args__ = ({"comment": "项目分类表"},)


class Project(BaseModel):
    """诊疗/服务项目"""
    __tablename__ = "projects"

    name = Column(String(100), nullable=False, comment="项目名称")
    category_id = Column(String(36), comment="项目分类ID")
    main_image = Column(String(500), comment="主图URL")
    price = Column(Numeric(10, 2), default=0, comment="项目价（售价）")
    cost = Column(Numeric(10, 2), default=0, comment="成本")
    service_fee = Column(Numeric(10, 2), default=0, comment="服务费用（服务包总额）")
    service_count = Column(Integer, default=1, comment="服务次数（次数型）")
    participate_member_discount = Column(Boolean, default=True, comment="是否参与会员折扣")
    participate_commission = Column(Boolean, default=False, comment="是否参与提成")
    # 服务方式：count=按次数, period=按周期
    service_type = Column(String(20), default="count", comment="服务方式 count/period")
    # 周期类型：year=包年, month=包月, custom=指定时间范围
    period_type = Column(String(20), comment="周期类型 year/month/custom")
    period_start = Column(Date, comment="周期开始（custom）")
    period_end = Column(Date, comment="周期结束（custom）")
    status = Column(String(20), default="active", comment="状态 active/inactive")
    remark = Column(Text, comment="备注")
    # 会员积分：每次服务可抵扣的积分（0 表示不可抵扣）
    deductible_points = Column(Integer, default=0, comment="每次服务可抵扣积分（0 表示不可抵扣）")

    __table_args__ = ({"comment": "项目表"},)


class PatientProject(BaseModel):
    """患者购买项目记录（用于核销）"""
    __tablename__ = "patient_projects"

    patient_id = Column(String(36), nullable=False, comment="患者ID")
    project_id = Column(String(36), nullable=False, comment="项目ID")
    project_name = Column(String(100), comment="项目名称快照")
    quantity = Column(Integer, default=1, comment="购买数量")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价（折后）")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    # 次数型剩余可核销次数；周期型为 NULL
    remaining_count = Column(Integer, default=0, comment="剩余核销次数")
    start_date = Column(Date, comment="生效开始（周期型）")
    end_date = Column(Date, comment="生效结束（周期型）")
    status = Column(String(20), default="active", comment="状态 active/completed/expired")

    __table_args__ = ({"comment": "患者项目购买表"},)


class ProjectVerification(BaseModel):
    """项目服务核销记录"""
    __tablename__ = "project_verifications"

    patient_project_id = Column(String(36), nullable=False, comment="患者项目ID")
    project_id = Column(String(36), comment="项目ID")
    patient_id = Column(String(36), comment="患者ID")
    technician_id = Column(String(36), comment="服务技师ID")
    verify_amount = Column(Numeric(10, 2), default=0, comment="本次核销收入(服务费/次数)")
    verified_at = Column(DateTime, server_default=func.now(), comment="核销时间")

    __table_args__ = ({"comment": "项目核销记录表"},)

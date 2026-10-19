"""
药房模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Numeric, Integer, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class DrugCategory(BaseModel):
    """药品分类模型"""
    __tablename__ = "drug_categories"

    name = Column(String(50), nullable=False, comment="分类名称")
    category_type = Column(String(20), default="western", comment="处方分类 western/chinese_patent/herb/all")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="active", comment="状态 active/inactive")
    remark = Column(Text, comment="备注")

    created_by_user = relationship(
        "User",
        primaryjoin="DrugCategory.created_by == User.id",
        foreign_keys="[DrugCategory.created_by]",
        uselist=False,
        lazy="joined",
    )

    __table_args__ = ({"comment": "药品分类表"},)


class Drug(BaseModel):
    """药品模型"""
    __tablename__ = "drugs"
    
    drug_code = Column(String(50), nullable=False, comment="药品编码")
    name = Column(String(100), nullable=False, comment="药品名称")
    generic_name = Column(String(100), comment="通用名")
    specification = Column(String(100), comment="规格")
    unit = Column(String(20), comment="单位")
    category = Column(String(50), comment="药品分类（旧，兼容保留）")
    category_id = Column(UUID(as_uuid=True), ForeignKey("drug_categories.id"), comment="药品分类ID")
    manufacturer = Column(String(100), comment="生产厂家")
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), comment="供应商ID")
    price = Column(Numeric(10, 2), default=0, comment="单价/零售价")
    status = Column(String(20), default="active", comment="状态")

    # 扩展字段（对齐新版药品录入页）
    drug_type = Column(String(20), default="western", comment="药品类型 western/chinese_patent/herb")
    barcode = Column(String(100), comment="药品条形码")
    pinyin_code = Column(String(50), comment="拼音码")
    form = Column(String(50), comment="药品剂型")
    is_otc = Column(Boolean, default=False, comment="是否OTC药品")
    fee_item_id = Column(String(36), comment="发票项目ID")
    approval_no = Column(String(100), comment="批准文号")

    # 包装信息
    base_coefficient = Column(Numeric(10, 4), default=1, comment="基本系数")
    base_unit = Column(String(20), comment="基本单位")
    dose_coefficient = Column(Numeric(10, 4), default=1, comment="剂量系数")
    dose_unit = Column(String(20), comment="剂量单位")
    purchase_price = Column(Numeric(10, 2), default=0, comment="采购价")
    allow_split = Column(Boolean, default=False, comment="允许拆零")
    allow_discount = Column(Boolean, default=True, comment="允许会员折扣")

    # 功效说明
    usage_id = Column(String(36), comment="用法ID")
    single_dose = Column(Numeric(10, 4), default=0, comment="单次用量")
    single_dose_unit = Column(String(20), comment="单次用量单位")
    frequency_id = Column(String(36), comment="频度ID")
    days = Column(Integer, default=1, comment="天数")
    total_qty = Column(Numeric(10, 4), default=1, comment="总量")
    total_unit = Column(String(20), comment="总量单位")

    # 其他信息
    stock_min = Column(Integer, default=0, comment="库存下限")
    stock_max = Column(Integer, default=0, comment="库存上限")
    location_no = Column(String(50), comment="货位号")
    expiry_warning_days = Column(Integer, default=30, comment="有效期预警天数")
    description = Column(Text, comment="药品说明")
    remark = Column(Text, comment="备注")
    
    __table_args__ = (
        {"comment": "药品表"},
    )


class Inventory(BaseModel):
    """库存模型"""
    __tablename__ = "inventory"
    
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    quantity = Column(Integer, default=0, comment="库存数量")
    min_quantity = Column(Integer, default=0, comment="最小库存")
    max_quantity = Column(Integer, default=0, comment="最大库存")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价")
    batch_no = Column(String(50), comment="批次号")
    expiry_date = Column(String(20), comment="有效期")
    
    __table_args__ = (
        {"comment": "库存表"},
    )


class Dispense(BaseModel):
    """发药模型"""
    __tablename__ = "dispenses"
    
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, comment="处方ID")
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    status = Column(String(20), default="pending", comment="状态：pending/dispensed/cancelled")
    remark = Column(Text, comment="备注")
    
    __table_args__ = (
        {"comment": "发药表"},
    )


class PriceAdjustment(BaseModel):
    """药品调价单（主表）"""
    __tablename__ = "price_adjustments"

    adjustment_no = Column(String(50), nullable=False, comment="调价单号")
    adjust_date = Column(String(20), comment="调价日期 YYYY-MM-DD")
    status = Column(String(20), default="draft", comment="状态 draft/submitted/approved")
    remark = Column(Text, comment="备注")

    __table_args__ = ({"comment": "药品调价单表"},)


class PriceAdjustmentItem(BaseModel):
    """药品调价单明细"""
    __tablename__ = "price_adjustment_items"

    adjustment_id = Column(UUID(as_uuid=True), ForeignKey("price_adjustments.id"), nullable=False, comment="调价单ID")
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    drug_name = Column(String(100), comment="药品名称")
    old_price = Column(Numeric(10, 2), default=0, comment="原价")
    new_price = Column(Numeric(10, 2), default=0, comment="新价")
    reason = Column(Text, comment="调价原因")

    __table_args__ = ({"comment": "药品调价单明细表"},)

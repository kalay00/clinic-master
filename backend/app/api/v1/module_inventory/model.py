"""
进销存模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Numeric, Integer, Text, ForeignKey, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Supplier(BaseModel):
    """供应商模型"""
    __tablename__ = "suppliers"
    
    name = Column(String(100), nullable=False, comment="供应商名称")
    code = Column(String(50), nullable=False, comment="供应商编码")
    contact_name = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    address = Column(Text, comment="地址")
    category = Column(String(50), comment="供应商分类")
    status = Column(String(20), default="active", comment="状态：active/inactive")
    remark = Column(Text, comment="备注")
    
    # 关系
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    __table_args__ = (
        {"comment": "供应商表"},
    )


class PurchaseOrder(BaseModel):
    """采购单模型"""
    __tablename__ = "purchase_orders"
    
    order_no = Column(String(50), nullable=False, unique=True, comment="采购单号")
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    order_date = Column(Date, nullable=False, comment="采购日期")
    expected_date = Column(Date, comment="预计到货日期")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    status = Column(String(20), default="draft", comment="状态：draft/approved/received/cancelled")
    remark = Column(Text, comment="备注")
    
    # 审核和入库信息
    approved_by = Column(UUID(as_uuid=True), comment="审核人ID")
    approved_at = Column(DateTime, comment="审核时间")
    received_by = Column(UUID(as_uuid=True), comment="入库人ID")
    received_at = Column(DateTime, comment="入库时间")
    
    # 关系
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"comment": "采购单表"},
    )


class PurchaseOrderItem(BaseModel):
    """采购明细模型"""
    __tablename__ = "purchase_order_items"
    
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, comment="采购单ID")
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    received_quantity = Column(Integer, default=0, comment="已入库数量")
    batch_no = Column(String(50), comment="批次号")
    expiry_date = Column(String(20), comment="有效期")
    
    # 关系
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    return_items = relationship("ReturnOrderItem", back_populates="purchase_order_item")
    
    __table_args__ = (
        {"comment": "采购明细表"},
    )


class InventoryTransaction(BaseModel):
    """库存流水模型"""
    __tablename__ = "inventory_transactions"
    
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    transaction_type = Column(String(20), nullable=False, comment="交易类型：purchase/sale/adjust/check")
    reference_id = Column(UUID(as_uuid=True), comment="关联ID（采购单ID、销售单ID等）")
    reference_type = Column(String(50), comment="关联类型：purchase_order/dispense/inventory_check")
    quantity = Column(Integer, nullable=False, comment="数量（正数入库，负数出库）")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    before_quantity = Column(Integer, default=0, comment="变动前库存")
    after_quantity = Column(Integer, default=0, comment="变动后库存")
    operator_id = Column(UUID(as_uuid=True), comment="操作人ID")
    transaction_date = Column(DateTime, nullable=False, comment="交易日期")
    remark = Column(Text, comment="备注")
    
    __table_args__ = (
        {"comment": "库存流水表"},
    )


class InventoryCheck(BaseModel):
    """库存盘点模型"""
    __tablename__ = "inventory_checks"
    
    check_no = Column(String(50), nullable=False, unique=True, comment="盘点单号")
    check_date = Column(Date, nullable=False, comment="盘点日期")
    status = Column(String(20), default="draft", comment="状态：draft/completed")
    operator_id = Column(UUID(as_uuid=True), comment="操作人ID")
    remark = Column(Text, comment="备注")
    
    # 关系
    items = relationship("InventoryCheckItem", back_populates="inventory_check", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"comment": "库存盘点表"},
    )


class InventoryCheckItem(BaseModel):
    """盘点明细模型"""
    __tablename__ = "inventory_check_items"
    
    inventory_check_id = Column(UUID(as_uuid=True), ForeignKey("inventory_checks.id"), nullable=False, comment="盘点单ID")
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    book_quantity = Column(Integer, nullable=False, comment="账面数量")
    actual_quantity = Column(Integer, nullable=False, comment="实际数量")
    difference = Column(Integer, default=0, comment="差异数量")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价")
    difference_amount = Column(Numeric(10, 2), default=0, comment="差异金额")
    remark = Column(Text, comment="备注")
    
    # 关系
    inventory_check = relationship("InventoryCheck", back_populates="items")
    
    __table_args__ = (
        {"comment": "盘点明细表"},
    )


class ReturnOrder(BaseModel):
    """退货单模型"""
    __tablename__ = "return_orders"
    
    return_no = Column(String(50), nullable=False, unique=True, comment="退货单号")
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, comment="采购单ID")
    return_date = Column(Date, nullable=False, comment="退货日期")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    status = Column(String(20), default="draft", comment="状态：draft/approved/completed/cancelled")
    remark = Column(Text, comment="备注")
    
    # 审核和执行信息
    approved_by = Column(UUID(as_uuid=True), comment="审核人ID")
    approved_at = Column(DateTime, comment="审核时间")
    completed_by = Column(UUID(as_uuid=True), comment="执行人ID")
    completed_at = Column(DateTime, comment="执行时间")
    
    # 关系
    purchase_order = relationship("PurchaseOrder", backref="return_orders")
    items = relationship("ReturnOrderItem", back_populates="return_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"comment": "退货单表"},
    )


class ReturnOrderItem(BaseModel):
    """退货明细模型"""
    __tablename__ = "return_order_items"
    
    return_order_id = Column(UUID(as_uuid=True), ForeignKey("return_orders.id"), nullable=False, comment="退货单ID")
    purchase_order_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_items.id"), nullable=False, comment="采购明细ID")
    drug_id = Column(UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    quantity = Column(Integer, nullable=False, comment="退货数量")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    batch_no = Column(String(50), comment="批次号")
    expiry_date = Column(String(20), comment="有效期")
    
    # 关系
    return_order = relationship("ReturnOrder", back_populates="items")
    purchase_order_item = relationship("PurchaseOrderItem", back_populates="return_items")
    
    __table_args__ = (
        {"comment": "退货明细表"},
    )

"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.base_schema import BaseSchema


def _coerce_user_id(v):
    """DB 中审核人/入库人/执行人等列是 UUID 类型，schema 字段为 str，
    校验时把 UUID 归一化为字符串，避免 ValidationError。"""
    return str(v) if isinstance(v, UUID) else v

from app.core.validator import DateTimeStr
from datetime import date


class SupplierSchema(BaseSchema):
    """Supplier Schema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="供应商名称")
    code: str = Field(..., comment="供应商编码")
    contact_name: Optional[str] = Field(default=None, comment="联系人")
    contact_phone: Optional[str] = Field(default=None, comment="联系电话")
    contact_email: Optional[str] = Field(default=None, comment="联系邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    category: Optional[str] = Field(default=None, comment="供应商分类")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    remark: Optional[str] = Field(default=None, comment="备注")


class SupplierCreateSchema(BaseModel):
    """Supplier CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="供应商名称")
    code: str = Field(..., comment="供应商编码")
    contact_name: Optional[str] = Field(default=None, comment="联系人")
    contact_phone: Optional[str] = Field(default=None, comment="联系电话")
    contact_email: Optional[str] = Field(default=None, comment="联系邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    category: Optional[str] = Field(default=None, comment="供应商分类")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    remark: Optional[str] = Field(default=None, comment="备注")


class SupplierUpdateSchema(BaseModel):
    """Supplier UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="供应商名称")
    code: str = Field(..., comment="供应商编码")
    contact_name: Optional[str] = Field(default=None, comment="联系人")
    contact_phone: Optional[str] = Field(default=None, comment="联系电话")
    contact_email: Optional[str] = Field(default=None, comment="联系邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    category: Optional[str] = Field(default=None, comment="供应商分类")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    remark: Optional[str] = Field(default=None, comment="备注")


class PurchaseOrderSchema(BaseSchema):
    """PurchaseOrder Schema"""

    model_config = ConfigDict(from_attributes=True)

    order_no: str = Field(..., comment="采购单号")
    supplier_id: UUID = Field(..., comment="供应商ID")
    order_date: date = Field(..., comment="采购日期")
    expected_date: Optional[date] = Field(default=None, comment="预计到货日期")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：draft/approved/received/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")
    approved_by: Optional[str] = Field(default=None, comment="审核人ID")
    approved_at: Optional[DateTimeStr] = Field(default=None, comment="审核时间")
    received_by: Optional[str] = Field(default=None, comment="入库人ID")
    received_at: Optional[DateTimeStr] = Field(default=None, comment="入库时间")

    @field_validator("approved_by", "received_by", mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_user_id(v)


class PurchaseOrderCreateSchema(BaseModel):
    """PurchaseOrder CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    order_no: str = Field(..., comment="采购单号")
    supplier_id: UUID = Field(..., comment="供应商ID")
    order_date: date = Field(..., comment="采购日期")
    expected_date: Optional[date] = Field(default=None, comment="预计到货日期")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：draft/approved/received/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")
    approved_by: Optional[str] = Field(default=None, comment="审核人ID")
    approved_at: Optional[DateTimeStr] = Field(default=None, comment="审核时间")
    received_by: Optional[str] = Field(default=None, comment="入库人ID")
    received_at: Optional[DateTimeStr] = Field(default=None, comment="入库时间")

    @field_validator("approved_by", "received_by", mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_user_id(v)


class PurchaseOrderUpdateSchema(BaseModel):
    """PurchaseOrder UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    order_no: str = Field(..., comment="采购单号")
    supplier_id: UUID = Field(..., comment="供应商ID")
    order_date: date = Field(..., comment="采购日期")
    expected_date: Optional[date] = Field(default=None, comment="预计到货日期")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：draft/approved/received/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")
    approved_by: Optional[str] = Field(default=None, comment="审核人ID")
    approved_at: Optional[DateTimeStr] = Field(default=None, comment="审核时间")
    received_by: Optional[str] = Field(default=None, comment="入库人ID")
    received_at: Optional[DateTimeStr] = Field(default=None, comment="入库时间")

    @field_validator("approved_by", "received_by", mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_user_id(v)


class PurchaseOrderItemSchema(BaseSchema):
    """PurchaseOrderItem Schema"""

    model_config = ConfigDict(from_attributes=True)

    purchase_order_id: UUID = Field(..., comment="采购单ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    received_quantity: Optional[int] = Field(default=None, comment="已入库数量")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class PurchaseOrderItemCreateSchema(BaseModel):
    """PurchaseOrderItem CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    purchase_order_id: UUID = Field(..., comment="采购单ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    received_quantity: Optional[int] = Field(default=None, comment="已入库数量")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class PurchaseOrderItemUpdateSchema(BaseModel):
    """PurchaseOrderItem UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    purchase_order_id: UUID = Field(..., comment="采购单ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    received_quantity: Optional[int] = Field(default=None, comment="已入库数量")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class InventoryTransactionSchema(BaseSchema):
    """InventoryTransaction Schema"""

    model_config = ConfigDict(from_attributes=True)

    drug_id: UUID = Field(..., comment="药品ID")
    transaction_type: str = Field(..., comment="交易类型：purchase/sale/adjust/check")
    reference_id: Optional[UUID] = Field(default=None, comment="关联ID（采购单ID、销售单ID等）")
    reference_type: Optional[str] = Field(default=None, comment="关联类型：purchase_order/dispense/inventory_check")
    quantity: int = Field(..., comment="数量（正数入库，负数出库）")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    before_quantity: Optional[int] = Field(default=None, comment="变动前库存")
    after_quantity: Optional[int] = Field(default=None, comment="变动后库存")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    transaction_date: DateTimeStr = Field(..., comment="交易日期")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryTransactionCreateSchema(BaseModel):
    """InventoryTransaction CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    drug_id: UUID = Field(..., comment="药品ID")
    transaction_type: str = Field(..., comment="交易类型：purchase/sale/adjust/check")
    reference_id: Optional[UUID] = Field(default=None, comment="关联ID（采购单ID、销售单ID等）")
    reference_type: Optional[str] = Field(default=None, comment="关联类型：purchase_order/dispense/inventory_check")
    quantity: int = Field(..., comment="数量（正数入库，负数出库）")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    before_quantity: Optional[int] = Field(default=None, comment="变动前库存")
    after_quantity: Optional[int] = Field(default=None, comment="变动后库存")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    transaction_date: DateTimeStr = Field(..., comment="交易日期")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryTransactionUpdateSchema(BaseModel):
    """InventoryTransaction UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    drug_id: UUID = Field(..., comment="药品ID")
    transaction_type: str = Field(..., comment="交易类型：purchase/sale/adjust/check")
    reference_id: Optional[UUID] = Field(default=None, comment="关联ID（采购单ID、销售单ID等）")
    reference_type: Optional[str] = Field(default=None, comment="关联类型：purchase_order/dispense/inventory_check")
    quantity: int = Field(..., comment="数量（正数入库，负数出库）")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    before_quantity: Optional[int] = Field(default=None, comment="变动前库存")
    after_quantity: Optional[int] = Field(default=None, comment="变动后库存")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    transaction_date: DateTimeStr = Field(..., comment="交易日期")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryCheckSchema(BaseSchema):
    """InventoryCheck Schema"""

    model_config = ConfigDict(from_attributes=True)

    check_no: str = Field(..., comment="盘点单号")
    check_date: date = Field(..., comment="盘点日期")
    status: Optional[str] = Field(default=None, comment="状态：draft/completed")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryCheckCreateSchema(BaseModel):
    """InventoryCheck CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    check_no: str = Field(..., comment="盘点单号")
    check_date: date = Field(..., comment="盘点日期")
    status: Optional[str] = Field(default=None, comment="状态：draft/completed")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryCheckUpdateSchema(BaseModel):
    """InventoryCheck UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    check_no: str = Field(..., comment="盘点单号")
    check_date: date = Field(..., comment="盘点日期")
    status: Optional[str] = Field(default=None, comment="状态：draft/completed")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryCheckItemSchema(BaseSchema):
    """InventoryCheckItem Schema"""

    model_config = ConfigDict(from_attributes=True)

    inventory_check_id: UUID = Field(..., comment="盘点单ID")
    drug_id: UUID = Field(..., comment="药品ID")
    book_quantity: int = Field(..., comment="账面数量")
    actual_quantity: int = Field(..., comment="实际数量")
    difference: Optional[int] = Field(default=None, comment="差异数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    difference_amount: Optional[float] = Field(default=None, comment="差异金额")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryCheckItemCreateSchema(BaseModel):
    """InventoryCheckItem CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    inventory_check_id: UUID = Field(..., comment="盘点单ID")
    drug_id: UUID = Field(..., comment="药品ID")
    book_quantity: int = Field(..., comment="账面数量")
    actual_quantity: int = Field(..., comment="实际数量")
    difference: Optional[int] = Field(default=None, comment="差异数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    difference_amount: Optional[float] = Field(default=None, comment="差异金额")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventoryCheckItemUpdateSchema(BaseModel):
    """InventoryCheckItem UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    inventory_check_id: UUID = Field(..., comment="盘点单ID")
    drug_id: UUID = Field(..., comment="药品ID")
    book_quantity: int = Field(..., comment="账面数量")
    actual_quantity: int = Field(..., comment="实际数量")
    difference: Optional[int] = Field(default=None, comment="差异数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    difference_amount: Optional[float] = Field(default=None, comment="差异金额")
    remark: Optional[str] = Field(default=None, comment="备注")


class ReturnOrderSchema(BaseSchema):
    """ReturnOrder Schema"""

    model_config = ConfigDict(from_attributes=True)

    return_no: str = Field(..., comment="退货单号")
    purchase_order_id: UUID = Field(..., comment="采购单ID")
    return_date: date = Field(..., comment="退货日期")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：draft/approved/completed/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")
    approved_by: Optional[str] = Field(default=None, comment="审核人ID")
    approved_at: Optional[DateTimeStr] = Field(default=None, comment="审核时间")
    completed_by: Optional[str] = Field(default=None, comment="执行人ID")
    completed_at: Optional[DateTimeStr] = Field(default=None, comment="执行时间")

    @field_validator("approved_by", "completed_by", mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_user_id(v)


class ReturnOrderCreateSchema(BaseModel):
    """ReturnOrder CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    return_no: str = Field(..., comment="退货单号")
    purchase_order_id: UUID = Field(..., comment="采购单ID")
    return_date: date = Field(..., comment="退货日期")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：draft/approved/completed/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")
    approved_by: Optional[str] = Field(default=None, comment="审核人ID")
    approved_at: Optional[DateTimeStr] = Field(default=None, comment="审核时间")
    completed_by: Optional[str] = Field(default=None, comment="执行人ID")
    completed_at: Optional[DateTimeStr] = Field(default=None, comment="执行时间")

    @field_validator("approved_by", "completed_by", mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_user_id(v)


class ReturnOrderUpdateSchema(BaseModel):
    """ReturnOrder UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    return_no: str = Field(..., comment="退货单号")
    purchase_order_id: UUID = Field(..., comment="采购单ID")
    return_date: date = Field(..., comment="退货日期")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：draft/approved/completed/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")
    approved_by: Optional[str] = Field(default=None, comment="审核人ID")
    approved_at: Optional[DateTimeStr] = Field(default=None, comment="审核时间")
    completed_by: Optional[str] = Field(default=None, comment="执行人ID")
    completed_at: Optional[DateTimeStr] = Field(default=None, comment="执行时间")

    @field_validator("approved_by", "completed_by", mode="before")
    @classmethod
    def _coerce(cls, v):
        return _coerce_user_id(v)


class ReturnOrderItemSchema(BaseSchema):
    """ReturnOrderItem Schema"""

    model_config = ConfigDict(from_attributes=True)

    return_order_id: UUID = Field(..., comment="退货单ID")
    purchase_order_item_id: UUID = Field(..., comment="采购明细ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="退货数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class ReturnOrderItemCreateSchema(BaseModel):
    """ReturnOrderItem CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    return_order_id: UUID = Field(..., comment="退货单ID")
    purchase_order_item_id: UUID = Field(..., comment="采购明细ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="退货数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class ReturnOrderItemUpdateSchema(BaseModel):
    """ReturnOrderItem UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    return_order_id: UUID = Field(..., comment="退货单ID")
    purchase_order_item_id: UUID = Field(..., comment="采购明细ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="退货数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")

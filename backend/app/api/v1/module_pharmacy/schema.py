"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, computed_field
from app.core.base_schema import BaseSchema


class DrugSchema(BaseSchema):
    """Drug Schema"""

    model_config = ConfigDict(from_attributes=True)

    drug_code: str = Field(..., comment="药品编码")
    name: str = Field(..., comment="药品名称")
    generic_name: Optional[str] = Field(default=None, comment="通用名")
    specification: Optional[str] = Field(default=None, comment="规格")
    unit: Optional[str] = Field(default=None, comment="单位")
    category: Optional[str] = Field(default=None, comment="药品分类")
    manufacturer: Optional[str] = Field(default=None, comment="生产厂家")
    supplier_id: Optional[UUID] = Field(default=None, comment="供应商ID")
    supplier_name: Optional[str] = Field(default=None, comment="供应商名称")
    price: Optional[float] = Field(default=None, comment="单价")
    status: Optional[str] = Field(default=None, comment="状态")

    drug_type: Optional[str] = Field(default=None, comment="药品类型")
    barcode: Optional[str] = Field(default=None, comment="药品条形码")
    pinyin_code: Optional[str] = Field(default=None, comment="拼音码")
    form: Optional[str] = Field(default=None, comment="药品剂型")
    is_otc: Optional[bool] = Field(default=None, comment="是否OTC")
    fee_item_id: Optional[str] = Field(default=None, comment="发票项目ID")
    approval_no: Optional[str] = Field(default=None, comment="批准文号")

    base_coefficient: Optional[float] = Field(default=None, comment="基本系数")
    base_unit: Optional[str] = Field(default=None, comment="基本单位")
    dose_coefficient: Optional[float] = Field(default=None, comment="剂量系数")
    dose_unit: Optional[str] = Field(default=None, comment="剂量单位")
    purchase_price: Optional[float] = Field(default=None, comment="采购价")
    allow_split: Optional[bool] = Field(default=None, comment="允许拆零")
    allow_discount: Optional[bool] = Field(default=None, comment="允许会员折扣")

    usage_id: Optional[str] = Field(default=None, comment="用法ID")
    single_dose: Optional[float] = Field(default=None, comment="单次用量")
    single_dose_unit: Optional[str] = Field(default=None, comment="单次用量单位")
    frequency_id: Optional[str] = Field(default=None, comment="频度ID")
    days: Optional[int] = Field(default=None, comment="天数")
    total_qty: Optional[float] = Field(default=None, comment="总量")
    total_unit: Optional[str] = Field(default=None, comment="总量单位")

    stock_min: Optional[int] = Field(default=None, comment="库存下限")
    stock_max: Optional[int] = Field(default=None, comment="库存上限")
    location_no: Optional[str] = Field(default=None, comment="货位号")
    expiry_warning_days: Optional[int] = Field(default=None, comment="有效期预警天数")
    description: Optional[str] = Field(default=None, comment="药品说明")
    remark: Optional[str] = Field(default=None, comment="备注")


class DrugCreateSchema(BaseModel):
    """Drug CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    drug_code: str = Field(..., comment="药品编码")
    name: str = Field(..., comment="药品名称")
    generic_name: Optional[str] = Field(default=None, comment="通用名")
    specification: Optional[str] = Field(default=None, comment="规格")
    unit: Optional[str] = Field(default=None, comment="单位")
    category: Optional[str] = Field(default=None, comment="药品分类（旧）")
    category_id: Optional[UUID] = Field(default=None, comment="药品分类ID")
    manufacturer: Optional[str] = Field(default=None, comment="生产厂家")
    supplier_id: Optional[UUID] = Field(default=None, comment="供应商ID")
    price: Optional[float] = Field(default=None, comment="单价")
    status: Optional[str] = Field(default="active", comment="状态")

    drug_type: Optional[str] = Field(default="western", comment="药品类型")
    barcode: Optional[str] = Field(default=None, comment="药品条形码")
    pinyin_code: Optional[str] = Field(default=None, comment="拼音码")
    form: Optional[str] = Field(default=None, comment="药品剂型")
    is_otc: Optional[bool] = Field(default=False, comment="是否OTC")
    fee_item_id: Optional[str] = Field(default=None, comment="发票项目ID")
    approval_no: Optional[str] = Field(default=None, comment="批准文号")

    base_coefficient: Optional[float] = Field(default=1, comment="基本系数")
    base_unit: Optional[str] = Field(default=None, comment="基本单位")
    dose_coefficient: Optional[float] = Field(default=1, comment="剂量系数")
    dose_unit: Optional[str] = Field(default=None, comment="剂量单位")
    purchase_price: Optional[float] = Field(default=0, comment="采购价")
    allow_split: Optional[bool] = Field(default=False, comment="允许拆零")
    allow_discount: Optional[bool] = Field(default=True, comment="允许会员折扣")

    usage_id: Optional[str] = Field(default=None, comment="用法ID")
    single_dose: Optional[float] = Field(default=0, comment="单次用量")
    single_dose_unit: Optional[str] = Field(default=None, comment="单次用量单位")
    frequency_id: Optional[str] = Field(default=None, comment="频度ID")
    days: Optional[int] = Field(default=1, comment="天数")
    total_qty: Optional[float] = Field(default=1, comment="总量")
    total_unit: Optional[str] = Field(default=None, comment="总量单位")

    stock_min: Optional[int] = Field(default=0, comment="库存下限")
    stock_max: Optional[int] = Field(default=0, comment="库存上限")
    location_no: Optional[str] = Field(default=None, comment="货位号")
    expiry_warning_days: Optional[int] = Field(default=30, comment="有效期预警天数")
    description: Optional[str] = Field(default=None, comment="药品说明")
    remark: Optional[str] = Field(default=None, comment="备注")


class DrugUpdateSchema(BaseModel):
    """Drug UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    drug_code: Optional[str] = Field(default=None, comment="药品编码")
    name: Optional[str] = Field(default=None, comment="药品名称")
    generic_name: Optional[str] = Field(default=None, comment="通用名")
    specification: Optional[str] = Field(default=None, comment="规格")
    unit: Optional[str] = Field(default=None, comment="单位")
    category: Optional[str] = Field(default=None, comment="药品分类（旧）")
    category_id: Optional[UUID] = Field(default=None, comment="药品分类ID")
    manufacturer: Optional[str] = Field(default=None, comment="生产厂家")
    supplier_id: Optional[UUID] = Field(default=None, comment="供应商ID")
    price: Optional[float] = Field(default=None, comment="单价")
    status: Optional[str] = Field(default=None, comment="状态")

    drug_type: Optional[str] = Field(default=None, comment="药品类型")
    barcode: Optional[str] = Field(default=None, comment="药品条形码")
    pinyin_code: Optional[str] = Field(default=None, comment="拼音码")
    form: Optional[str] = Field(default=None, comment="药品剂型")
    is_otc: Optional[bool] = Field(default=None, comment="是否OTC")
    fee_item_id: Optional[str] = Field(default=None, comment="发票项目ID")
    approval_no: Optional[str] = Field(default=None, comment="批准文号")

    base_coefficient: Optional[float] = Field(default=None, comment="基本系数")
    base_unit: Optional[str] = Field(default=None, comment="基本单位")
    dose_coefficient: Optional[float] = Field(default=None, comment="剂量系数")
    dose_unit: Optional[str] = Field(default=None, comment="剂量单位")
    purchase_price: Optional[float] = Field(default=None, comment="采购价")
    allow_split: Optional[bool] = Field(default=None, comment="允许拆零")
    allow_discount: Optional[bool] = Field(default=None, comment="允许会员折扣")

    usage_id: Optional[str] = Field(default=None, comment="用法ID")
    single_dose: Optional[float] = Field(default=None, comment="单次用量")
    single_dose_unit: Optional[str] = Field(default=None, comment="单次用量单位")
    frequency_id: Optional[str] = Field(default=None, comment="频度ID")
    days: Optional[int] = Field(default=None, comment="天数")
    total_qty: Optional[float] = Field(default=None, comment="总量")
    total_unit: Optional[str] = Field(default=None, comment="总量单位")

    stock_min: Optional[int] = Field(default=None, comment="库存下限")
    stock_max: Optional[int] = Field(default=None, comment="库存上限")
    location_no: Optional[str] = Field(default=None, comment="货位号")
    expiry_warning_days: Optional[int] = Field(default=None, comment="有效期预警天数")
    description: Optional[str] = Field(default=None, comment="药品说明")
    remark: Optional[str] = Field(default=None, comment="备注")


class InventorySchema(BaseSchema):
    """Inventory Schema"""

    model_config = ConfigDict(from_attributes=True)

    drug_id: UUID = Field(..., comment="药品ID")
    quantity: Optional[int] = Field(default=None, comment="库存数量")
    min_quantity: Optional[int] = Field(default=None, comment="最小库存")
    max_quantity: Optional[int] = Field(default=None, comment="最大库存")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class InventoryCreateSchema(BaseModel):
    """Inventory CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    drug_id: UUID = Field(..., comment="药品ID")
    quantity: Optional[int] = Field(default=None, comment="库存数量")
    min_quantity: Optional[int] = Field(default=None, comment="最小库存")
    max_quantity: Optional[int] = Field(default=None, comment="最大库存")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class InventoryUpdateSchema(BaseModel):
    """Inventory UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    drug_id: UUID = Field(..., comment="药品ID")
    quantity: Optional[int] = Field(default=None, comment="库存数量")
    min_quantity: Optional[int] = Field(default=None, comment="最小库存")
    max_quantity: Optional[int] = Field(default=None, comment="最大库存")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    batch_no: Optional[str] = Field(default=None, comment="批次号")
    expiry_date: Optional[str] = Field(default=None, comment="有效期")


class DispenseSchema(BaseSchema):
    """Dispense Schema"""

    model_config = ConfigDict(from_attributes=True)

    prescription_id: UUID = Field(..., comment="处方ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/dispensed/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")


class DispenseCreateSchema(BaseModel):
    """Dispense CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    prescription_id: UUID = Field(..., comment="处方ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/dispensed/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")


class DispenseUpdateSchema(BaseModel):
    """Dispense UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    prescription_id: UUID = Field(..., comment="处方ID")
    drug_id: UUID = Field(..., comment="药品ID")
    quantity: int = Field(..., comment="数量")
    unit_price: Optional[float] = Field(default=None, comment="单价")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/dispensed/cancelled")
    remark: Optional[str] = Field(default=None, comment="备注")


class DispenseItemSchema(BaseModel):
    """发药明细项（前端提交的单条发药药品）"""

    drug_id: str = Field(..., comment="药品ID")
    quantity: int = Field(..., ge=1, comment="发药数量")


class DispenseRequestSchema(BaseModel):
    """发药请求（按处方发药，POST /pharmacy/dispense）"""

    prescription_id: str = Field(..., comment="处方ID")
    items: List[DispenseItemSchema] = Field(..., comment="发药明细列表")


# ---------- 药品分类 ----------
class DrugCategorySchema(BaseSchema):
    """DrugCategory Schema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="分类名称")
    category_type: Optional[str] = Field(default=None, comment="处方分类 western/chinese_patent/herb/all")
    sort: int = Field(0, comment="排序")
    status: Optional[str] = Field(default=None, comment="状态")
    remark: Optional[str] = Field(default=None, comment="备注")

    @computed_field
    @property
    def creator(self) -> Optional[str]:
        user = getattr(self, "created_by_user", None)
        if user is not None:
            return getattr(user, "real_name", None) or getattr(user, "username", None)
        return None


class DrugCategoryCreateSchema(BaseModel):
    """DrugCategory CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="分类名称")
    category_type: Optional[str] = Field(default="western", comment="处方分类")
    sort: int = Field(0, comment="排序")
    status: str = Field("active", comment="状态")
    remark: Optional[str] = Field(default=None, comment="备注")


class DrugCategoryUpdateSchema(BaseModel):
    """DrugCategory UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, comment="分类名称")
    category_type: Optional[str] = Field(default=None, comment="处方分类")
    sort: Optional[int] = Field(default=None, comment="排序")
    status: Optional[str] = Field(default=None, comment="状态")
    remark: Optional[str] = Field(default=None, comment="备注")


# ---------- 药品调价 ----------
class PriceAdjustmentItemSchema(BaseModel):
    """调价单明细项"""

    model_config = ConfigDict(from_attributes=True)

    drug_id: UUID = Field(..., comment="药品ID")
    drug_name: Optional[str] = Field(default=None, comment="药品名称")
    old_price: Optional[float] = Field(default=None, comment="原价")
    new_price: float = Field(..., comment="新价")
    reason: Optional[str] = Field(default=None, comment="调价原因")


class PriceAdjustmentSchema(BaseSchema):
    """PriceAdjustment Schema"""

    model_config = ConfigDict(from_attributes=True)

    adjustment_no: Optional[str] = Field(default=None, comment="调价单号")
    adjust_date: Optional[str] = Field(default=None, comment="调价日期")
    status: Optional[str] = Field(default=None, comment="状态 draft/submitted/approved")
    remark: Optional[str] = Field(default=None, comment="备注")
    items: List[PriceAdjustmentItemSchema] = Field(default_factory=list, comment="明细")


class PriceAdjustmentCreateSchema(BaseModel):
    """PriceAdjustment CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    adjust_date: Optional[str] = Field(default=None, comment="调价日期")
    remark: Optional[str] = Field(default=None, comment="备注")
    items: List[PriceAdjustmentItemSchema] = Field(..., comment="明细")

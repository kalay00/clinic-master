"""
账单明细服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.bill_item_repository import BillItemRepository
from app.api.v1.module_payment.model import BillItem
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class BillItemService:
    """账单明细服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.bill_item_repo = BillItemRepository(db)
    
    def create_bill_item(
        self,
        item_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> BillItem:
        """创建账单明细"""
        # 转换UUID字段
        if "bill_id" in item_data:
            if isinstance(item_data["bill_id"], str):
                from uuid import UUID
                item_data["bill_id"] = UUID(item_data["bill_id"])
        
        # 计算总价
        if "quantity" in item_data and "unit_price" in item_data:
            item_data["total_price"] = float(item_data["quantity"]) * float(item_data["unit_price"])
        
        item = self.bill_item_repo.create_bill_item(item_data, tenant_id)
        if creator_id:
            from uuid import UUID
            item.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        logger.info(f"创建账单明细: {item.id} by {creator_id}")
        return item
    
    def get_bill_item(self, item_id: str, tenant_id: str) -> BillItem:
        """获取账单明细详情"""
        item = self.bill_item_repo.get_bill_item_by_id(item_id, tenant_id)
        if not item:
            raise NotFoundException("账单明细", item_id)
        return item
    
    def get_bill_items_by_bill(
        self,
        bill_id: str,
        tenant_id: str
    ) -> List[BillItem]:
        """根据账单ID获取明细列表"""
        return self.bill_item_repo.get_bill_items_by_bill(bill_id, tenant_id)
    
    def update_bill_item(
        self,
        item_id: str,
        tenant_id: str,
        item_data: Dict[str, Any],
        updater_id: str
    ) -> BillItem:
        """更新账单明细"""
        # 重新计算总价
        if "quantity" in item_data or "unit_price" in item_data:
            item = self.bill_item_repo.get_bill_item_by_id(item_id, tenant_id)
            if not item:
                raise NotFoundException("账单明细", item_id)
            
            quantity = item_data.get("quantity", item.quantity)
            unit_price = item_data.get("unit_price", item.unit_price)
            item_data["total_price"] = float(quantity) * float(unit_price)
        
        item = self.bill_item_repo.update_bill_item(item_id, tenant_id, item_data)
        if updater_id:
            from uuid import UUID
            item.updated_by = UUID(updater_id) if isinstance(updater_id, str) else updater_id
        self.db.commit()
        return item
    
    def delete_bill_item(self, item_id: str, tenant_id: str) -> bool:
        """删除账单明细（软删除）"""
        return self.bill_item_repo.delete_bill_item(item_id, tenant_id)


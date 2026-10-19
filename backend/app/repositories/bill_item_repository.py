"""
账单明细数据仓库
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from app.api.v1.module_payment.model import BillItem
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class BillItemRepository:
    """账单明细数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_bill_item(self, item_data: dict, tenant_id: str) -> BillItem:
        """创建账单明细"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        item = BillItem(
            tenant_id=tenant_id,
            **item_data
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_bill_item_by_id(
        self,
        item_id: str,
        tenant_id: str
    ) -> Optional[BillItem]:
        """根据ID获取账单明细"""
        if isinstance(item_id, str):
            item_id = UUID(item_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(BillItem).filter(
            and_(
                BillItem.id == item_id,
                BillItem.tenant_id == tenant_id,
                BillItem.deleted_at.is_(None)
            )
        ).first()
    
    def get_bill_items_by_bill(
        self,
        bill_id: str,
        tenant_id: str
    ) -> List[BillItem]:
        """根据账单ID获取明细列表"""
        if isinstance(bill_id, str):
            bill_id = UUID(bill_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(BillItem).filter(
            and_(
                BillItem.bill_id == bill_id,
                BillItem.tenant_id == tenant_id,
                BillItem.deleted_at.is_(None)
            )
        ).all()
    
    def update_bill_item(
        self,
        item_id: str,
        tenant_id: str,
        item_data: dict
    ) -> BillItem:
        """更新账单明细"""
        item = self.get_bill_item_by_id(item_id, tenant_id)
        if not item:
            raise NotFoundException("账单明细", item_id)
        
        for key, value in item_data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete_bill_item(self, item_id: str, tenant_id: str) -> bool:
        """删除账单明细（软删除）"""
        item = self.get_bill_item_by_id(item_id, tenant_id)
        if not item:
            raise NotFoundException("账单明细", item_id)
        
        item.deleted_at = datetime.now()
        self.db.commit()
        return True


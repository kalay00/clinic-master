"""
药房数据仓库：药品、库存、发药的数据操作
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.api.v1.module_pharmacy.model import Drug, Inventory, Dispense
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class DrugRepository:
    """药品数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_drug(self, drug_data: dict, tenant_id: str) -> Drug:
        """创建药品"""
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        drug = Drug(
            tenant_id=tenant_id_uuid,
            **drug_data
        )
        self.db.add(drug)
        self.db.commit()
        self.db.refresh(drug)
        return drug
    
    def get_drug_by_id(self, drug_id: str, tenant_id: str) -> Optional[Drug]:
        """根据ID获取药品"""
        from uuid import UUID
        
        # 转换ID为UUID
        if isinstance(drug_id, str):
            try:
                drug_id_uuid = UUID(drug_id)
            except (ValueError, TypeError):
                drug_id_uuid = drug_id
        else:
            drug_id_uuid = drug_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Drug).filter(
            and_(
                Drug.id == drug_id_uuid,
                Drug.tenant_id == tenant_id_uuid,
                Drug.deleted_at.is_(None)
            )
        ).first()
    
    def get_drugs(
        self,
        tenant_id: str,
        search: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Drug], int]:
        """获取药品列表"""
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Drug).filter(
            and_(
                Drug.tenant_id == tenant_id_uuid,
                Drug.deleted_at.is_(None)
            )
        )
        
        if search:
            query = query.filter(
                or_(
                    Drug.name.ilike(f"%{search}%"),
                    Drug.generic_name.ilike(f"%{search}%"),
                    Drug.drug_code.ilike(f"%{search}%")
                )
            )
        if category:
            query = query.filter(Drug.category == category)
        
        total = query.count()
        drugs = query.offset(skip).limit(limit).all()
        return drugs, total


class InventoryRepository:
    """库存数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_inventory_by_drug(self, drug_id: str, tenant_id: str) -> Optional[Inventory]:
        """根据药品ID获取库存"""
        from uuid import UUID
        
        # 转换ID为UUID
        if isinstance(drug_id, str):
            try:
                drug_id_uuid = UUID(drug_id)
            except (ValueError, TypeError):
                drug_id_uuid = drug_id
        else:
            drug_id_uuid = drug_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Inventory).filter(
            and_(
                Inventory.drug_id == drug_id_uuid,
                Inventory.tenant_id == tenant_id_uuid,
                Inventory.deleted_at.is_(None)
            )
        ).first()
    
    def update_inventory(self, drug_id: str, tenant_id: str, quantity_change: int) -> Inventory:
        """更新库存"""
        from uuid import UUID
        
        # 转换ID为UUID
        if isinstance(drug_id, str):
            try:
                drug_id_uuid = UUID(drug_id)
            except (ValueError, TypeError):
                drug_id_uuid = drug_id
        else:
            drug_id_uuid = drug_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        inventory = self.get_inventory_by_drug(str(drug_id_uuid), str(tenant_id_uuid))
        
        if not inventory:
            # 创建新库存记录
            inventory = Inventory(
                tenant_id=tenant_id_uuid,
                drug_id=drug_id_uuid,
                quantity=quantity_change
            )
            self.db.add(inventory)
        else:
            # 更新库存
            new_quantity = inventory.quantity + quantity_change
            if new_quantity < 0:
                raise BusinessException("库存不足", code=400)
            inventory.quantity = new_quantity
        
        self.db.commit()
        self.db.refresh(inventory)
        return inventory
    
    def get_low_stock_drugs(self, tenant_id: str) -> List[Inventory]:
        """获取低库存药品（当前库存小于等于最小库存，且最小库存大于0）"""
        from uuid import UUID
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Inventory).filter(
            and_(
                Inventory.tenant_id == tenant_id_uuid,
                Inventory.quantity <= Inventory.min_quantity,
                Inventory.min_quantity > 0,  # 最小库存必须大于0才报警
                Inventory.deleted_at.is_(None)
            )
        ).all()
    
    def get_all_inventories(self, tenant_id: str) -> List[Inventory]:
        """获取所有库存记录（用于过期检查）"""
        from uuid import UUID
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Inventory).filter(
            and_(
                Inventory.tenant_id == tenant_id_uuid,
                Inventory.deleted_at.is_(None)
            )
        ).all()

    def get_inventories_by_drug_ids(self, drug_ids: List[str], tenant_id: str) -> dict:
        """批量获取多个药品的库存信息"""
        from uuid import UUID
        
        if not drug_ids:
            return {}
        
        # 转换ID为UUID
        drug_id_uuids = []
        for drug_id in drug_ids:
            if isinstance(drug_id, str):
                try:
                    drug_id_uuids.append(UUID(drug_id))
                except (ValueError, TypeError):
                    continue
            else:
                drug_id_uuids.append(drug_id)
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        if not drug_id_uuids:
            return {}
        
        inventories = self.db.query(Inventory).filter(
            and_(
                Inventory.drug_id.in_(drug_id_uuids),
                Inventory.tenant_id == tenant_id_uuid,
                Inventory.deleted_at.is_(None)
            )
        ).all()
        
        # 转换为字典，key为drug_id的字符串形式
        result = {}
        for inv in inventories:
            result[str(inv.drug_id)] = inv
        
        return result


class DispenseRepository:
    """发药数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_dispense(self, dispense_data: dict, tenant_id: str) -> Dispense:
        """创建发药记录"""
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        dispense = Dispense(
            tenant_id=tenant_id_uuid,
            **dispense_data
        )
        self.db.add(dispense)
        self.db.commit()
        self.db.refresh(dispense)
        return dispense
    
    def get_dispenses(
        self,
        tenant_id: str,
        prescription_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Dispense], int]:
        """获取发药记录列表"""
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Dispense).filter(
            and_(
                Dispense.tenant_id == tenant_id_uuid,
                Dispense.deleted_at.is_(None)
            )
        )
        
        if prescription_id:
            if isinstance(prescription_id, str):
                try:
                    prescription_id_uuid = UUID(prescription_id)
                except (ValueError, TypeError):
                    prescription_id_uuid = prescription_id
            else:
                prescription_id_uuid = prescription_id
            query = query.filter(Dispense.prescription_id == prescription_id_uuid)
        
        total = query.count()
        dispenses = query.order_by(Dispense.created_at.desc()).offset(skip).limit(limit).all()
        return dispenses, total


"""
药房服务：药品管理、库存管理、发药管理
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.api.v1.module_pharmacy.model import Drug, Inventory, Dispense
from app.repositories.pharmacy_repository import (
    DrugRepository,
    InventoryRepository,
    DispenseRepository
)
from app.services.tenant_service import TenantService
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class PharmacyService:
    """药房服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.drug_repo = DrugRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.dispense_repo = DispenseRepository(db)
        self.tenant_service = TenantService(db)
    
    # 药品管理
    def create_drug(self, drug_data: Dict[str, Any], tenant_id: str, creator_id: str) -> Drug:
        """创建药品"""
        drug = self.drug_repo.create_drug(drug_data, tenant_id)
        drug.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建药品: {drug.id} by {creator_id}")
        return drug
    
    def get_drug(self, drug_id: str, tenant_id: str) -> Drug:
        """获取药品详情"""
        drug = self.drug_repo.get_drug_by_id(drug_id, tenant_id)
        if not drug:
            raise NotFoundException("药品", drug_id)
        return drug
    
    def list_drugs(
        self,
        tenant_id: str,
        search: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Drug], int]:
        """获取药品列表"""
        return self.drug_repo.get_drugs(tenant_id, search, category, skip, limit)
    
    # 库存管理
    def get_inventories_by_drug_ids(self, drug_ids: List[str], tenant_id: str) -> dict:
        """批量获取多个药品的库存信息"""
        return self.inventory_repo.get_inventories_by_drug_ids(drug_ids, tenant_id)
    
    def get_inventory(self, drug_id: str, tenant_id: str) -> Inventory:
        """获取库存"""
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
        
        inventory = self.inventory_repo.get_inventory_by_drug(str(drug_id_uuid), str(tenant_id_uuid))
        if not inventory:
            # 返回默认库存（不保存到数据库）
            return Inventory(
                tenant_id=tenant_id_uuid,
                drug_id=drug_id_uuid,
                quantity=0,
                min_quantity=0,
                max_quantity=0
            )
        return inventory
    
    def update_inventory(
        self,
        drug_id: str,
        tenant_id: str,
        quantity_change: int,
        operator_id: str
    ) -> Inventory:
        """更新库存（入库/出库）"""
        inventory = self.inventory_repo.update_inventory(drug_id, tenant_id, quantity_change)
        inventory.updated_by = operator_id
        self.db.commit()
        
        logger.info(f"更新库存: {drug_id}, 变化: {quantity_change} by {operator_id}")
        return inventory
    
    def get_low_stock_drugs(self, tenant_id: str) -> List[Inventory]:
        """获取低库存药品"""
        return self.inventory_repo.get_low_stock_drugs(tenant_id)
    
    def get_inventory_warnings(self, tenant_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取库存预警信息
        
        返回低库存、过期、即将过期的药品列表
        """
        from datetime import date, timedelta
        
        try:
            logger.info(f"开始获取库存预警 - tenant_id: {tenant_id}, type: {type(tenant_id)}")
            
            # 获取低库存药品
            low_stock_inventories = self.inventory_repo.get_low_stock_drugs(tenant_id)
            logger.info(f"低库存药品数量: {len(low_stock_inventories)}")
            
            low_stock_list = []
            for inv in low_stock_inventories:
                try:
                    drug = self.drug_repo.get_drug_by_id(str(inv.drug_id), tenant_id)
                    if drug:
                        low_stock_list.append({
                            "drug_id": str(inv.drug_id),
                            "drug_code": drug.drug_code,
                            "drug_name": drug.name,
                            "specification": drug.specification,
                            "current_quantity": inv.quantity,
                            "min_quantity": inv.min_quantity,
                            "unit": drug.unit or ""
                        })
                except Exception as e:
                    logger.warning(f"处理低库存药品失败: drug_id={inv.drug_id}, error={str(e)}")
                    continue
            
            # 获取过期和即将过期的药品（基于expiry_date字段）
            expired_list = []
            expiring_soon_list = []
            
            # 查询所有库存记录
            all_inventories = self.inventory_repo.get_all_inventories(tenant_id)
            logger.info(f"所有库存记录数量: {len(all_inventories)}")
            
            today = date.today()
            warning_days = 30  # 30天内过期视为即将过期
            
            for inv in all_inventories:
                try:
                    if hasattr(inv, 'expiry_date') and inv.expiry_date:
                        try:
                            if isinstance(inv.expiry_date, str):
                                expiry_date = date.fromisoformat(inv.expiry_date)
                            else:
                                expiry_date = inv.expiry_date
                            
                            drug = self.drug_repo.get_drug_by_id(str(inv.drug_id), tenant_id)
                            if not drug:
                                continue
                            
                            drug_info = {
                                "drug_id": str(inv.drug_id),
                                "drug_code": drug.drug_code,
                                "drug_name": drug.name,
                                "specification": drug.specification,
                                "current_quantity": inv.quantity,
                                "expiry_date": expiry_date.isoformat() if isinstance(expiry_date, date) else str(expiry_date),
                                "unit": drug.unit or ""
                            }
                            
                            if expiry_date < today:
                                # 已过期
                                expired_list.append(drug_info)
                            elif expiry_date <= today + timedelta(days=warning_days):
                                # 即将过期（30天内）
                                days_until_expiry = (expiry_date - today).days
                                drug_info["days_until_expiry"] = days_until_expiry
                                expiring_soon_list.append(drug_info)
                        except Exception as e:
                            logger.warning(f"处理库存过期日期失败: drug_id={inv.drug_id}, error={str(e)}")
                            continue
                except Exception as e:
                    logger.warning(f"处理库存记录失败: inv_id={inv.id if hasattr(inv, 'id') else 'unknown'}, error={str(e)}")
                    continue
            
            result = {
                "low_stock": low_stock_list,
                "expired": expired_list,
                "expiring_soon": expiring_soon_list
            }
            
            logger.info(f"库存预警获取完成 - low_stock: {len(low_stock_list)}, expired: {len(expired_list)}, expiring_soon: {len(expiring_soon_list)}")
            
            return result
        except Exception as e:
            logger.error(f"获取库存预警失败: {str(e)}", exc_info=True)
            raise
    
    # 发药管理
    def dispense_prescription(
        self,
        prescription_id: str,
        tenant_id: str,
        dispense_items: List[Dict[str, Any]],
        operator_id: str
    ) -> List[Dispense]:
        """
        发药
        
        如果药师审核开关关闭，用药禁忌默认审核通过
        """
        # 检查药师审核开关状态
        pharmacist_review_enabled = self.tenant_service.is_pharmacist_review_enabled(tenant_id)
        
        if not pharmacist_review_enabled:
            logger.info(f"药师审核已关闭，用药禁忌自动审核通过 - 租户: {tenant_id}")
        
        dispense_records = []
        
        for item in dispense_items:
            drug_id = item["drug_id"]
            quantity = item["quantity"]
            
            # 检查库存
            inventory = self.get_inventory(drug_id, tenant_id)
            if inventory.quantity < quantity:
                raise BusinessException(f"药品库存不足: {drug_id}", code=400)
            
            # 检查用药禁忌（如果药师审核开启）
            if pharmacist_review_enabled:
                # TODO: 在这里添加用药禁忌检查逻辑
                # 例如：检查药物相互作用、过敏史等
                # 如果需要药师审核，可以抛出异常或返回待审核状态
                pass
            # 如果药师审核关闭，用药禁忌默认审核通过，直接继续
            
            # 创建发药记录
            drug = self.get_drug(drug_id, tenant_id)
            unit_price = drug.price if drug.price else 0
            total_amount = unit_price * quantity
            
            dispense_data = {
                "prescription_id": prescription_id,
                "drug_id": drug_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": total_amount,
                "status": "dispensed" if not pharmacist_review_enabled else "pending"  # 如果审核开启，状态为待审核
            }
            
            # 如果药师审核关闭，添加备注说明自动审核通过
            if not pharmacist_review_enabled:
                dispense_data["remark"] = "用药禁忌自动审核通过（药师审核已关闭）"
            
            dispense = self.dispense_repo.create_dispense(dispense_data, tenant_id)
            dispense.created_by = operator_id
            dispense_records.append(dispense)
            
            # 更新库存（出库）
            self.update_inventory(drug_id, tenant_id, -quantity, operator_id)
        
        # 更新处方状态为已发药（如果所有发药记录都成功）
        if dispense_records:
            try:
                from app.services.treatment_service import TreatmentService
                treatment_service = TreatmentService(self.db)
                # 更新处方状态为已发药
                treatment_service.update_prescription(
                    prescription_id=prescription_id,
                    tenant_id=tenant_id,
                    prescription_data={"status": "dispensed"},
                    updater_id=operator_id
                )
                logger.info(f"处方状态已更新为已发药: {prescription_id}")
            except Exception as e:
                logger.warning(f"更新处方状态失败: {str(e)}，但发药记录已创建")
        
        self.db.commit()
        
        logger.info(f"发药: {prescription_id} by {operator_id}, 药师审核: {'开启' if pharmacist_review_enabled else '关闭'}")
        return dispense_records
    
    def list_dispenses(
        self,
        tenant_id: str,
        prescription_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Dispense], int]:
        """获取发药记录列表"""
        return self.dispense_repo.get_dispenses(tenant_id, prescription_id, skip, limit)


"""
进销存模块功能测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.api.v1.module_inventory.model import Supplier, PurchaseOrder, PurchaseOrderItem
from app.api.v1.module_pharmacy.model import Drug, Inventory
from app.api.v1.module_tenant.model import Tenant
from app.api.v1.module_user.model import User
from uuid import uuid4
from datetime import date, datetime

def test_inventory_module():
    """测试进销存模块功能"""
    print("=" * 60)
    print("进销存模块功能测试")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. 测试供应商管理
        print("\n1. 测试供应商管理...")
        test_supplier = Supplier(
            id=uuid4(),
            tenant_id=uuid4(),
            name="测试供应商",
            code="SUP001",
            contact_name="张三",
            contact_phone="13800138000",
            status="active"
        )
        db.add(test_supplier)
        db.commit()
        print("✅ 供应商创建成功")
        
        # 2. 测试采购单创建
        print("\n2. 测试采购单创建...")
        test_order = PurchaseOrder(
            id=uuid4(),
            tenant_id=test_supplier.tenant_id,
            order_no="PO202412190001",
            supplier_id=test_supplier.id,
            order_date=date.today(),
            status="draft",
            total_amount=1000.0
        )
        db.add(test_order)
        db.commit()
        print("✅ 采购单创建成功")
        
        # 3. 测试采购明细创建
        print("\n3. 测试采购明细创建...")
        test_drug = db.query(Drug).first()
        if test_drug:
            test_item = PurchaseOrderItem(
                id=uuid4(),
                tenant_id=test_supplier.tenant_id,
                purchase_order_id=test_order.id,
                drug_id=test_drug.id,
                quantity=10,
                unit_price=50.0,
                total_amount=500.0
            )
            db.add(test_item)
            db.commit()
            print("✅ 采购明细创建成功")
        else:
            print("⚠️  未找到药品数据，跳过采购明细测试")
        
        print("\n" + "=" * 60)
        print("进销存模块基础功能测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_inventory_module()


"""
进销存模块API测试脚本
"""
import requests
import json
from datetime import date, datetime
from uuid import uuid4

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
TEST_TENANT_ID = None
TEST_USER_TOKEN = None
TEST_SUPPLIER_ID = None
TEST_PURCHASE_ORDER_ID = None
TEST_DRUG_ID = None
TEST_CHECK_ID = None

def login():
    """登录获取Token"""
    global TEST_USER_TOKEN, TEST_TENANT_ID
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "admin",
        "password": "admin123",
        "tenant_id": "default"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                TEST_USER_TOKEN = result["data"]["access_token"]
                TEST_TENANT_ID = result["data"].get("tenant_id")
                print("✅ 登录成功")
                return True
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return False

def get_headers():
    """获取请求头"""
    return {
        "Authorization": f"Bearer {TEST_USER_TOKEN}",
        "Content-Type": "application/json"
    }

def test_suppliers():
    """测试供应商管理"""
    print("\n" + "=" * 60)
    print("测试供应商管理")
    print("=" * 60)
    
    global TEST_SUPPLIER_ID
    
    # 1. 创建供应商
    print("\n1. 测试创建供应商...")
    url = f"{BASE_URL}/inventory/suppliers"
    data = {
        "name": "测试供应商",
        "code": f"SUP{uuid4().hex[:8].upper()}",
        "contact_name": "张三",
        "contact_phone": "13800138000",
        "contact_email": "test@example.com",
        "address": "测试地址",
        "category": "药品供应商",
        "status": "active"
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("code") in [200, 201]:
                TEST_SUPPLIER_ID = result["data"]["id"]
                print(f"✅ 创建供应商成功: {TEST_SUPPLIER_ID}")
            else:
                print(f"❌ 创建供应商失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 创建供应商失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建供应商异常: {str(e)}")
        return False
    
    # 2. 获取供应商列表
    print("\n2. 测试获取供应商列表...")
    url = f"{BASE_URL}/inventory/suppliers"
    params = {"skip": 0, "limit": 10}
    
    try:
        response = requests.get(url, params=params, headers=get_headers())
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                items = result["data"].get("items", [])
                print(f"✅ 获取供应商列表成功: 共 {len(items)} 条")
                return True
            else:
                print(f"❌ 获取供应商列表失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 获取供应商列表失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取供应商列表异常: {str(e)}")
        return False
    
    # 3. 获取供应商详情
    if TEST_SUPPLIER_ID:
        print("\n3. 测试获取供应商详情...")
        url = f"{BASE_URL}/inventory/suppliers/{TEST_SUPPLIER_ID}"
        
        try:
            response = requests.get(url, headers=get_headers())
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print(f"✅ 获取供应商详情成功")
                    return True
                else:
                    print(f"❌ 获取供应商详情失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 获取供应商详情失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 获取供应商详情异常: {str(e)}")
            return False
    
    return True

def get_drug_id():
    """获取一个药品ID"""
    global TEST_DRUG_ID
    
    url = f"{BASE_URL}/pharmacy/drugs"
    params = {"skip": 0, "limit": 1}
    
    try:
        response = requests.get(url, params=params, headers=get_headers())
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                items = result["data"].get("items", [])
                if items:
                    TEST_DRUG_ID = items[0]["id"]
                    return TEST_DRUG_ID
    except Exception as e:
        print(f"⚠️  获取药品ID失败: {str(e)}")
    
    return None

def test_purchase_orders():
    """测试采购单管理"""
    print("\n" + "=" * 60)
    print("测试采购单管理")
    print("=" * 60)
    
    global TEST_PURCHASE_ORDER_ID, TEST_SUPPLIER_ID, TEST_DRUG_ID
    
    # 确保有供应商ID
    if not TEST_SUPPLIER_ID:
        print("⚠️  未找到供应商ID，先创建供应商...")
        if not test_suppliers():
            print("❌ 无法创建供应商，跳过采购单测试")
            return False
    
    # 获取药品ID
    if not TEST_DRUG_ID:
        print("⚠️  获取药品ID...")
        TEST_DRUG_ID = get_drug_id()
        if not TEST_DRUG_ID:
            print("❌ 未找到药品，跳过采购单测试")
            return False
    
    # 1. 创建采购单
    print("\n1. 测试创建采购单...")
    url = f"{BASE_URL}/inventory/purchase-orders"
    data = {
        "supplier_id": TEST_SUPPLIER_ID,
        "order_date": str(date.today()),
        "expected_date": str(date.today()),
        "items": [
            {
                "drug_id": TEST_DRUG_ID,
                "quantity": 10,
                "unit_price": 50.0,
                "batch_no": "BATCH001",
                "expiry_date": "2025-12-31"
            }
        ],
        "remark": "测试采购单"
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("code") in [200, 201]:
                TEST_PURCHASE_ORDER_ID = result["data"]["id"]
                print(f"✅ 创建采购单成功: {TEST_PURCHASE_ORDER_ID}")
            else:
                print(f"❌ 创建采购单失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 创建采购单失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建采购单异常: {str(e)}")
        return False
    
    # 2. 获取采购单列表
    print("\n2. 测试获取采购单列表...")
    url = f"{BASE_URL}/inventory/purchase-orders"
    params = {"skip": 0, "limit": 10}
    
    try:
        response = requests.get(url, params=params, headers=get_headers())
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                items = result["data"].get("items", [])
                print(f"✅ 获取采购单列表成功: 共 {len(items)} 条")
            else:
                print(f"❌ 获取采购单列表失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 获取采购单列表失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取采购单列表异常: {str(e)}")
        return False
    
    # 3. 审核采购单
    if TEST_PURCHASE_ORDER_ID:
        print("\n3. 测试审核采购单...")
        url = f"{BASE_URL}/inventory/purchase-orders/{TEST_PURCHASE_ORDER_ID}/approve"
        
        try:
            response = requests.post(url, headers=get_headers())
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print(f"✅ 审核采购单成功")
                else:
                    print(f"❌ 审核采购单失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 审核采购单失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 审核采购单异常: {str(e)}")
            return False
        
        # 4. 入库采购单
        print("\n4. 测试入库采购单...")
        url = f"{BASE_URL}/inventory/purchase-orders/{TEST_PURCHASE_ORDER_ID}/receive"
        
        try:
            response = requests.post(url, headers=get_headers())
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print(f"✅ 入库采购单成功")
                else:
                    print(f"❌ 入库采购单失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 入库采购单失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 入库采购单异常: {str(e)}")
            return False
    
    return True

def test_transactions():
    """测试库存流水"""
    print("\n" + "=" * 60)
    print("测试库存流水")
    print("=" * 60)
    
    # 获取库存流水列表
    print("\n1. 测试获取库存流水列表...")
    url = f"{BASE_URL}/inventory/transactions"
    params = {"skip": 0, "limit": 10}
    
    try:
        response = requests.get(url, params=params, headers=get_headers())
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                items = result["data"].get("items", [])
                print(f"✅ 获取库存流水列表成功: 共 {len(items)} 条")
                return True
            else:
                print(f"❌ 获取库存流水列表失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 获取库存流水列表失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取库存流水列表异常: {str(e)}")
        return False

def test_inventory_checks():
    """测试库存盘点"""
    print("\n" + "=" * 60)
    print("测试库存盘点")
    print("=" * 60)
    
    global TEST_CHECK_ID, TEST_DRUG_ID
    
    # 获取药品ID
    if not TEST_DRUG_ID:
        TEST_DRUG_ID = get_drug_id()
        if not TEST_DRUG_ID:
            print("❌ 未找到药品，跳过盘点测试")
            return False
    
    # 1. 创建盘点单
    print("\n1. 测试创建盘点单...")
    url = f"{BASE_URL}/inventory/checks"
    data = {
        "check_date": str(date.today()),
        "items": [
            {
                "drug_id": TEST_DRUG_ID,
                "actual_quantity": 15
            }
        ],
        "remark": "测试盘点单"
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("code") in [200, 201]:
                TEST_CHECK_ID = result["data"]["id"]
                print(f"✅ 创建盘点单成功: {TEST_CHECK_ID}")
            else:
                print(f"❌ 创建盘点单失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 创建盘点单失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建盘点单异常: {str(e)}")
        return False
    
    # 2. 完成盘点
    if TEST_CHECK_ID:
        print("\n2. 测试完成盘点...")
        url = f"{BASE_URL}/inventory/checks/{TEST_CHECK_ID}/complete"
        
        try:
            response = requests.post(url, headers=get_headers())
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print(f"✅ 完成盘点成功")
                else:
                    print(f"❌ 完成盘点失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 完成盘点失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 完成盘点异常: {str(e)}")
            return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("进销存模块API测试")
    print("=" * 60)
    
    # 登录
    if not login():
        print("❌ 登录失败，无法继续测试")
        return
    
    # 测试结果
    results = []
    
    # 测试供应商管理
    results.append(("供应商管理", test_suppliers()))
    
    # 测试采购单管理
    results.append(("采购单管理", test_purchase_orders()))
    
    # 测试库存流水
    results.append(("库存流水", test_transactions()))
    
    # 测试库存盘点
    results.append(("库存盘点", test_inventory_checks()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed + failed} 项测试")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    print(f"通过率: {passed / (passed + failed) * 100:.1f}%")

if __name__ == "__main__":
    main()


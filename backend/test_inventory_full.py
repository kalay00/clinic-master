"""
进销存模块完整测试脚本
包含完整的采购流程、盘点流程和数据一致性测试
"""
import requests
import json
from datetime import date, datetime
from uuid import uuid4
from app.core.database import engine, SessionLocal
from sqlalchemy import text

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
TEST_TENANT_ID = None
TEST_USER_TOKEN = None
TEST_SUPPLIER_ID = None
TEST_PURCHASE_ORDER_ID = None
TEST_DRUG_ID = None
TEST_CHECK_ID = None

def setup_test_data():
    """设置测试数据（创建租户、用户、药品）"""
    global TEST_TENANT_ID, TEST_DRUG_ID
    
    db = SessionLocal()
    try:
        with engine.begin() as conn:
            # 检查是否有租户
            result = conn.execute(text("SELECT id FROM tenants LIMIT 1"))
            row = result.fetchone()
            
            if not row:
                # 创建测试租户
                tenant_id = uuid4()
                conn.execute(text(f"""
                    INSERT INTO tenants (id, name, code, type, status)
                    VALUES ('{tenant_id}', '测试诊所', 'TEST001', 'clinic', 'active')
                """))
                TEST_TENANT_ID = str(tenant_id)
                print(f"✅ 创建测试租户: {TEST_TENANT_ID}")
            else:
                TEST_TENANT_ID = str(row[0])
                print(f"✅ 使用现有租户: {TEST_TENANT_ID}")
            
            # 检查是否有用户
            result = conn.execute(text(f"SELECT id FROM users WHERE tenant_id = '{TEST_TENANT_ID}' LIMIT 1"))
            user_row = result.fetchone()
            
            if not user_row:
                # 创建测试用户
                try:
                    import bcrypt
                    user_id = uuid4()
                    password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
                    conn.execute(text(f"""
                        INSERT INTO users (id, tenant_id, username, password_hash, real_name, status)
                        VALUES ('{user_id}', '{TEST_TENANT_ID}', 'admin', '{password_hash}', '管理员', 'active')
                    """))
                    print(f"✅ 创建测试用户: admin/admin123")
                except Exception as e:
                    print(f"⚠️  使用UserService创建用户失败: {str(e)}")
                    # 备用方案
                    import bcrypt
                    user_id = uuid4()
                    password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
                    conn.execute(text(f"""
                        INSERT INTO users (id, tenant_id, username, password_hash, real_name, status)
                        VALUES ('{user_id}', '{TEST_TENANT_ID}', 'admin', '{password_hash}', '管理员', 'active')
                    """))
                    print(f"✅ 创建测试用户（备用方案）: admin/admin123")
            
            # 检查是否有药品（先检查表是否存在）
            try:
                result = conn.execute(text(f"SELECT id FROM drugs WHERE tenant_id = '{TEST_TENANT_ID}' LIMIT 1"))
                drug_row = result.fetchone()
            except:
                drug_row = None
            
            if not drug_row:
                # 创建测试药品
                drug_id = uuid4()
                conn.execute(text(f"""
                    INSERT INTO drugs (id, tenant_id, drug_code, name, specification, unit, price, status)
                    VALUES ('{drug_id}', '{TEST_TENANT_ID}', 'DRUG001', '测试药品', '10mg', '盒', 50.00, 'active')
                """))
                TEST_DRUG_ID = str(drug_id)
                print(f"✅ 创建测试药品: {TEST_DRUG_ID}")
                
                # 创建初始库存
                inventory_id = uuid4()
                conn.execute(text(f"""
                    INSERT INTO inventory (id, tenant_id, drug_id, quantity, min_quantity, max_quantity, unit_price)
                    VALUES ('{inventory_id}', '{TEST_TENANT_ID}', '{drug_id}', 100, 10, 1000, 50.00)
                """))
                print(f"✅ 创建初始库存: 100")
            else:
                TEST_DRUG_ID = str(drug_row[0])
                print(f"✅ 使用现有药品: {TEST_DRUG_ID}")
    except Exception as e:
        print(f"⚠️  设置测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def login():
    """登录获取Token"""
    global TEST_USER_TOKEN, TEST_TENANT_ID
    
    setup_test_data()
    
    if not TEST_TENANT_ID:
        print("❌ 无法获取租户ID")
        return False
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": "admin",
        "password": "admin123",
        "tenant_id": TEST_TENANT_ID
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                TEST_USER_TOKEN = result["data"]["access_token"]
                print("✅ 登录成功")
                return True
        print(f"❌ 登录失败: {response.status_code} - {response.text[:200]}")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务已启动")
        print("   启动命令: cd backend && uvicorn app.main:app --reload")
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

def get_inventory_from_db(drug_id):
    """从数据库获取库存"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT quantity FROM inventory 
                WHERE drug_id = '{drug_id}' AND tenant_id = '{TEST_TENANT_ID}' AND deleted_at IS NULL
            """))
            row = result.fetchone()
            return row[0] if row else 0
    except:
        return 0

def get_transactions_from_db(drug_id):
    """从数据库获取库存流水记录"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT transaction_type, quantity, before_quantity, after_quantity, reference_type
                FROM inventory_transactions 
                WHERE drug_id = '{drug_id}' AND tenant_id = '{TEST_TENANT_ID}' AND deleted_at IS NULL
                ORDER BY transaction_date DESC
            """))
            return result.fetchall()
    except:
        return []

def test_purchase_full_flow():
    """测试完整采购流程"""
    print("\n" + "=" * 60)
    print("测试完整采购流程")
    print("=" * 60)
    
    global TEST_PURCHASE_ORDER_ID, TEST_SUPPLIER_ID, TEST_DRUG_ID
    
    # 1. 创建供应商
    print("\n1. 创建供应商...")
    url = f"{BASE_URL}/inventory/suppliers"
    data = {
        "name": "测试供应商",
        "code": f"SUP{uuid4().hex[:8].upper()}",
        "contact_name": "张三",
        "contact_phone": "13800138000",
        "status": "active"
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("code") in [200, 201]:
                TEST_SUPPLIER_ID = result["data"]["id"]
                print(f"✅ 创建供应商成功: {TEST_SUPPLIER_ID}")
            else:
                print(f"❌ 创建供应商失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 创建供应商失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 创建供应商异常: {str(e)}")
        return False
    
    # 2. 获取初始库存
    initial_inventory = get_inventory_from_db(TEST_DRUG_ID)
    print(f"\n2. 初始库存: {initial_inventory}")
    
    # 3. 创建采购单
    print("\n3. 创建采购单...")
    url = f"{BASE_URL}/inventory/purchase-orders"
    purchase_quantity = 20
    purchase_price = 45.0
    data = {
        "supplier_id": TEST_SUPPLIER_ID,
        "order_date": str(date.today()),
        "items": [
            {
                "drug_id": TEST_DRUG_ID,
                "quantity": purchase_quantity,
                "unit_price": purchase_price,
                "batch_no": "BATCH001",
                "expiry_date": "2025-12-31"
            }
        ],
        "remark": "完整采购流程测试"
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("code") in [200, 201]:
                TEST_PURCHASE_ORDER_ID = result["data"]["id"]
                print(f"✅ 创建采购单成功: {TEST_PURCHASE_ORDER_ID}")
            else:
                print(f"❌ 创建采购单失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 创建采购单失败: {response.status_code} - {response.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ 创建采购单异常: {str(e)}")
        return False
    
    # 4. 验证采购单状态（应该是draft）
    print("\n4. 验证采购单状态...")
    url = f"{BASE_URL}/inventory/purchase-orders/{TEST_PURCHASE_ORDER_ID}"
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                order = result["data"]
                if order["status"] == "draft":
                    print(f"✅ 采购单状态正确: draft")
                else:
                    print(f"⚠️  采购单状态: {order['status']}")
            else:
                print(f"⚠️  获取采购单详情失败")
    except Exception as e:
        print(f"⚠️  验证采购单状态异常: {str(e)}")
    
    # 5. 验证库存未变化（审核前）
    inventory_before_approve = get_inventory_from_db(TEST_DRUG_ID)
    print(f"\n5. 审核前库存: {inventory_before_approve}")
    if inventory_before_approve != initial_inventory:
        print(f"❌ 审核前库存不应变化！")
        return False
    else:
        print(f"✅ 审核前库存未变化（正确）")
    
    # 6. 审核采购单
    print("\n6. 审核采购单...")
    url = f"{BASE_URL}/inventory/purchase-orders/{TEST_PURCHASE_ORDER_ID}/approve"
    try:
        response = requests.post(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 审核采购单成功")
            else:
                print(f"❌ 审核采购单失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 审核采购单失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 审核采购单异常: {str(e)}")
        return False
    
    # 7. 验证库存仍未变化（审核后，入库前）
    inventory_after_approve = get_inventory_from_db(TEST_DRUG_ID)
    print(f"\n7. 审核后库存: {inventory_after_approve}")
    if inventory_after_approve != initial_inventory:
        print(f"❌ 审核后库存不应变化！")
        return False
    else:
        print(f"✅ 审核后库存未变化（正确）")
    
    # 8. 入库采购单
    print("\n8. 入库采购单...")
    url = f"{BASE_URL}/inventory/purchase-orders/{TEST_PURCHASE_ORDER_ID}/receive"
    try:
        response = requests.post(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 入库采购单成功")
            else:
                print(f"❌ 入库采购单失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 入库采购单失败: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 入库采购单异常: {str(e)}")
        return False
    
    # 9. 验证库存变化（入库后）
    inventory_after_receive = get_inventory_from_db(TEST_DRUG_ID)
    expected_inventory = initial_inventory + purchase_quantity
    print(f"\n9. 入库后库存: {inventory_after_receive}")
    print(f"   预期库存: {expected_inventory}")
    if inventory_after_receive == expected_inventory:
        print(f"✅ 库存变化正确（+{purchase_quantity}）")
    else:
        print(f"❌ 库存变化不正确！预期: {expected_inventory}, 实际: {inventory_after_receive}")
        return False
    
    # 10. 验证库存流水记录
    print("\n10. 验证库存流水记录...")
    transactions = get_transactions_from_db(TEST_DRUG_ID)
    purchase_transactions = [t for t in transactions if t[4] == "purchase_order"]
    if purchase_transactions:
        latest = purchase_transactions[0]
        print(f"✅ 找到采购入库流水记录:")
        print(f"   类型: {latest[0]}")
        print(f"   数量: +{latest[1]}")
        print(f"   变动前: {latest[2]}")
        print(f"   变动后: {latest[3]}")
        if latest[1] == purchase_quantity and latest[2] == initial_inventory and latest[3] == inventory_after_receive:
            print(f"✅ 流水记录数据正确")
        else:
            print(f"❌ 流水记录数据不正确！")
            return False
    else:
        print(f"❌ 未找到采购入库流水记录！")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 完整采购流程测试通过")
    print("=" * 60)
    return True

def test_check_full_flow():
    """测试完整盘点流程"""
    print("\n" + "=" * 60)
    print("测试完整盘点流程")
    print("=" * 60)
    
    global TEST_CHECK_ID, TEST_DRUG_ID
    
    # 1. 获取当前库存
    current_inventory = get_inventory_from_db(TEST_DRUG_ID)
    print(f"\n1. 当前库存（账面数量）: {current_inventory}")
    
    # 2. 创建盘点单
    print("\n2. 创建盘点单...")
    actual_quantity = current_inventory + 5  # 假设实际数量多5
    difference = actual_quantity - current_inventory
    
    url = f"{BASE_URL}/inventory/checks"
    data = {
        "check_date": str(date.today()),
        "items": [
            {
                "drug_id": TEST_DRUG_ID,
                "actual_quantity": actual_quantity
            }
        ],
        "remark": "完整盘点流程测试"
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("code") in [200, 201]:
                TEST_CHECK_ID = result["data"]["id"]
                print(f"✅ 创建盘点单成功: {TEST_CHECK_ID}")
            else:
                print(f"❌ 创建盘点单失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 创建盘点单失败: {response.status_code} - {response.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ 创建盘点单异常: {str(e)}")
        return False
    
    # 3. 验证盘点单详情
    print("\n3. 验证盘点单详情...")
    url = f"{BASE_URL}/inventory/checks/{TEST_CHECK_ID}"
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                check = result["data"]
                if check["items"]:
                    item = check["items"][0]
                    print(f"   账面数量: {item['book_quantity']}")
                    print(f"   实际数量: {item['actual_quantity']}")
                    print(f"   差异数量: {item['difference']}")
                    if item['book_quantity'] == current_inventory and item['actual_quantity'] == actual_quantity:
                        print(f"✅ 盘点单数据正确")
                    else:
                        print(f"❌ 盘点单数据不正确！")
                        return False
            else:
                print(f"⚠️  获取盘点单详情失败")
    except Exception as e:
        print(f"⚠️  验证盘点单详情异常: {str(e)}")
    
    # 4. 验证库存未变化（完成盘点前）
    inventory_before_complete = get_inventory_from_db(TEST_DRUG_ID)
    print(f"\n4. 完成盘点前库存: {inventory_before_complete}")
    if inventory_before_complete != current_inventory:
        print(f"❌ 完成盘点前库存不应变化！")
        return False
    else:
        print(f"✅ 完成盘点前库存未变化（正确）")
    
    # 5. 完成盘点
    print("\n5. 完成盘点...")
    url = f"{BASE_URL}/inventory/checks/{TEST_CHECK_ID}/complete"
    try:
        response = requests.post(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 完成盘点成功")
            else:
                print(f"❌ 完成盘点失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 完成盘点失败: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 完成盘点异常: {str(e)}")
        return False
    
    # 6. 验证库存变化（完成盘点后）
    inventory_after_complete = get_inventory_from_db(TEST_DRUG_ID)
    expected_inventory = actual_quantity
    print(f"\n6. 完成盘点后库存: {inventory_after_complete}")
    print(f"   预期库存: {expected_inventory}")
    if inventory_after_complete == expected_inventory:
        print(f"✅ 库存变化正确（差异: {difference:+d}）")
    else:
        print(f"❌ 库存变化不正确！预期: {expected_inventory}, 实际: {inventory_after_complete}")
        return False
    
    # 7. 验证库存流水记录
    print("\n7. 验证库存流水记录...")
    transactions = get_transactions_from_db(TEST_DRUG_ID)
    check_transactions = [t for t in transactions if t[4] == "inventory_check"]
    if check_transactions:
        latest = check_transactions[0]
        print(f"✅ 找到盘点流水记录:")
        print(f"   类型: {latest[0]}")
        print(f"   数量: {latest[1]:+d}")
        print(f"   变动前: {latest[2]}")
        print(f"   变动后: {latest[3]}")
        if latest[1] == difference and latest[2] == current_inventory and latest[3] == inventory_after_complete:
            print(f"✅ 流水记录数据正确")
        else:
            print(f"❌ 流水记录数据不正确！")
            return False
    else:
        print(f"❌ 未找到盘点流水记录！")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 完整盘点流程测试通过")
    print("=" * 60)
    return True

def test_data_consistency():
    """测试数据一致性"""
    print("\n" + "=" * 60)
    print("数据一致性测试")
    print("=" * 60)
    
    global TEST_DRUG_ID
    
    # 1. 验证库存流水总和
    print("\n1. 验证库存流水总和...")
    transactions = get_transactions_from_db(TEST_DRUG_ID)
    if transactions:
        total_in = sum(t[1] for t in transactions if t[1] > 0)
        total_out = abs(sum(t[1] for t in transactions if t[1] < 0))
        print(f"   总入库: +{total_in}")
        print(f"   总出库: -{total_out}")
        print(f"   净变化: {total_in - total_out:+d}")
        
        # 验证最后一条流水记录的after_quantity是否等于当前库存
        current_inventory = get_inventory_from_db(TEST_DRUG_ID)
        if transactions:
            last_transaction = transactions[0]
            if last_transaction[3] == current_inventory:
                print(f"✅ 最后一条流水记录的after_quantity等于当前库存")
            else:
                print(f"❌ 最后一条流水记录的after_quantity({last_transaction[3]})不等于当前库存({current_inventory})")
                return False
    else:
        print("⚠️  没有库存流水记录")
    
    # 2. 验证采购单状态流转
    print("\n2. 验证采购单状态流转...")
    if TEST_PURCHASE_ORDER_ID:
        url = f"{BASE_URL}/inventory/purchase-orders/{TEST_PURCHASE_ORDER_ID}"
        try:
            response = requests.get(url, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    order = result["data"]
                    if order["status"] == "received":
                        print(f"✅ 采购单状态正确: received")
                    else:
                        print(f"⚠️  采购单状态: {order['status']}")
                    
                    # 验证已入库数量
                    if order["items"]:
                        item = order["items"][0]
                        if item["received_quantity"] == item["quantity"]:
                            print(f"✅ 已入库数量正确: {item['received_quantity']}/{item['quantity']}")
                        else:
                            print(f"❌ 已入库数量不正确: {item['received_quantity']}/{item['quantity']}")
                            return False
            else:
                print(f"⚠️  无法获取采购单详情")
        except Exception as e:
            print(f"⚠️  验证采购单状态异常: {str(e)}")
    
    # 3. 验证盘点单状态流转
    print("\n3. 验证盘点单状态流转...")
    if TEST_CHECK_ID:
        url = f"{BASE_URL}/inventory/checks/{TEST_CHECK_ID}"
        try:
            response = requests.get(url, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    check = result["data"]
                    if check["status"] == "completed":
                        print(f"✅ 盘点单状态正确: completed")
                    else:
                        print(f"⚠️  盘点单状态: {check['status']}")
                else:
                    print(f"⚠️  无法获取盘点单详情")
        except Exception as e:
            print(f"⚠️  验证盘点单状态异常: {str(e)}")
    
    # 4. 验证库存流水记录的连续性
    print("\n4. 验证库存流水记录的连续性...")
    transactions = get_transactions_from_db(TEST_DRUG_ID)
    if len(transactions) >= 2:
        # 按时间顺序验证（从旧到新）
        sorted_transactions = sorted(transactions, key=lambda x: x[2] if x[2] else 0)
        for i in range(len(sorted_transactions) - 1):
            current = sorted_transactions[i]
            next_t = sorted_transactions[i + 1]
            if current[3] == next_t[2]:  # 当前交易的after_quantity应该等于下一个交易的before_quantity
                print(f"✅ 流水记录{i+1}和{i+2}连续")
            else:
                print(f"❌ 流水记录{i+1}和{i+2}不连续！")
                print(f"   记录{i+1} after_quantity: {current[3]}")
                print(f"   记录{i+2} before_quantity: {next_t[2]}")
                return False
        print(f"✅ 所有流水记录连续")
    else:
        print("⚠️  流水记录不足，无法验证连续性")
    
    print("\n" + "=" * 60)
    print("✅ 数据一致性测试通过")
    print("=" * 60)
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("进销存模块完整测试（采购流程 + 盘点流程 + 数据一致性）")
    print("=" * 60)
    
    # 登录
    if not login():
        print("\n❌ 登录失败，无法继续测试")
        print("\n提示：")
        print("1. 请确保后端服务已启动: cd backend && uvicorn app.main:app --reload")
        print("2. 测试脚本会自动创建测试数据（租户、用户、药品）")
        return
    
    # 测试结果
    results = []
    
    # 测试完整采购流程
    results.append(("完整采购流程", test_purchase_full_flow()))
    
    # 测试完整盘点流程
    results.append(("完整盘点流程", test_check_full_flow()))
    
    # 测试数据一致性
    results.append(("数据一致性", test_data_consistency()))
    
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
    if passed + failed > 0:
        print(f"通过率: {passed / (passed + failed) * 100:.1f}%")
    
    print("\n" + "=" * 60)
    if passed == passed + failed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
    print("=" * 60)

if __name__ == "__main__":
    main()


"""
API测试脚本
用于测试新创建的中医、日志、账单明细等API接口
"""
import requests
import json
from typing import Optional

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用的认证Token（需要先登录获取）
AUTH_TOKEN: Optional[str] = None
TENANT_ID: Optional[str] = None


def login(username: str, password: str, tenant_code: str) -> bool:
    """
    登录获取Token
    
    Args:
        username: 用户名
        password: 密码
        tenant_code: 租户代码
    
    Returns:
        bool: 是否登录成功
    """
    global AUTH_TOKEN, TENANT_ID
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password,
        "tenant_code": tenant_code
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                AUTH_TOKEN = result["data"]["access_token"]
                TENANT_ID = result["data"].get("tenant_id")
                print(f"✅ 登录成功，Token: {AUTH_TOKEN[:20]}...")
                return True
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False


def get_headers() -> dict:
    """获取请求头"""
    headers = {"Content-Type": "application/json"}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    if TENANT_ID:
        headers["X-Tenant-Id"] = TENANT_ID
    return headers


def test_create_diagnosis(medical_record_id: str):
    """测试创建诊断"""
    url = f"{BASE_URL}/tcm/diagnoses"
    data = {
        "medical_record_id": medical_record_id,
        "icd_code": "A00.0",
        "diagnosis_name": "感冒",
        "diagnosis_type": "primary",
        "description": "上呼吸道感染"
    }
    
    response = requests.post(url, json=data, headers=get_headers())
    print(f"\n测试创建诊断:")
    print(f"  请求: POST {url}")
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code in [200, 201]


def test_get_diagnoses(medical_record_id: str):
    """测试获取诊断列表"""
    url = f"{BASE_URL}/tcm/diagnoses/medical-record/{medical_record_id}"
    
    response = requests.get(url, headers=get_headers())
    print(f"\n测试获取诊断列表:")
    print(f"  请求: GET {url}")
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_create_tcm_diagnosis(medical_record_id: str):
    """测试创建中医诊断"""
    url = f"{BASE_URL}/tcm/tcm-diagnosis"
    data = {
        "medical_record_id": medical_record_id,
        "syndrome_type": "风寒感冒",
        "pathogenesis": "外感风寒，肺卫失宣",
        "disease_name": "感冒",
        "constitution_type": "平和质",
        "tongue_state": "舌淡红，苔薄白",
        "pulse_state": "脉浮紧",
        "tcm_diagnosis": "风寒感冒",
        "treatment_principle": "辛温解表",
        "treatment_method": "疏风散寒"
    }
    
    response = requests.post(url, json=data, headers=get_headers())
    print(f"\n测试创建中医诊断:")
    print(f"  请求: POST {url}")
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code in [200, 201]


def test_get_operation_logs():
    """测试获取操作日志列表"""
    url = f"{BASE_URL}/logs/operation-logs"
    params = {
        "skip": 0,
        "limit": 10
    }
    
    response = requests.get(url, params=params, headers=get_headers())
    print(f"\n测试获取操作日志列表:")
    print(f"  请求: GET {url}")
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_get_bill_items(bill_id: str):
    """测试获取账单明细列表"""
    url = f"{BASE_URL}/payments/bills/{bill_id}/items"
    
    response = requests.get(url, headers=get_headers())
    print(f"\n测试获取账单明细列表:")
    print(f"  请求: GET {url}")
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def main():
    """主测试函数"""
    print("=" * 60)
    print("API测试脚本")
    print("=" * 60)
    
    # 登录（需要替换为实际的用户名、密码和租户代码）
    print("\n1. 登录测试")
    if not login("admin", "password", "default"):
        print("❌ 登录失败，无法继续测试")
        return
    
    # 测试操作日志API（不需要额外数据）
    print("\n2. 测试操作日志API")
    test_get_operation_logs()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n注意：")
    print("1. 需要先启动后端服务：cd backend && uvicorn app.main:app --reload")
    print("2. 需要替换测试脚本中的用户名、密码和租户代码")
    print("3. 需要准备测试数据（如medical_record_id、bill_id等）")


if __name__ == "__main__":
    main()


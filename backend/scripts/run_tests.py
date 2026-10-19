#!/usr/bin/env python3
"""
测试执行脚本
"""
import sys
import subprocess
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

def run_command(cmd, description):
    """执行命令"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    
    if result.returncode != 0:
        print(f"\n❌ {description} 失败")
        return False
    else:
        print(f"\n✅ {description} 成功")
        return True

def main():
    """主函数"""
    print("="*60)
    print("开始执行测试")
    print("="*60)
    
    # 1. 单元测试
    print("\n1. 执行单元测试...")
    unit_test_success = run_command(
        "pytest tests/unit -v --cov=app --cov-report=html --cov-report=term",
        "单元测试"
    )
    
    # 2. 集成测试
    print("\n2. 执行集成测试...")
    integration_test_success = run_command(
        "pytest tests/integration -v",
        "集成测试"
    )
    
    # 3. API测试
    print("\n3. 执行API测试...")
    api_test_success = run_command(
        "pytest tests/api -v",
        "API测试"
    )
    
    # 总结
    print("\n" + "="*60)
    print("测试执行总结")
    print("="*60)
    print(f"单元测试: {'✅ 通过' if unit_test_success else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_test_success else '❌ 失败'}")
    print(f"API测试: {'✅ 通过' if api_test_success else '❌ 失败'}")
    
    if unit_test_success and integration_test_success and api_test_success:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())


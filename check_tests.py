#!/usr/bin/env python3
"""
测试代码检查脚本
检查测试文件的基本结构和导入问题
"""
import os
import sys
import ast
import importlib.util

def check_file_syntax(filepath):
    """检查文件语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)

def check_imports(filepath):
    """检查导入语句"""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module
                if module and module.startswith('app.'):
                    # 检查是否是有效的导入路径
                    pass
    except Exception as e:
        issues.append(f"导入检查错误: {e}")
    
    return issues

def check_test_structure(filepath):
    """检查测试结构"""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有测试类
        if 'class Test' not in content and 'def test_' not in content:
            issues.append("未找到测试类或测试函数")
        
        # 检查是否有await在非async函数中（简单检查）
        if 'async def' not in content and 'await' in content:
            issues.append("可能存在await在非async函数中的问题")
            
    except Exception as e:
        issues.append(f"结构检查错误: {e}")
    
    return issues

def main():
    """主函数"""
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if not os.path.exists(test_dir):
        print(f"错误: 测试目录不存在: {test_dir}")
        return 1
    
    print("=" * 60)
    print("测试代码检查")
    print("=" * 60)
    
    all_ok = True
    checked_files = 0
    
    # 检查单元测试
    unit_dir = os.path.join(test_dir, 'unit')
    if os.path.exists(unit_dir):
        print(f"\n检查单元测试目录: {unit_dir}")
        for filename in os.listdir(unit_dir):
            if filename.endswith('.py') and filename.startswith('test_'):
                filepath = os.path.join(unit_dir, filename)
                checked_files += 1
                print(f"\n检查: {filename}")
                
                # 语法检查
                ok, error = check_file_syntax(filepath)
                if not ok:
                    print(f"  ❌ 语法错误: {error}")
                    all_ok = False
                else:
                    print(f"  ✅ 语法正确")
                
                # 结构检查
                issues = check_test_structure(filepath)
                if issues:
                    for issue in issues:
                        print(f"  ⚠️  {issue}")
                        all_ok = False
                else:
                    print(f"  ✅ 结构正确")
    
    # 检查集成测试
    integration_dir = os.path.join(test_dir, 'integration')
    if os.path.exists(integration_dir):
        print(f"\n检查集成测试目录: {integration_dir}")
        for filename in os.listdir(integration_dir):
            if filename.endswith('.py') and filename.startswith('test_'):
                filepath = os.path.join(integration_dir, filename)
                checked_files += 1
                print(f"\n检查: {filename}")
                
                # 语法检查
                ok, error = check_file_syntax(filepath)
                if not ok:
                    print(f"  ❌ 语法错误: {error}")
                    all_ok = False
                else:
                    print(f"  ✅ 语法正确")
                
                # 结构检查
                issues = check_test_structure(filepath)
                if issues:
                    for issue in issues:
                        print(f"  ⚠️  {issue}")
                        all_ok = False
                else:
                    print(f"  ✅ 结构正确")
    
    # 检查conftest.py
    conftest_path = os.path.join(test_dir, 'conftest.py')
    if os.path.exists(conftest_path):
        print(f"\n检查: conftest.py")
        checked_files += 1
        ok, error = check_file_syntax(conftest_path)
        if not ok:
            print(f"  ❌ 语法错误: {error}")
            all_ok = False
        else:
            print(f"  ✅ 语法正确")
    
    print("\n" + "=" * 60)
    print(f"检查完成: 共检查 {checked_files} 个文件")
    if all_ok:
        print("✅ 所有检查通过！")
        return 0
    else:
        print("❌ 发现一些问题，请检查上述输出")
        return 1

if __name__ == '__main__':
    sys.exit(main())


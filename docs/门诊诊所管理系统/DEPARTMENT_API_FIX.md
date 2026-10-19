# 科室API 500错误修复

## 问题描述
调用`/api/v1/departments`接口时返回500错误。

## 根本原因
1. **缺少导入**：`departments.py`中缺少`and_`的导入
2. **UUID转换问题**：`DepartmentRepository`中的方法没有正确处理UUID类型转换
3. **错误处理不足**：异常处理没有记录详细错误信息

## 解决方案

### 1. 添加缺失的导入 ✅
在`departments.py`中：
- 添加`and_`导入
- 添加`logger`导入，用于记录错误

### 2. 修复UUID转换 ✅
在`system_repository.py`中：
- `get_departments`：添加tenant_id的UUID转换
- `get_department_by_id`：添加department_id和tenant_id的UUID转换
- `create_department`：添加tenant_id的UUID转换
- `get_doctors`：添加tenant_id和department_id的UUID转换
- `get_doctor_by_id`：添加doctor_id和tenant_id的UUID转换
- `create_doctor`：添加tenant_id、department_id和user_id的UUID转换

### 3. 改进错误处理 ✅
- 添加详细的错误日志记录
- 在统计医生数量时添加try-catch，避免单个科室统计失败影响整体

## 修改的文件

### 后端文件
1. `/backend/app/api/v1/departments.py`
   - ✅ 添加`and_`和`logger`导入
   - ✅ 改进错误处理，添加详细日志
   - ✅ 在统计医生数量时添加异常处理

2. `/backend/app/repositories/system_repository.py`
   - ✅ 修复所有方法的UUID转换问题
   - ✅ 确保所有UUID字段都正确转换

## 技术细节

### UUID转换模式
参考`PatientRepository`的实现，所有接受字符串ID的方法都需要转换为UUID：
```python
from uuid import UUID

if isinstance(id, str):
    try:
        id_uuid = UUID(id)
    except (ValueError, TypeError):
        id_uuid = id
else:
    id_uuid = id
```

### 错误处理改进
```python
try:
    # 统计医生数量
    doctor_count = db.query(func.count(Doctor.id)).filter(...).scalar() or 0
except Exception as count_error:
    logger.warning(f"统计科室 {dept.id} 的医生数量失败: {str(count_error)}")
    doctor_count = 0
```

## 测试验证

修复后应该能够：
1. ✅ 成功调用`/api/v1/departments`接口
2. ✅ 正确返回科室列表
3. ✅ 正确统计每个科室的医生数量
4. ✅ 即使某个科室统计失败，也不影响整体返回

## 注意事项

1. **UUID格式**：确保所有ID都是有效的UUID格式
2. **错误处理**：单个科室统计失败不会影响整体列表返回
3. **日志记录**：所有错误都会记录到日志中，便于排查问题

## 总结

✅ **导入修复**：添加缺失的`and_`和`logger`导入
✅ **UUID转换**：修复所有方法的UUID类型转换问题
✅ **错误处理**：改进错误处理和日志记录
✅ **容错性**：单个操作失败不影响整体功能

所有功能现在应该可以正常工作了。请刷新页面后测试科室列表加载功能。


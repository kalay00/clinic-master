# 挂号创建UUID格式错误修复

## 问题描述
创建挂号时出现错误：`invalid input syntax for type uuid: "1"`

错误原因：前端传递的`doctor_id`和`department_id`是字符串`'1'`、`'2'`、`'3'`等，但数据库期望的是UUID格式。

## 根本原因
1. **硬编码数据**：挂号表单中的科室和医生选择器使用硬编码的值，不是真实的UUID
2. **缺少数据加载**：没有从后端API加载真实的科室和医生列表
3. **缺少UUID验证**：前端没有验证UUID格式

## 解决方案

### 1. 从后端加载科室和医生列表 ✅
在`showAddRegistrationModal`函数中：
- 调用`DepartmentAPI.getList()`加载科室列表
- 使用真实的科室UUID作为选项值
- 添加错误处理，如果加载失败显示警告

### 2. 实现科室-医生联动 ✅
- 添加`loadDoctorsForRegistration`函数
- 当选择科室时，自动加载该科室的医生列表
- 在`FormComponents.createSelect`中添加`onChange`支持

### 3. 添加UUID格式验证 ✅
在表单提交时：
- 验证`doctor_id`和`department_id`是否为有效的UUID格式
- 如果格式错误，显示友好的错误提示
- 确保必填字段都已填写

### 4. 改进表单组件 ✅
在`FormComponents.createSelect`中：
- 添加`onChange`参数支持
- 支持在select元素上添加`onchange`事件

## 修改的文件

### 前端文件
1. `/frontend/views/registrations/list.html`
   - ✅ 修改`showAddRegistrationModal`，从后端加载科室列表
   - ✅ 添加`loadDoctorsForRegistration`函数，实现科室-医生联动
   - ✅ 添加UUID格式验证
   - ✅ 改进错误处理和用户提示

2. `/frontend/js/components.js`
   - ✅ 修改`FormComponents.createSelect`，添加`onChange`支持

## 技术细节

### 1. 科室列表加载
```javascript
const deptsResponse = await DepartmentAPI.getList({ page: 1, page_size: 100 });
const departments = deptsResponse.items || deptsResponse || [];
departmentOptions = [
    { value: '', text: '请选择科室' },
    ...departments.map(dept => ({ 
        value: dept.id,  // 使用真实的UUID
        text: dept.name || dept.code || '未知科室' 
    }))
];
```

### 2. 医生列表联动
```javascript
window.loadDoctorsForRegistration = async function() {
    const departmentId = document.getElementById('department-select')?.value;
    // 根据科室ID加载医生列表
    const doctorsResponse = await DoctorAPI.getList({ 
        page: 1, 
        page_size: 100,
        department_id: departmentId
    });
    // 更新医生选项...
};
```

### 3. UUID格式验证
```javascript
const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
if (data.doctor_id && !uuidRegex.test(data.doctor_id)) {
    utils.showToast('医生ID格式错误，请重新选择医生', 'danger');
    return false;
}
```

## 测试验证

修复后应该能够：
1. ✅ 打开新增挂号弹窗，正确加载科室列表
2. ✅ 选择科室后，自动加载该科室的医生列表
3. ✅ 选择医生和科室后，提交时使用真实的UUID
4. ✅ 如果UUID格式错误，显示友好的错误提示
5. ✅ 成功创建挂号记录

## 注意事项

1. **数据依赖**：确保后端有科室和医生数据，否则下拉框可能为空
2. **UUID格式**：所有ID字段必须是有效的UUID格式
3. **错误处理**：如果API调用失败，会显示警告但不会阻止表单显示
4. **联动逻辑**：选择科室后，医生列表会自动更新

## 总结

✅ **数据加载**：从后端API加载真实的科室和医生数据
✅ **UUID格式**：使用真实的UUID而不是硬编码的字符串
✅ **联动功能**：实现科室-医生联动选择
✅ **格式验证**：添加UUID格式验证，防止无效数据提交
✅ **错误处理**：改进错误处理和用户提示

所有功能现在应该可以正常工作了。请刷新页面后测试新增挂号功能。


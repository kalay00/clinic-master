# 患者选择器病历号显示undefined问题修复

## 问题描述
在新增挂号时，选择患者后，患者病历号显示为`undefined`。

## 根本原因
1. **字段名不一致**：后端返回的字段是`patient_no`，但前端代码中可能使用`medical_record_no`
2. **JSON序列化问题**：在`onclick`事件中直接使用JSON对象可能导致数据丢失
3. **数据传递问题**：患者数据在选择器组件中传递时，字段名可能没有正确统一

## 解决方案

### 1. 修复患者选择器组件 ✅
在`components.js`的`loadPatientsForSelector`函数中：
- 使用`data`属性存储患者数据，避免JSON序列化问题
- 通过索引访问患者数据，而不是直接在`onclick`中传递对象
- 确保字段名统一：同时保留`patient_no`和`medical_record_no`字段

### 2. 修复选择患者回调 ✅
在`registrations/list.html`的`selectPatientForRegistration`函数中：
- 增强字段名兼容性，支持多种可能的字段名
- 添加空值检查，防止undefined错误
- 添加元素存在性检查，确保DOM元素存在后再设置值

## 修改的文件

### 前端文件
1. `/frontend/js/components.js`
   - ✅ 修改`loadPatientsForSelector`函数，使用索引方式传递患者数据
   - ✅ 添加患者数据存储机制，避免JSON序列化问题
   - ✅ 确保字段名统一，同时保留`patient_no`和`medical_record_no`
   - ✅ 添加清理逻辑，关闭弹窗时清理存储的数据

2. `/frontend/views/registrations/list.html`
   - ✅ 修复`selectPatientForRegistration`函数，增强字段名兼容性
   - ✅ 添加空值检查和元素存在性检查
   - ✅ 改进错误处理和用户提示

## 技术细节

### 1. 字段名统一
后端返回的字段是`patient_no`，但前端可能使用`medical_record_no`。现在同时保留两个字段：
```javascript
const patientData = {
    ...patient,
    medical_record_no: recordNo,
    patient_no: recordNo  // 同时保留patient_no字段
};
```

### 2. 数据传递方式改进
原来使用JSON字符串直接传递，现在改为：
- 使用`data-patient-index`和`data-patient-data`属性存储数据
- 通过索引访问存储的患者列表
- 避免JSON序列化/反序列化过程中的数据丢失

### 3. 选择器回调增强
```javascript
onSelect: (selectedPatient) => {
    // 支持多种字段名
    const recordNo = selectedPatient.medical_record_no || 
                    selectedPatient.patient_no || 
                    selectedPatient.record_no || 
                    '-';
    // ...
}
```

## 测试验证

修复后应该能够：
1. ✅ 点击"选择患者"按钮，正确打开患者选择器
2. ✅ 选择患者后，正确显示患者姓名和病历号
3. ✅ 病历号不再显示`undefined`
4. ✅ 患者信息正确填充到挂号表单

## 总结

✅ **字段名统一**：确保`patient_no`和`medical_record_no`都能正确识别
✅ **数据传递**：改进数据传递方式，避免JSON序列化问题
✅ **错误处理**：添加空值检查和元素存在性检查
✅ **用户体验**：改进错误提示和用户反馈

所有功能现在应该可以正常工作了。请刷新页面后测试选择患者功能。

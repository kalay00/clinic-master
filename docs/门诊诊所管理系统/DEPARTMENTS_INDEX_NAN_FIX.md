# 科室管理序号显示NaN问题修复

## 问题描述

科室管理页面中，科室列表的序号列显示为 `NaN`，而不是正确的序号（1, 2, 3...）。

## 问题原因

在 `TableComponents.renderTable` 方法中，`render` 函数只接收 `row` 参数，没有传递 `index` 参数。

### 问题代码

```javascript
// components.js 第276行
const value = col.render ? col.render(row) : (row[col.key] || '');
```

但是在科室管理页面中，序号列的 `render` 函数期望接收两个参数：

```javascript
// departments.html 第144行
render: (row, index) => index + 1
```

当 `render` 函数被调用时，`index` 参数是 `undefined`，所以 `undefined + 1` 的结果是 `NaN`。

## 修复方案

修改 `TableComponents.renderTable` 方法，在调用 `render` 函数时传递 `index` 参数：

### 修复前

```javascript
data.forEach(row => {
    html += '<tr>';
    columns.forEach(col => {
        const align = col.align || 'left';
        const value = col.render ? col.render(row) : (row[col.key] || '');  // ❌ 只传递row
        html += `<td style="text-align: ${align}">${value}</td>`;
    });
    html += '</tr>';
});
```

### 修复后

```javascript
data.forEach((row, index) => {  // ✅ 获取index
    html += '<tr>';
    columns.forEach(col => {
        const align = col.align || 'left';
        const value = col.render ? col.render(row, index) : (row[col.key] || '');  // ✅ 传递row和index
        html += `<td style="text-align: ${align}">${value}</td>`;
    });
    html += '</tr>';
});
```

## 修复内容

1. **修改 `data.forEach` 回调函数**
   - 从 `data.forEach(row => {` 改为 `data.forEach((row, index) => {`
   - 获取数组索引 `index`

2. **修改 `render` 函数调用**
   - 从 `col.render(row)` 改为 `col.render(row, index)`
   - 传递 `index` 参数给 `render` 函数

## 修复效果

### 修复前
- ❌ 序号列显示 `NaN`
- ❌ `render` 函数无法获取索引

### 修复后
- ✅ 序号列正确显示 1, 2, 3...
- ✅ `render` 函数可以接收 `row` 和 `index` 两个参数
- ✅ 兼容只使用 `row` 参数的 `render` 函数

## 兼容性说明

修复后的代码向后兼容：
- 如果 `render` 函数只使用 `row` 参数，仍然可以正常工作
- 如果 `render` 函数需要使用 `index` 参数，现在可以正常获取

## 验证步骤

1. **访问科室管理页面**
   ```
   http://localhost:8000/index.html
   ```
   登录后，导航到"系统管理" > "科室管理"

2. **检查序号列**
   - 序号列应该显示 1, 2, 3...
   - 不应该显示 `NaN`

3. **测试其他使用序号列的页面**
   - 确认其他页面的序号列也正常工作

## 相关文件

- 修复文件: `/frontend/js/components.js` (renderTable方法)
- 使用页面: `/frontend/views/system/departments.html` (序号列定义)

## 总结

**问题**：序号列显示 `NaN`

**原因**：`render` 函数调用时没有传递 `index` 参数

**解决方案**：在 `forEach` 中获取 `index`，并在调用 `render` 时传递

**修复状态**：✅ 已修复

修复时间: 2025-11-07 07:40


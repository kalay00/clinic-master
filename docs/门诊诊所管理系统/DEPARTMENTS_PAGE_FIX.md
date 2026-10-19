# 科室管理页面修复记录

## 问题描述
科室管理页面异常，函数未定义错误。

## 原因分析
在动态加载的HTML页面中，JavaScript函数需要显式挂载到`window`对象上，才能在`onclick`属性中正确调用。科室管理页面的函数没有挂载到全局作用域。

## 解决方案

### 1. 将所有函数挂载到window对象
- `loadDepartments` → `window.loadDepartments`
- `searchDepartments` → `window.searchDepartments`
- `resetSearch` → `window.resetSearch`
- `showAddDepartmentModal` → `window.showAddDepartmentModal`
- `editDepartment` → `window.editDepartment`
- `deleteDepartment` → `window.deleteDepartment`

### 2. 更新所有onclick调用
- HTML中的`onclick`属性都使用`window.`前缀
- 函数内部调用也使用`window.`前缀

## 修复内容

### 修改的文件
- `/home/laknl/his/frontend/views/system/departments.html`

### 具体修改
1. **pageInit函数**：调用`window.loadDepartments()`和`window.searchDepartments()`
2. **loadDepartments函数**：挂载为`window.loadDepartments`
3. **searchDepartments函数**：挂载为`window.searchDepartments`
4. **resetSearch函数**：挂载为`window.resetSearch`
5. **showAddDepartmentModal函数**：挂载为`window.showAddDepartmentModal`
6. **editDepartment函数**：挂载为`window.editDepartment`
7. **deleteDepartment函数**：挂载为`window.deleteDepartment`
8. **HTML中的onclick属性**：全部添加`window.`前缀

## 修复结果
- ✅ 所有函数已挂载到全局作用域
- ✅ HTML中的onclick调用已更新
- ✅ 函数内部调用已更新
- ✅ 页面应该可以正常加载和操作

## 注意事项
1. 在SPA应用中，动态加载的HTML页面中的函数必须挂载到`window`对象
2. 所有`onclick`属性中的函数调用都应该使用`window.`前缀
3. 函数内部调用其他函数时也应该使用`window.`前缀，确保一致性

修复完成时间: 2025-11-06 23:35


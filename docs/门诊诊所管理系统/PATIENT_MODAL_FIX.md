# 患者管理新增患者弹窗修复

## 问题描述

在患者管理页面点击"新增患者"按钮时，提示错误：`showAddPatientModal is not defined`

## 根本原因

当通过 `innerHTML` 动态插入 HTML 内容时，其中的 `<script>` 标签不会被执行。这是因为浏览器出于安全考虑，不会执行通过 `innerHTML` 插入的脚本。

## 解决方案

### 1. 修改页面加载逻辑 (`app.js`)

修改 `loadPage()` 方法，提取并执行页面中的 `<script>` 标签：

```javascript
async loadPage() {
    // ... 获取HTML内容
    
    // 解析HTML，分离内容和脚本
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const scripts = doc.querySelectorAll('script');
    
    // 先插入HTML内容（不包含script标签）
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    const scriptsElements = tempDiv.querySelectorAll('script');
    scriptsElements.forEach(script => script.remove());
    contentArea.innerHTML = tempDiv.innerHTML;
    
    // 执行脚本
    scripts.forEach(script => {
        const newScript = document.createElement('script');
        if (script.src) {
            newScript.src = script.src;
        } else {
            newScript.textContent = script.textContent;
        }
        document.body.appendChild(newScript);
        // 如果是内联脚本，执行后移除
        if (!script.src) {
            document.body.removeChild(newScript);
        }
    });
}
```

### 2. 将函数挂载到全局作用域 (`list.html`)

将所有需要在 `onclick` 中调用的函数显式挂载到 `window` 对象：

```javascript
// 修改前
async function showAddPatientModal() { ... }

// 修改后
window.showAddPatientModal = async function() { ... }
```

修改的函数包括：
- `showAddPatientModal` - 显示新增患者弹窗
- `viewPatient` - 查看患者详情
- `editPatient` - 编辑患者
- `deletePatient` - 删除患者
- `exportPatients` - 导出患者
- `initSearchBar` - 初始化搜索栏
- `loadPatients` - 加载患者列表

### 3. 更新函数调用

更新 `pageInit` 和其他函数中的调用，使用 `window.` 前缀：

```javascript
window.pageInit = function() {
    window.initSearchBar();
    window.loadPatients();
};
```

## 修复的文件

1. `/home/laknl/his/frontend/js/app.js` - 修改页面加载逻辑，支持执行动态加载的脚本
2. `/home/laknl/his/frontend/views/patients/list.html` - 将所有函数挂载到全局作用域

## 测试验证

修复后，点击"新增患者"按钮应该能够：
1. 正常显示新增患者弹窗
2. 表单字段正确显示
3. 可以正常提交数据

## 注意事项

1. 所有通过 `onclick` 属性调用的函数都需要挂载到 `window` 对象
2. 如果页面中有其他类似的动态加载页面，也需要应用相同的修复
3. 建议统一使用 `window.` 前缀，确保函数在全局作用域中可用


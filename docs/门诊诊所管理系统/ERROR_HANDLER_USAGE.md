# 错误提示组件使用文档

## 一、概述

统一错误处理组件（`ErrorHandler`）提供了统一的错误提示和错误处理机制，支持多种类型的提示（成功、错误、警告、信息）。

## 二、引入组件

在HTML页面中引入错误处理组件：

```html
<script src="/js/error-handler.js"></script>
```

**注意**: 错误处理组件应该在Bootstrap JS之后、API客户端之前引入。

## 三、基本使用

### 1. 显示错误提示

```javascript
// 显示错误提示
ErrorHandler.showError('操作失败，请稍后重试');

// 带标题的错误提示
ErrorHandler.showError('用户名或密码错误', {
    title: '登录失败',
    duration: 5000
});
```

### 2. 显示成功提示

```javascript
ErrorHandler.showSuccess('操作成功');
```

### 3. 显示警告提示

```javascript
ErrorHandler.showWarning('请确认操作');
```

### 4. 显示信息提示

```javascript
ErrorHandler.showInfo('提示信息');
```

## 四、API错误处理

### 自动错误处理

API客户端已经集成了错误处理，当API请求失败时会自动显示错误提示：

```javascript
// API客户端会自动处理错误
try {
    const result = await PatientAPI.getList();
} catch (error) {
    // 错误已经自动显示，这里可以做额外处理
    console.error('获取患者列表失败:', error);
}
```

### 手动处理API错误

```javascript
try {
    const result = await api.post('/patients', data);
} catch (error) {
    // 手动处理错误
    ErrorHandler.handleApiError(error, {
        showToast: true,
        defaultMessage: '创建患者失败'
    });
}
```

## 五、配置选项

### Toast配置

```javascript
ErrorHandler.showError('错误信息', {
    title: '错误',           // 标题（可选）
    duration: 5000,          // 显示时长（毫秒），0表示不自动关闭
    position: 'top-end',     // 位置（top-start, top-center, top-end等）
    showCloseButton: true,   // 是否显示关闭按钮
    type: 'error'            // 类型（success, error, warning, info）
});
```

### 位置选项

- `top-start`: 顶部左侧
- `top-center`: 顶部居中
- `top-end`: 顶部右侧（默认）
- `middle-start`: 中间左侧
- `middle-center`: 中间居中
- `middle-end`: 中间右侧
- `bottom-start`: 底部左侧
- `bottom-center`: 底部居中
- `bottom-end`: 底部右侧

## 六、错误类型

### 1. 网络错误

```javascript
try {
    const result = await api.get('/patients');
} catch (error) {
    if (error.message.includes('network') || error.message.includes('fetch')) {
        ErrorHandler.showError('网络连接失败，请检查网络设置', {
            title: '网络错误'
        });
    }
}
```

### 2. 认证错误（401）

API客户端会自动处理401错误，显示"登录已过期，请重新登录"并跳转到登录页。

### 3. 权限错误（403）

```javascript
// 错误处理器会自动识别403错误并显示相应提示
ErrorHandler.handleApiError(error);
// 显示: "没有权限执行此操作"
```

### 4. 业务错误

```javascript
try {
    const result = await api.post('/patients', data);
} catch (error) {
    // 显示后端返回的错误信息
    ErrorHandler.handleApiError(error);
}
```

## 七、全局错误处理

错误处理组件会自动捕获全局错误：

```javascript
// 全局错误会自动显示
window.addEventListener('error', (event) => {
    // ErrorHandler已自动处理
});

// Promise错误会自动显示
window.addEventListener('unhandledrejection', (event) => {
    // ErrorHandler已自动处理
});
```

## 八、确认对话框

### 带错误提示的确认对话框

```javascript
const confirmed = await ErrorHandler.confirmWithError(
    '确定要删除此患者吗？此操作不可恢复！',
    {
        title: '确认删除',
        type: 'danger'
    }
);

if (confirmed) {
    // 执行删除操作
    await PatientAPI.delete(patientId);
    ErrorHandler.showSuccess('删除成功');
}
```

## 九、最佳实践

### 1. 在API调用中使用

```javascript
async function createPatient(data) {
    try {
        const result = await PatientAPI.create(data);
        ErrorHandler.showSuccess('创建患者成功');
        return result;
    } catch (error) {
        ErrorHandler.handleApiError(error);
        throw error; // 重新抛出以便上层处理
    }
}
```

### 2. 在表单提交中使用

```javascript
document.getElementById('patientForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 提交中...';
    
    try {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        await PatientAPI.create(data);
        ErrorHandler.showSuccess('创建患者成功');
        // 重置表单或跳转
    } catch (error) {
        ErrorHandler.handleApiError(error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
});
```

### 3. 批量操作

```javascript
async function batchDelete(ids) {
    const confirmed = await ErrorHandler.confirmWithError(
        `确定要删除选中的 ${ids.length} 条记录吗？`,
        { type: 'danger' }
    );
    
    if (!confirmed) return;
    
    let successCount = 0;
    let failCount = 0;
    
    for (const id of ids) {
        try {
            await PatientAPI.delete(id);
            successCount++;
        } catch (error) {
            failCount++;
            console.error(`删除 ${id} 失败:`, error);
        }
    }
    
    if (successCount > 0) {
        ErrorHandler.showSuccess(`成功删除 ${successCount} 条记录`);
    }
    if (failCount > 0) {
        ErrorHandler.showError(`删除失败 ${failCount} 条记录`);
    }
}
```

## 十、自定义样式

可以通过CSS自定义Toast样式：

```css
.toast-container {
    z-index: 9999;
}

.toast {
    min-width: 300px;
    max-width: 500px;
}

.toast-body {
    font-size: 14px;
}
```

## 十一、API参考

### ErrorHandler.showError(error, options)
显示错误提示

### ErrorHandler.showSuccess(message, options)
显示成功提示

### ErrorHandler.showWarning(message, options)
显示警告提示

### ErrorHandler.showInfo(message, options)
显示信息提示

### ErrorHandler.showToast(message, type, options)
显示Toast通知（通用方法）

### ErrorHandler.handleApiError(error, options)
处理API错误

### ErrorHandler.confirmWithError(message, options)
显示确认对话框（带错误提示）

## 十二、注意事项

1. **组件加载顺序**: 错误处理组件应该在Bootstrap JS之后加载
2. **自动处理**: API客户端已集成错误处理，大部分情况下无需手动调用
3. **错误信息**: 尽量使用后端返回的错误信息，提供更准确的提示
4. **用户体验**: 错误提示应该有明确的关闭按钮，避免遮挡重要内容
5. **性能考虑**: 避免频繁显示Toast，可以考虑合并多个错误提示


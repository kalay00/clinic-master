# 错误提示组件（增强版）使用文档

## 一、概述

增强版错误处理组件（`ErrorHandlerEnhanced`）在基础版的基础上，提供了更多功能和更好的用户体验。

## 二、新增功能

### 1. Toast队列管理 ✅

自动管理多个Toast，避免同时显示太多Toast影响用户体验。

```javascript
// 最多同时显示5个Toast，超出部分会排队等待
ErrorHandlerEnhanced.showError('错误1');
ErrorHandlerEnhanced.showError('错误2');
ErrorHandlerEnhanced.showError('错误3');
// ... 超出部分会自动排队
```

### 2. 消息合并 ✅

相同组的错误消息可以合并显示，显示错误次数。

```javascript
// 相同组的错误会合并显示
ErrorHandlerEnhanced.handleApiError(error1, {
    group: 'api-errors',
    merge: true
});
ErrorHandlerEnhanced.handleApiError(error2, {
    group: 'api-errors',
    merge: true
});
// 只显示一个Toast，显示"错误 (2)"
```

### 3. 进度条 ✅

显示Toast自动关闭的进度条。

```javascript
ErrorHandlerEnhanced.showError('错误信息', {
    showProgress: true,  // 显示进度条
    duration: 5000       // 5秒后自动关闭
});
```

### 4. 自定义操作按钮 ✅

在Toast中添加操作按钮（如重试）。

```javascript
ErrorHandlerEnhanced.handleApiError(error, {
    action: async () => {
        // 重试操作
        await PatientAPI.create(data);
    },
    actionText: '重试',
    persistent: true  // 有操作按钮时，Toast不自动关闭
});
```

### 5. 持久化Toast ✅

支持不自动关闭的Toast，需要手动关闭。

```javascript
ErrorHandlerEnhanced.showError('重要错误', {
    persistent: true,  // 不自动关闭
    duration: 0         // 或设置duration为0
});
```

### 6. 清除功能 ✅

支持清除所有Toast或指定类型的Toast。

```javascript
// 清除所有Toast
ErrorHandlerEnhanced.clearAll();

// 清除指定类型的Toast
ErrorHandlerEnhanced.clearByType('error');
ErrorHandlerEnhanced.clearByType('success');
```

## 三、完整配置选项

```javascript
ErrorHandlerEnhanced.showError('错误信息', {
    // 基础选项
    title: '错误',              // 标题（可选）
    duration: 5000,             // 显示时长（毫秒），0表示不自动关闭
    position: 'top-end',        // 位置（9个选项）
    showCloseButton: true,      // 是否显示关闭按钮
    icon: 'bi-x-circle-fill',   // 自定义图标
    
    // 增强选项
    showProgress: true,          // 显示进度条
    action: retryFunction,      // 自定义操作函数
    actionText: '重试',         // 操作按钮文本
    persistent: false,          // 是否持久化（不自动关闭）
    group: 'api-errors',        // 分组标识（用于合并）
    merge: false                // 是否合并相同组的消息
});
```

## 四、使用示例

### 1. 带重试功能的错误提示

```javascript
async function createPatientWithRetry(data) {
    try {
        return await PatientAPI.create(data);
    } catch (error) {
        ErrorHandlerEnhanced.handleApiError(error, {
            retry: async () => {
                // 重试创建
                return await PatientAPI.create(data);
            },
            retryText: '重试创建',
            group: 'create-patient',
            merge: true
        });
        throw error;
    }
}
```

### 2. 重要错误（需要手动关闭）

```javascript
try {
    await criticalOperation();
} catch (error) {
    ErrorHandlerEnhanced.showError('重要错误，请立即处理', {
        title: '系统错误',
        persistent: true,  // 不自动关闭
        showCloseButton: true
    });
}
```

### 3. 批量操作错误合并

```javascript
async function batchDelete(ids) {
    const errors = [];
    
    for (const id of ids) {
        try {
            await PatientAPI.delete(id);
            ErrorHandlerEnhanced.showSuccess(`删除 ${id} 成功`, {
                duration: 2000,
                group: 'batch-delete-success',
                merge: true
            });
        } catch (error) {
            errors.push({ id, error });
            ErrorHandlerEnhanced.handleApiError(error, {
                group: 'batch-delete-errors',
                merge: true
            });
        }
    }
    
    if (errors.length > 0) {
        ErrorHandlerEnhanced.showError(
            `删除失败 ${errors.length} 条记录`,
            {
                title: '批量删除结果',
                persistent: true
            }
        );
    }
}
```

### 4. 网络错误重试

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await api.get(url);
        } catch (error) {
            if (i < maxRetries - 1) {
                ErrorHandlerEnhanced.showWarning(
                    `网络错误，${3 - i}秒后重试...`,
                    {
                        duration: 3000,
                        action: () => fetchWithRetry(url, options, maxRetries),
                        actionText: '立即重试',
                        group: 'network-retry',
                        merge: true
                    }
                );
                await new Promise(resolve => setTimeout(resolve, 3000));
            } else {
                ErrorHandlerEnhanced.showError('网络错误，重试失败', {
                    persistent: true
                });
                throw error;
            }
        }
    }
}
```

## 五、样式定制

### 自定义Toast样式

```css
/* 自定义Toast样式 */
.toast.bg-danger {
    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%) !important;
}

/* 自定义进度条颜色 */
.toast-progress-bar {
    background: rgba(255, 255, 255, 0.9) !important;
}

/* 自定义动画 */
.toast {
    animation: customSlideIn 0.3s ease-out;
}
```

## 六、最佳实践

### 1. 错误分组

```javascript
// 将相同类型的错误分组，避免显示太多Toast
ErrorHandlerEnhanced.handleApiError(error, {
    group: 'patient-operations',
    merge: true
});
```

### 2. 重要错误持久化

```javascript
// 重要错误需要手动关闭
ErrorHandlerEnhanced.showError('系统错误', {
    persistent: true,
    title: '严重错误'
});
```

### 3. 操作反馈

```javascript
// 成功操作可以快速关闭
ErrorHandlerEnhanced.showSuccess('操作成功', {
    duration: 2000  // 2秒后自动关闭
});

// 失败操作可以显示重试按钮
ErrorHandlerEnhanced.handleApiError(error, {
    action: retryFunction,
    actionText: '重试',
    persistent: true
});
```

### 4. 批量操作

```javascript
// 批量操作时合并相同类型的提示
for (const item of items) {
    try {
        await processItem(item);
    } catch (error) {
        ErrorHandlerEnhanced.handleApiError(error, {
            group: 'batch-process',
            merge: true
        });
    }
}
```

## 七、API参考

### ErrorHandlerEnhanced.showError(error, options)
显示错误提示（增强版）

### ErrorHandlerEnhanced.showSuccess(message, options)
显示成功提示（增强版）

### ErrorHandlerEnhanced.showWarning(message, options)
显示警告提示（增强版）

### ErrorHandlerEnhanced.showInfo(message, options)
显示信息提示（增强版）

### ErrorHandlerEnhanced.handleApiError(error, options)
处理API错误（增强版）

### ErrorHandlerEnhanced.confirmWithError(message, options)
显示确认对话框（增强版）

### ErrorHandlerEnhanced.clearAll()
清除所有Toast

### ErrorHandlerEnhanced.clearByType(type)
清除指定类型的Toast

## 八、与基础版对比

| 功能 | 基础版 | 增强版 |
|------|--------|--------|
| 基本Toast | ✅ | ✅ |
| Toast队列管理 | ❌ | ✅ |
| 消息合并 | ❌ | ✅ |
| 进度条 | ❌ | ✅ |
| 自定义操作 | ❌ | ✅ |
| 持久化Toast | ❌ | ✅ |
| 清除功能 | ❌ | ✅ |
| 动画效果 | 基础 | 增强 |
| 响应式设计 | 基础 | 优化 |

## 九、注意事项

1. **向后兼容**: 增强版与基础版完全兼容，旧代码无需修改
2. **性能考虑**: Toast队列管理避免同时显示太多Toast
3. **用户体验**: 消息合并减少Toast数量，提升用户体验
4. **自定义样式**: 可以通过CSS自定义Toast样式和动画


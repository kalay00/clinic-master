# TenantAPI初始化错误修复

## 问题描述

```
error-handler.js:283 全局错误: ReferenceError: Cannot access 'TenantAPI' before initialization
    at api.js:867:20
```

## 问题原因

在 `api.js` 文件中，第867行尝试将 `TenantAPI` 赋值给 `window.TenantAPI`，但此时 `TenantAPI` 还没有定义（定义在第872行）。

这是一个典型的**变量提升问题**：

```javascript
// ❌ 错误：在使用前就尝试赋值
window.TenantAPI = TenantAPI;  // 第867行

// TenantAPI的定义在后面
const TenantAPI = {  // 第872行
    // ...
};
```

### JavaScript变量提升规则

- `const` 和 `let` 声明的变量不会被提升到作用域顶部
- 在声明之前访问 `const`/`let` 变量会抛出 `ReferenceError`
- 这就是为什么会出现 "Cannot access 'TenantAPI' before initialization" 错误

## 修复方案

将 `TenantAPI` 的定义移到赋值之前：

```javascript
// ✅ 正确：先定义，后赋值
/**
 * 租户配置API
 */
const TenantAPI = {
    /**
     * 获取租户配置
     * @returns {Promise} 租户配置
     */
    async getConfig() {
        return await api.get('/tenant/config');
    },
    
    /**
     * 更新租户配置
     * @param {object} data - 配置数据 {config: {...}}
     * @returns {Promise} 更新结果
     */
    async updateConfig(data) {
        return await api.put('/tenant/config', data);
    },
    
    /**
     * 获取药师审核状态
     * @returns {Promise} 审核状态
     */
    async getPharmacistReviewStatus() {
        return await api.get('/tenant/pharmacist-review-status');
    }
};

// 然后才赋值给window对象
window.TenantAPI = TenantAPI;
```

## 修复内容

1. **移动TenantAPI定义位置**
   - 从第872行移到第863行（在赋值之前）
   - 确保在使用前已定义

2. **保持代码结构一致**
   - 与其他API的定义顺序保持一致
   - 先定义，后导出到window对象

## 验证步骤

1. **清除浏览器缓存**
   - 强制刷新页面（Ctrl+F5）

2. **检查控制台**
   - 不应该再有 "Cannot access 'TenantAPI' before initialization" 错误

3. **测试TenantAPI功能**
   - 确认 `window.TenantAPI` 可以正常访问
   - 确认相关功能正常工作

## 相关文件

- 修复文件: `/frontend/js/api.js`
- 错误位置: 第867行（修复前）
- 修复后位置: 第863-888行（定义），第897行（赋值）

## 总结

**问题**：变量在使用前未定义（变量提升问题）

**原因**：`TenantAPI` 在赋值给 `window.TenantAPI` 之前未定义

**解决方案**：将 `TenantAPI` 的定义移到赋值之前

**修复状态**：✅ 已修复

修复时间: 2025-11-07 07:30


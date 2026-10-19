# API错误修复总结

## 问题描述

1. **Dashboard API 404错误**：`api/v1/reports/dashboard?date=2025-11-06:1` - 404 Not Found
2. **患者列表API 500错误**：`api/v1/patients?skip=0&limit=10&search=` - 500 Internal Server Error

## 根本原因

### 1. Dashboard API 404错误

- 参数名不匹配：后端使用 `date_param` 作为参数名，但前端传递的是 `date`
- URL参数构建问题：前端可能传递了空值或无效参数

### 2. 患者列表API 500错误

- 搜索逻辑问题：当search为空字符串时，仍然会触发搜索条件
- 哈希搜索问题：搜索身份证号和手机号时，需要先计算哈希值，但代码直接使用原始search值进行匹配
- 错误处理不完善：异常信息没有记录到日志，难以调试

## 解决方案

### 1. 修复Dashboard API参数名

```python
# 修改前
async def get_dashboard_stats(
    request: Request,
    date_param: Optional[str] = Query(None, alias="date", description="日期（YYYY-MM-DD），默认今天"),
    db: Session = Depends(get_db)
):

# 修改后
async def get_dashboard_stats(
    request: Request,
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认今天"),
    db: Session = Depends(get_db)
):
```

### 2. 修复前端URL参数构建

在 `app.js` 的 `get` 方法中，过滤掉空值和undefined：

```javascript
get(url, params = {}) {
    // 过滤掉空值和undefined
    const cleanParams = {};
    for (const [key, value] of Object.entries(params)) {
        if (value !== null && value !== undefined && value !== '') {
            cleanParams[key] = value;
        }
    }
    const queryString = new URLSearchParams(cleanParams).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request(fullUrl, { method: 'GET' });
}
```

### 3. 修复患者列表搜索逻辑

```python
# 修改前
if search:
    query = query.filter(
        or_(
            Patient.patient_no.ilike(f"%{search}%"),
            Patient.id_card_hash == search,
            Patient.phone_hash == search
        )
    )

# 修改后
if search and search.strip():
    # 搜索患者号或哈希字段
    # 注意：身份证号和手机号需要先计算哈希值才能搜索
    from app.core.encryption import hash_for_query
    search_hash = hash_for_query(search.strip())
    query = query.filter(
        or_(
            Patient.patient_no.ilike(f"%{search.strip()}%"),
            Patient.id_card_hash == search_hash,
            Patient.phone_hash == search_hash
        )
    )
```

### 4. 增强错误处理

在患者API中添加详细的错误日志：

```python
except Exception as e:
    from app.core.logger import logger
    logger.error(f"获取患者列表失败: {str(e)}", exc_info=True)
    return error_response(message=f"获取患者列表失败: {str(e)}", code=500)
```

在Dashboard API中添加日期格式验证：

```python
if date:
    try:
        target_date_obj = date.fromisoformat(date)
    except ValueError as e:
        from app.core.logger import logger
        logger.warning(f"日期格式错误: {date}, 错误: {str(e)}")
        target_date_obj = None
```

## 修复的文件

1. `/home/laknl/his/frontend/js/app.js` - 修复URL参数构建，过滤空值
2. `/home/laknl/his/backend/app/api/v1/reports.py` - 修复参数名和日期格式验证
3. `/home/laknl/his/backend/app/api/v1/patients.py` - 增强错误处理
4. `/home/laknl/his/backend/app/repositories/patient_repository.py` - 修复搜索逻辑

## 测试验证

修复后应该能够：
1. ✅ Dashboard API正常返回统计数据
2. ✅ 患者列表API正常返回患者列表
3. ✅ 搜索功能正常工作（支持患者号、身份证号、手机号搜索）

## 注意事项

1. 搜索身份证号和手机号时，系统会先计算哈希值，然后与数据库中的哈希值进行匹配
2. 空字符串搜索会被过滤，不会触发搜索条件
3. 所有API错误现在都会记录详细日志，便于调试


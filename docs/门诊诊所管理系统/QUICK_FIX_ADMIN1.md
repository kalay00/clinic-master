# 快速修复：创建admin1用户

## 问题

登录时提示"用户名或密码错误"，原因是数据库中没有 `admin1` 用户。

## 快速解决方案

### 方案1：运行初始化脚本（推荐）

```bash
cd backend
python3 -m app.core.init_test_data
```

**注意**：如果遇到表结构错误，需要先修复数据库表结构。

### 方案2：手动创建admin1用户

如果初始化脚本有问题，可以手动创建：

```python
from app.core.database import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash

db = SessionLocal()
try:
    # 获取TEST001租户
    tenant = db.query(Tenant).filter(Tenant.code == 'TEST001').first()
    
    # 创建admin1用户
    user = User(
        tenant_id=tenant.id,
        username='admin1',
        password_hash=get_password_hash('111111'),
        real_name='系统管理员',
        email='admin1@test.com',
        status='active'
    )
    db.add(user)
    db.commit()
    print('✓ 已创建admin1用户')
finally:
    db.close()
```

## 登录方式

创建用户后，使用以下方式登录：

1. **用户名**：`admin1`
2. **密码**：`111111`
3. **租户代码**：`TEST001`（在登录页面的租户代码输入框中填写）

## 注意事项

1. 确保数据库表结构正确（已修复 `roles` 表的 `created_by` 和 `updated_by` 字段）
2. 确保租户 `TEST001` 存在
3. 如果密码哈希有问题，可能需要更新 `passlib` 或 `bcrypt` 库


# 数据库初始化修复总结

## 问题描述

使用账号 `admin1`，密码 `111111` 登录时，提示"用户名或密码错误"。

## 根本原因

1. **数据库中没有测试用户**：测试数据（包括admin1用户）尚未初始化
2. **数据库表结构问题**：
   - `roles` 表缺少 `created_by` 和 `updated_by` 字段
   - `role_permissions` 和 `user_roles` 关联表错误地继承了 `BaseModel`，包含不必要的字段
   - `users` 表的 `phone` 字段长度不足（加密后需要255字符）
3. **密码哈希库兼容性问题**：`passlib` 与 `bcrypt 5.0.0` 存在兼容性问题

## 解决方案

### 1. 修复 RolePermission 和 UserRole 模型

将关联表模型改为直接继承 `Base`，而不是 `BaseModel`：

```python
class UserRole(Base):
    """用户角色关联模型（关联表，不继承BaseModel）"""
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, primary_key=True)

class RolePermission(Base):
    """角色权限关联模型（关联表，不继承BaseModel）"""
    __tablename__ = "role_permissions"
    
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False, primary_key=True)
```

### 2. 修复数据库表结构

- 添加 `roles.created_by` 和 `roles.updated_by` 字段
- 修改 `users.phone` 字段长度为 255

### 3. 修复密码哈希函数

直接使用 `bcrypt` 库，避免 `passlib` 的兼容性问题：

```python
import bcrypt

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

### 4. 修复初始化脚本

- 支持幂等性：检查租户、角色、用户是否已存在，避免重复创建
- 在创建患者和药品数据之前先提交用户数据，确保用户创建成功
- 检查表是否存在，如果不存在则跳过相应数据创建

## 执行结果

✅ **admin1用户创建成功！**

**登录信息**：
- 用户名：`admin1`
- 密码：`111111`
- 租户代码：`TEST001`

**提示**：在登录页面的"租户代码"输入框中填写：`TEST001`

## 后续操作

1. 登录系统，使用上述账号信息
2. 如果遇到其他表结构问题，可以运行数据库迁移：
   ```bash
   cd backend
   python -m alembic upgrade head
   ```
3. 如果需要重新初始化数据，可以运行：
   ```bash
   python3 -m app.core.init_test_data
   ```

## 修复的文件

1. `/home/laknl/his/backend/app/models/user.py` - 修复关联表模型
2. `/home/laknl/his/backend/app/core/security.py` - 修复密码哈希函数
3. `/home/laknl/his/backend/app/core/init_test_data.py` - 修复初始化脚本
4. 数据库表结构修复（roles表、users表）


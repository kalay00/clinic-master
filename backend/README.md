# 门诊诊所管理系统 - 后端

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── core/              # 核心模块（配置、数据库等）
│   ├── models/            # 数据模型
│   ├── repositories/      # 数据访问层
│   ├── services/          # 业务服务层
│   ├── utils/             # 工具函数
│   └── main.py            # FastAPI应用入口
├── services/              # 微服务模块
│   ├── user_service/      # 用户服务
│   ├── patient_service/   # 患者服务
│   ├── registration_service/  # 挂号服务
│   ├── treatment_service/     # 诊疗服务
│   ├── payment_service/       # 收费服务
│   ├── pharmacy_service/      # 药房服务
│   ├── report_service/        # 报表服务
│   ├── notification_service/  # 通知服务
│   └── integration_service/   # 对接服务
├── alembic/              # 数据库迁移
├── tests/                # 测试文件
├── requirements.txt      # Python依赖
└── pyproject.toml        # 项目配置
```

## 开发环境设置

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp ../env.example ../.env
# 编辑 .env 文件
```

3. 运行开发服务器：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后，访问：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc


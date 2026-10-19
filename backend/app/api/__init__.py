"""
API路由模块
"""
from fastapi import APIRouter

# 创建API路由器
api_router = APIRouter()

# 直接导入 v1 路由。
# 注意：不再用 try/except 吞掉 ImportError —— 此前该做法会静默掩盖各 module 的导入错误，
# 使 API 退化成最小路由（仅 /status）而应用仍"启动成功"，难以排查。
# 任何路由/模型导入问题都应显式抛出，便于及时发现与修复。
from app.api.v1 import router as v1_router
api_router.include_router(v1_router)

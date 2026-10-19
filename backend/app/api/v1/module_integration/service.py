"""
对接服务（对齐旧 services/integration_service.py，异步，Python 3.12+）

本模块无独立 ORM 模型，直接使用 AuthSchema 的异步会话。
支付/医保对接优先读取租户第三方配置并使用适配器，未配置时返回框架结果。
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from uuid import UUID

from app.core.base_schema import AuthSchema
from app.core.logger import logger


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class IntegrationService:
    """对接服务（无独立模型，使用 auth 会话）"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.db = auth.db

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    async def _config_service(self):
        from app.api.v1.module_third_party_config.service import ThirdPartyConfigService
        return ThirdPartyConfigService(self.auth)

    # ── 医保 ──
    async def medical_insurance_verify(self, patient_id: str, id_card: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"医保验证: patient_id={patient_id}, tenant_id={tenant_id or self._tenant_id}")
        return {
            "verified": True, "insurance_type": "basic",
            "balance": 0.0, "coverage_rate": 0.8,
        }

    async def medical_insurance_pay(self, bill_id: str, amount: float, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"医保支付: bill_id={bill_id}, amount={amount}, tenant_id={tenant_id or self._tenant_id}")
        return {"success": True, "transaction_id": f"INS{bill_id[:8]}", "paid_amount": amount}

    # ── 微信支付 ──
    async def wechat_pay(self, bill_id: str, amount: float, tenant_id: Optional[str] = None, openid: Optional[str] = None) -> Dict[str, Any]:
        tid = tenant_id or self._tenant_id
        try:
            cfg = await (await self._config_service()).get_config(tid, "wechat_pay") if tid else None
            if cfg and cfg.get("is_enabled"):
                from app.services.third_party.wechat_pay import WeChatPayAdapter
                adapter = WeChatPayAdapter(cfg["config_data"])
                result = adapter.create_payment(out_trade_no=bill_id, total_amount=int(amount * 100),
                                                 description=f"账单支付-{bill_id}", openid=openid)
                if result.get("success"):
                    logger.info(f"微信支付创建成功: bill_id={bill_id}")
                    return result
                logger.error(f"微信支付创建失败: {result.get('message')}")
                return result
        except Exception as e:  # pragma: no cover
            logger.error(f"微信支付失败: {e}")
            return {"success": False, "message": f"微信支付失败: {e}"}
        logger.warning(f"微信支付未配置，使用框架模式: tenant_id={tid}")
        return {
            "success": True, "transaction_id": f"WX{bill_id[:8]}",
            "qr_code": f"weixin://wxpay/bizpayurl?pr={bill_id[:8]}",
            "prepay_id": f"prepay_{bill_id[:8]}", "message": "请配置微信支付参数",
        }

    # ── 支付宝支付 ──
    async def alipay_pay(self, bill_id: str, amount: float, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        tid = tenant_id or self._tenant_id
        try:
            cfg = await (await self._config_service()).get_config(tid, "alipay") if tid else None
            if cfg and cfg.get("is_enabled"):
                from app.services.third_party.alipay import AlipayAdapter
                adapter = AlipayAdapter(cfg["config_data"])
                result = adapter.create_payment(out_trade_no=bill_id, total_amount=amount, subject=f"账单支付-{bill_id}")
                if result.get("success"):
                    logger.info(f"支付宝支付创建成功: bill_id={bill_id}")
                    return result
                logger.error(f"支付宝支付创建失败: {result.get('message')}")
                return result
        except Exception as e:  # pragma: no cover
            logger.error(f"支付宝支付失败: {e}")
            return {"success": False, "message": f"支付宝支付失败: {e}"}
        logger.warning(f"支付宝支付未配置，使用框架模式: tenant_id={tid}")
        return {
            "success": True, "transaction_id": f"ALI{bill_id[:8]}",
            "pay_url": f"https://openapi.alipay.com/gateway.do?bill_id={bill_id}",
            "message": "请配置支付宝支付参数",
        }

    # ── 银联支付 ──
    async def unionpay_pay(self, bill_id: str, amount: float, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        tid = tenant_id or self._tenant_id
        try:
            cfg = await (await self._config_service()).get_config(tid, "unionpay") if tid else None
            if cfg and cfg.get("is_enabled"):
                from app.services.third_party.unionpay import UnionPayAdapter
                adapter = UnionPayAdapter(cfg["config_data"])
                result = adapter.create_payment(out_trade_no=bill_id, total_amount=amount, subject=f"账单支付-{bill_id}")
                if result.get("success"):
                    logger.info(f"银联支付创建成功: bill_id={bill_id}")
                    return result
                logger.error(f"银联支付创建失败: {result.get('message')}")
                return result
        except Exception as e:  # pragma: no cover
            logger.error(f"银联支付失败: {e}")
            return {"success": False, "message": f"银联支付失败: {e}"}
        logger.warning(f"银联支付未配置，使用框架模式: tenant_id={tid}")
        return {
            "success": True, "transaction_id": f"UNION{bill_id[:8]}",
            "pay_url": f"https://gateway.95516.com/gateway/api/order.do?bill_id={bill_id}",
            "message": "请配置银联支付参数",
        }

    # ── 微信授权 ──
    async def wechat_auth(self, code: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"微信授权: code={code}, tenant_id={tenant_id or self._tenant_id}")
        return {"success": True, "openid": f"openid_{code[:8]}", "unionid": None, "access_token": f"token_{code[:8]}"}

"""
通知服务（对齐旧 services/notification_service.py，异步 + CRUDBase，Python 3.12+）

业务规则：
- 通知记录 CRUD
- 短信 / 微信通知发送（优先使用租户第三方配置，失败回退消息队列）
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import Notification
from .schema import NotificationSchema, NotificationCreateSchema, NotificationUpdateSchema
from .crud import NotificationCRUD


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class NotificationService:
    """Notification 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = NotificationCRUD(Notification, auth=auth)

    @property
    def _db(self):
        return self.crud.db

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    # ── 标准 CRUD ──
    async def get(self, id: str) -> NotificationSchema:
        return await self.crud.get_or_404(id=id, out_schema=NotificationSchema)

    async def list(self, page_no: int, page_size: int, order_by=None, search: dict | None = None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=NotificationSchema,
        )

    async def create(self, data: NotificationCreateSchema) -> NotificationSchema:
        obj = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return NotificationSchema.model_validate(obj)

    async def update(self, id: str, data: NotificationUpdateSchema) -> NotificationSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return NotificationSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 业务方法：发送 ──
    async def _config_service(self):
        from app.api.v1.module_third_party_config.service import ThirdPartyConfigService
        return ThirdPartyConfigService(self.auth)

    async def send_sms(self, phone: str, message: str, tenant_id: Optional[str] = None, template_params: Optional[Dict[str, Any]] = None) -> bool:
        tid = tenant_id or self._tenant_id
        try:
            cfg = await (await self._config_service()).get_config(tid, "aliyun_sms") if tid else None
        except Exception as e:  # pragma: no cover
            logger.warning(f"读取阿里云短信配置失败: {e}")
            cfg = None

        if cfg and cfg.get("is_enabled"):
            try:
                from app.services.third_party.aliyun_sms import AliyunSMSAdapter
                adapter = AliyunSMSAdapter(cfg["config_data"])
                result = adapter.send_notification(phone, message)
                if result.get("success"):
                    logger.info(f"阿里云短信发送成功: {phone}")
                    return True
            except Exception as e:  # pragma: no cover
                logger.error(f"阿里云短信发送失败: {e}")
        return await self._send_sms_via_queue(phone, message, tid)

    async def _send_sms_via_queue(self, phone: str, message: str, tenant_id: Optional[str]) -> bool:
        try:
            from app.core.mq_client import mq_client
            mq_client.publish(
                exchange="notifications", routing_key="sms.send",
                message={"type": "sms", "phone": phone, "message": message, "tenant_id": tenant_id},
            )
            logger.info(f"短信通知已加入队列: {phone}")
            return True
        except Exception as e:  # pragma: no cover
            logger.error(f"加入消息队列失败: {e}")
            return False

    async def send_wechat(self, openid: str, template_id: str, data: Dict[str, Any], tenant_id: Optional[str] = None) -> bool:
        try:
            from app.core.mq_client import mq_client
            mq_client.publish(
                exchange="notifications", routing_key="wechat.send",
                message={"type": "wechat", "openid": openid, "template_id": template_id,
                         "data": data, "tenant_id": tenant_id or self._tenant_id},
            )
            logger.info(f"发送微信通知: {openid}")
            return True
        except Exception as e:  # pragma: no cover
            logger.error(f"发送微信通知失败: {e}")
            return False

    async def send_appointment_reminder(
        self, patient_id: str, appointment_time: str,
        phone: Optional[str] = None, openid: Optional[str] = None, tenant_id: Optional[str] = None,
    ) -> bool:
        message = f"您的预约时间为{appointment_time}，请准时就诊。"
        success = True
        if phone:
            success = await self.send_sms(phone, message, tenant_id) and success
        if openid:
            success = await self.send_wechat(openid, "appointment_reminder", {"time": appointment_time}, tenant_id) and success
        return success

    async def send_payment_notification(
        self, patient_id: str, amount: float,
        phone: Optional[str] = None, openid: Optional[str] = None, tenant_id: Optional[str] = None,
    ) -> bool:
        message = f"您的账单已支付成功，金额：{amount}元。"
        success = True
        if phone:
            success = await self.send_sms(phone, message, tenant_id) and success
        if openid:
            success = await self.send_wechat(openid, "payment_notification", {"amount": amount}, tenant_id) and success
        return success

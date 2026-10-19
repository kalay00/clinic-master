"""数据库初始化与种子数据管理（对齐 FastapiAdmin: app.scripts.initialize）。

- init_db(): 应用启动时由 main.py 的 lifespan 调用
  - 先异步自动建表（模型有变更自动创建新表）
  - 再初始化基础数据（复用 core/init_db.init_data，幂等：已有数据跳过）
"""

import asyncio

from app.core.database import create_tables
from app.core.init_db import init_data
from app.core.logger import logger

# 关键：启动时建表前必须注册全部模型到 Base.metadata，
# 否则 create_all 会因外键找不到目标表而报 NoReferencedTableError。
from app.core import models  # noqa: F401  (导入即注册)


class InitializeData:
    """初始化数据库表结构与基础数据。"""

    async def init_db(self) -> None:
        """自动建表并写入基础数据。"""
        try:
            # 1. 异步自动建表（create_all 只建不存在的表，模型变更自动生效）
            await create_tables()
            logger.info("✅ 数据库表结构已自动创建")
        except asyncio.TimeoutError:
            logger.error("❌ 数据库表结构初始化超时")
            raise

        # 1.1 补齐历史表缺失字段（create_all 不会 ALTER 已存在表，这里幂等可重复执行）
        try:
            from sqlalchemy import text
            from app.core.database import async_engine
            async with async_engine.begin() as conn:
                await conn.execute(text(
                    "ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS bill_id UUID REFERENCES bills(id)"
                ))
            logger.info("✅ prescriptions.bill_id 字段已补齐")
        except Exception as e:  # pragma: no cover
            logger.warning(f"补齐 prescriptions.bill_id 字段失败（可忽略，字段可能已存在）: {e!s}")

        # 1.2 药品供应商：改为关联 suppliers 表的 supplier_id 外键
        try:
            from sqlalchemy import text
            from app.core.database import async_engine
            async with async_engine.begin() as conn:
                await conn.execute(text(
                    "ALTER TABLE drugs ADD COLUMN IF NOT EXISTS "
                    "supplier_id UUID REFERENCES suppliers(id)"
                ))
                # 删除上一版遗留的自由文本 supplier 列（如存在）
                await conn.execute(text("ALTER TABLE drugs DROP COLUMN IF EXISTS supplier"))
                logger.info("✅ drugs.supplier_id 字段已补齐")
        except Exception as e:  # pragma: no cover
            logger.warning(f"补齐 drugs.supplier_id 字段失败（可忽略，字段可能已存在）: {e!s}")

        # 1.3 患者表：去除敏感字段加密，改为明文存储
        try:
            from sqlalchemy import text
            from app.core.database import async_engine
            async with async_engine.begin() as conn:
                # 1) 先确保明文列存在
                await conn.execute(text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS name VARCHAR(255)"))
                await conn.execute(text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS id_card VARCHAR(18)"))
                await conn.execute(text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS phone VARCHAR(20)"))
                # 2) 若加密列仍存在，先解密回填到明文列（数据迁移，避免丢失）
                enc_exists = (await conn.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name='patients' AND column_name='name_encrypted'"
                ))).fetchone()
                if enc_exists:
                    from app.core.encryption import decrypt_data
                    rows = (await conn.execute(text(
                        "SELECT id, name_encrypted, id_card_encrypted, phone_encrypted "
                        "FROM patients WHERE name IS NULL OR id_card IS NULL"
                    ))).fetchall()
                    for r in rows:
                        name = decrypt_data(r.name_encrypted) if r.name_encrypted else None
                        id_card = decrypt_data(r.id_card_encrypted) if r.id_card_encrypted else None
                        phone = decrypt_data(r.phone_encrypted) if r.phone_encrypted else None
                        await conn.execute(text(
                            "UPDATE patients SET name=:name, id_card=:id_card, phone=:phone WHERE id=:id"
                        ), {"name": name, "id_card": id_card, "phone": phone, "id": r.id})
                    logger.info(f"✅ 已将 {len(rows)} 条患者加密数据解密回填到明文列")
                # 3) 删除加密列与旧索引
                await conn.execute(text("DROP INDEX IF EXISTS uq_patients_tenant_id_card_hash"))
                await conn.execute(text("ALTER TABLE patients DROP COLUMN IF EXISTS name_encrypted"))
                await conn.execute(text("ALTER TABLE patients DROP COLUMN IF EXISTS name_hash"))
                await conn.execute(text("ALTER TABLE patients DROP COLUMN IF EXISTS id_card_encrypted"))
                await conn.execute(text("ALTER TABLE patients DROP COLUMN IF EXISTS id_card_hash"))
                await conn.execute(text("ALTER TABLE patients DROP COLUMN IF EXISTS phone_encrypted"))
                await conn.execute(text("ALTER TABLE patients DROP COLUMN IF EXISTS phone_hash"))
                # 4) 新唯一索引
                await conn.execute(text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_patients_tenant_id_card "
                    "ON patients (tenant_id, id_card) WHERE deleted_at IS NULL"
                ))
            logger.info("✅ patients 表已移除加密列、改为明文存储")
        except Exception as e:  # pragma: no cover
            logger.warning(f"patients 表迁移失败（可忽略，字段可能已存在）: {e!s}")

        # 1.4 业务扩展字段（会员/提成/药品分类）
        try:
            from sqlalchemy import text
            from app.core.database import async_engine

            async def _add_column_if_not_exists(conn, table, column, col_type):
                exists = await conn.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    f"WHERE table_name='{table}' AND column_name='{column}'"
                ))
                if not exists.first():
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))

            async with async_engine.begin() as conn:
                await _add_column_if_not_exists(conn, "patients", "member_level_id", "VARCHAR(36)")
                await _add_column_if_not_exists(conn, "patients", "consumption_total", "NUMERIC(12,2)")
                await _add_column_if_not_exists(conn, "doctors", "commission_plan_id", "VARCHAR(36)")
                await _add_column_if_not_exists(conn, "drugs", "category_id", "UUID")
            logger.info("✅ 业务扩展字段迁移完成")
        except Exception as e:  # pragma: no cover
            logger.warning(f"业务扩展字段迁移失败（可忽略，字段可能已存在）: {e!s}")

        # 1.5 会员资产字段（余额 / 积分 / 抵扣）
        try:
            from sqlalchemy import text
            from app.core.database import async_engine

            async def _add_column_if_not_exists(conn, table, column, col_type):
                exists = await conn.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    f"WHERE table_name='{table}' AND column_name='{column}'"
                ))
                if not exists.first():
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))

            async with async_engine.begin() as conn:
                await _add_column_if_not_exists(conn, "patients", "balance", "NUMERIC(12,2)")
                await _add_column_if_not_exists(conn, "patients", "points", "INTEGER")
                await _add_column_if_not_exists(conn, "projects", "deductible_points", "INTEGER")
                await _add_column_if_not_exists(conn, "bills", "balance_deduction", "NUMERIC(12,2)")
                await _add_column_if_not_exists(conn, "bills", "points_deduction", "INTEGER")
                # 历史数据 NULL 回填为 0，避免 Pydantic 校验报错
                await conn.execute(text("UPDATE bills SET balance_deduction = 0 WHERE balance_deduction IS NULL"))
                await conn.execute(text("UPDATE bills SET points_deduction = 0 WHERE points_deduction IS NULL"))
            logger.info("✅ 会员资产字段迁移完成")
        except Exception as e:  # pragma: no cover
            logger.warning(f"会员资产字段迁移失败（可忽略，字段可能已存在）: {e!s}")

        # 1.6 会员扩展字段（到期时间 / 状态 / 累计储值 / 累计赠送）
        try:
            from sqlalchemy import text
            from app.core.database import async_engine

            async def _add_col(conn, table, column, col_type):
                exists = await conn.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    f"WHERE table_name='{table}' AND column_name='{column}'"
                ))
                if not exists.first():
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))

            async with async_engine.begin() as conn:
                await _add_col(conn, "patients", "member_status", "VARCHAR(20)")
                await _add_col(conn, "patients", "expire_date", "DATE")
                await _add_col(conn, "patients", "stored_total", "NUMERIC(12,2)")
                await _add_col(conn, "patients", "gift_total", "NUMERIC(12,2)")
                await conn.execute(text("UPDATE patients SET member_status = 'active' WHERE member_status IS NULL"))
                await conn.execute(text("UPDATE patients SET stored_total = 0 WHERE stored_total IS NULL"))
                await conn.execute(text("UPDATE patients SET gift_total = 0 WHERE gift_total IS NULL"))
            logger.info("✅ 会员扩展字段迁移完成")
        except Exception as e:  # pragma: no cover
            logger.warning(f"会员扩展字段迁移失败（可忽略，字段可能已存在）: {e!s}")

        # 1.7 费用成本价（用于利润统计）
        try:
            from sqlalchemy import text
            from app.core.database import async_engine

            async def _add_col(conn, table, column, col_type):
                exists = await conn.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    f"WHERE table_name='{table}' AND column_name='{column}'"
                ))
                if not exists.first():
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))

            async with async_engine.begin() as conn:
                await _add_col(conn, "fees", "cost_price", "NUMERIC(10,2)")
                # 历史数据 NULL 回填为 0，便于直接参与利润计算
                await conn.execute(text("UPDATE fees SET cost_price = 0 WHERE cost_price IS NULL"))
            logger.info("✅ fees.cost_price 字段迁移完成")
        except Exception as e:  # pragma: no cover
            logger.warning(f"fees.cost_price 字段迁移失败（可忽略，字段可能已存在）: {e!s}")

        # 2. 初始化基础数据（init_data 内部为同步阻塞操作，放到线程执行，避免阻塞事件循环）
        try:
            await asyncio.to_thread(init_data)
            logger.info("✅ 基础数据初始化完成")
        except Exception:
            logger.error("❌ 基础数据初始化失败")
            raise

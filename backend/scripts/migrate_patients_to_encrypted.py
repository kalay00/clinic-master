"""
迁移 patients 表到新的加密列命名（与 app/models/patient.py 对齐）。

背景：
- 现行 Patient 模型使用 name_encrypted / id_card_encrypted / phone_encrypted /
  name_hash / id_card_hash / phone_hash / allergy_history / chronic_disease 等列。
- 但早期通过 create_core_tables.py / alembic 001 创建的库使用旧命名：
  name / id_card / phone / allergies / medical_history（部分库甚至缺 name_hash）。
- 本脚本在运行时检查实际列，补齐全缺失列，并将旧列重命名/回填，
  不破坏已有数据（旧明文或旧密文都会被正确重新加密并计算查询哈希）。

用法（在 backend 目录下）：
    python scripts/migrate_patients_to_encrypted.py
"""
import asyncio

from sqlalchemy import text

from app.core.database import engine
from app.core.encryption import decrypt_data, encrypt_data, hash_for_query


async def main() -> None:
    # 1. 读取现有列
    async with engine.connect() as conn:
        res = await conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'patients'"
            )
        )
        cols = {row[0] for row in res}

    print(f"现有 patients 列: {sorted(cols)}")

    # 2. 补齐模型需要的列（全部 nullable，避免对存量数据加 NOT NULL 约束）
    needed = {
        "name_encrypted": "VARCHAR(255)",
        "name_hash": "VARCHAR(64)",
        "id_card_encrypted": "VARCHAR(255)",
        "id_card_hash": "VARCHAR(64)",
        "phone_encrypted": "VARCHAR(255)",
        "phone_hash": "VARCHAR(64)",
        "emergency_contact": "VARCHAR(50)",
        "emergency_phone": "VARCHAR(20)",
        "allergy_history": "TEXT",
        "chronic_disease": "TEXT",
        "remark": "TEXT",
    }
    async with engine.begin() as conn:
        for col, typ in needed.items():
            if col not in cols:
                await conn.execute(
                    text(f"ALTER TABLE patients ADD COLUMN {col} {typ}")
                )
                print(f"  + 新增列 {col} {typ}")

    # 3. 旧列重命名到新列（仅当旧列存在且新列尚不存在）
    renames = {
        "name": "name_encrypted",
        "id_card": "id_card_encrypted",
        "phone": "phone_encrypted",
        "allergies": "allergy_history",
        "medical_history": "chronic_disease",
    }
    async with engine.connect() as conn:
        res = await conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'patients'"
            )
        )
        cols = {row[0] for row in res}
    applied_renames = []
    async with engine.begin() as conn:
        for old, new in renames.items():
            if old in cols and new not in cols:
                await conn.execute(
                    text(f"ALTER TABLE patients RENAME COLUMN {old} TO {new}")
                )
                applied_renames.append((old, new))
                print(f"  ~ 重命名列 {old} -> {new}")

    # 4. 回填加密列与查询哈希（兼容旧明文 / 旧密文两种历史数据）
    async with engine.connect() as conn:
        res = await conn.execute(
            text(
                """
                SELECT id, name_encrypted, name_hash,
                       id_card_encrypted, id_card_hash,
                       phone_encrypted, phone_hash
                FROM patients
                """
            )
        )
        rows = res.fetchall()

    updated = 0
    async with engine.begin() as conn:
        for row in rows:
            (
                rid,
                name_enc,
                name_hash_val,
                id_enc,
                id_hash_val,
                phone_enc,
                phone_hash_val,
            ) = row

            upd_name = None
            upd_id = None
            upd_phone = None

            # name
            if name_enc is not None and not name_hash_val:
                plaintext = _coerce_plaintext(name_enc)
                if plaintext is not None:
                    upd_name = (
                        encrypt_data(plaintext),
                        hash_for_query(plaintext),
                    )
            # id_card
            if id_enc is not None and not id_hash_val:
                plaintext = _coerce_plaintext(id_enc)
                if plaintext is not None:
                    upd_id = (
                        encrypt_data(plaintext),
                        hash_for_query(plaintext),
                    )
            # phone
            if phone_enc is not None and not phone_hash_val:
                plaintext = _coerce_plaintext(phone_enc)
                if plaintext is not None:
                    upd_phone = (
                        encrypt_data(plaintext),
                        hash_for_query(plaintext),
                    )

            if upd_name or upd_id or upd_phone:
                sets, params = [], {"rid": rid}
                if upd_name:
                    sets.append("name_encrypted = :name_enc, name_hash = :name_hash")
                    params["name_enc"] = upd_name[0]
                    params["name_hash"] = upd_name[1]
                if upd_id:
                    sets.append(
                        "id_card_encrypted = :id_enc, id_card_hash = :id_hash"
                    )
                    params["id_enc"] = upd_id[0]
                    params["id_hash"] = upd_id[1]
                if upd_phone:
                    sets.append(
                        "phone_encrypted = :phone_enc, phone_hash = :phone_hash"
                    )
                    params["phone_enc"] = upd_phone[0]
                    params["phone_hash"] = upd_phone[1]
                await conn.execute(
                    text(
                        f"UPDATE patients SET {', '.join(sets)} WHERE id = :rid"
                    ),
                    params,
                )
                updated += 1

    print(f"✅ 迁移完成。共扫描 {len(rows)} 条患者记录，回填 {updated} 条。")
    if applied_renames:
        print(f"   重命名: {applied_renames}")


def _coerce_plaintext(value: str):
    """尝试把存储值还原为明文：能解密则解密，否则当作明文。"""
    if value is None:
        return None
    try:
        return decrypt_data(value)
    except Exception:
        # 解密失败 -> 视为明文（旧库历史数据）
        return value


if __name__ == "__main__":
    asyncio.run(main())

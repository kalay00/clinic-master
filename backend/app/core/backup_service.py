"""
数据备份服务：自动备份、手动备份、备份恢复
v2.0新增功能
"""
import os
import json
import gzip
import shutil
import base64
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.logger import logger
from app.core.encryption import EncryptionService
from app.core.database import get_db


class BackupService:
    """数据备份服务"""
    
    def __init__(self):
        """初始化备份服务"""
        self.backup_dir = Path(settings.UPLOAD_DIR) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.encryption_service = EncryptionService()
    
    def create_backup(
        self,
        backup_type: str = "full",
        tenant_id: Optional[UUID] = None,
        description: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        创建数据备份
        
        Args:
            backup_type: 备份类型（full/incremental）
            tenant_id: 租户ID（如果指定，只备份该租户数据）
            description: 备份描述
            db: 数据库会话
        
        Returns:
            Dict: 备份信息
        """
        try:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_dir / f"{backup_id}.sql.gz"
            
            # 获取数据库连接
            if db is None:
                db = next(get_db())
            
            # 执行数据库备份
            # 注意：这里使用pg_dump命令，需要确保系统中有pg_dump工具
            # 或者使用SQLAlchemy导出数据
            
            # 方法1：使用pg_dump（推荐，性能好）
            try:
                import subprocess
                db_url = settings.DATABASE_URL
                
                # 构建pg_dump命令
                cmd = [
                    "pg_dump",
                    db_url,
                    "--format=custom",
                    "--file", str(backup_path),
                ]
                
                # 如果指定了租户，添加WHERE条件（需要在备份脚本中处理）
                if tenant_id:
                    cmd.extend(["--table", "*"])  # 需要根据实际情况调整
                
                # 执行备份
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"pg_dump失败: {result.stderr}")
                
            except FileNotFoundError:
                # 如果pg_dump不可用，使用SQLAlchemy导出（较慢）
                logger.warning("pg_dump不可用，使用SQLAlchemy导出数据（性能较慢）")
                self._backup_with_sqlalchemy(backup_path, tenant_id, db)
            
            # 加密备份文件
            encrypted_backup_path = self._encrypt_backup(backup_path)
            
            # 删除未加密的备份文件
            if backup_path.exists():
                backup_path.unlink()
            
            # 计算备份文件大小
            backup_size = encrypted_backup_path.stat().st_size
            
            backup_info = {
                'backup_id': backup_id,
                'backup_type': backup_type,
                'backup_path': str(encrypted_backup_path),
                'backup_size': backup_size,
                'tenant_id': str(tenant_id) if tenant_id else None,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"备份创建成功: {backup_id}, 大小: {backup_size} bytes")
            
            return backup_info
            
        except Exception as e:
            logger.error(f"创建备份失败: {str(e)}")
            raise
    
    def _backup_with_sqlalchemy(
        self,
        backup_path: Path,
        tenant_id: Optional[UUID],
        db: Session
    ):
        """
        使用SQLAlchemy导出数据（备用方法）
        
        Args:
            backup_path: 备份文件路径
            tenant_id: 租户ID
            db: 数据库会话
        """
        # TODO: 实现SQLAlchemy数据导出
        # 这里先创建一个占位文件
        with open(backup_path, 'w') as f:
            f.write("-- SQLAlchemy backup placeholder\n")
            f.write(f"-- Tenant ID: {tenant_id}\n")
            f.write(f"-- Created at: {datetime.now()}\n")
        
        # 压缩备份文件
        with open(backup_path, 'rb') as f_in:
            with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 删除未压缩的文件
        backup_path.unlink()
        backup_path = Path(f"{backup_path}.gz")
    
    def _encrypt_backup(self, backup_path: Path) -> Path:
        """
        加密备份文件
        
        Args:
            backup_path: 备份文件路径
        
        Returns:
            Path: 加密后的备份文件路径
        """
        try:
            # 读取备份文件
            with open(backup_path, 'rb') as f:
                backup_data = f.read()
            
            # 将二进制数据转换为Base64字符串
            backup_data_b64 = base64.b64encode(backup_data).decode('utf-8')
            
            # 加密备份数据
            encrypted_data = self.encryption_service.encrypt(backup_data_b64)
            
            # 写入加密后的备份文件
            encrypted_backup_path = backup_path.parent / f"{backup_path.stem}.encrypted.gz"
            with open(encrypted_backup_path, 'w') as f:
                f.write(encrypted_data)
            
            return encrypted_backup_path
            
        except Exception as e:
            logger.error(f"加密备份文件失败: {str(e)}")
            raise
    
    def restore_backup(
        self,
        backup_path: str,
        tenant_id: Optional[UUID] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        恢复数据备份
        
        Args:
            backup_path: 备份文件路径
            tenant_id: 租户ID（如果指定，只恢复该租户数据）
            db: 数据库会话
        
        Returns:
            Dict: 恢复信息
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            # 解密备份文件
            decrypted_backup_path = self._decrypt_backup(backup_file)
            
            # 执行数据库恢复
            # 注意：这里使用pg_restore命令，需要确保系统中有pg_restore工具
            
            try:
                import subprocess
                db_url = settings.DATABASE_URL
                
                # 构建pg_restore命令
                cmd = [
                    "pg_restore",
                    "--dbname", db_url,
                    "--clean",
                    "--if-exists",
                    str(decrypted_backup_path),
                ]
                
                # 执行恢复
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"pg_restore失败: {result.stderr}")
                
            except FileNotFoundError:
                # 如果pg_restore不可用，使用SQLAlchemy导入（较慢）
                logger.warning("pg_restore不可用，使用SQLAlchemy导入数据（性能较慢）")
                self._restore_with_sqlalchemy(decrypted_backup_path, tenant_id, db)
            
            # 删除解密后的临时文件
            if decrypted_backup_path.exists():
                decrypted_backup_path.unlink()
            
            restore_info = {
                'backup_path': backup_path,
                'tenant_id': str(tenant_id) if tenant_id else None,
                'restored_at': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"备份恢复成功: {backup_path}")
            
            return restore_info
            
        except Exception as e:
            logger.error(f"恢复备份失败: {str(e)}")
            raise
    
    def _decrypt_backup(self, encrypted_backup_path: Path) -> Path:
        """
        解密备份文件
        
        Args:
            encrypted_backup_path: 加密的备份文件路径
        
        Returns:
            Path: 解密后的备份文件路径
        """
        try:
            # 读取加密的备份文件
            with open(encrypted_backup_path, 'r') as f:
                encrypted_data = f.read()
            
            # 解密备份数据
            decrypted_data_b64 = self.encryption_service.decrypt(encrypted_data)
            
            # 将Base64字符串转换为二进制数据
            decrypted_data = base64.b64decode(decrypted_data_b64)
            
            # 写入解密后的备份文件
            decrypted_backup_path = encrypted_backup_path.parent / f"{encrypted_backup_path.stem}.decrypted.gz"
            with open(decrypted_backup_path, 'wb') as f:
                f.write(decrypted_data)
            
            return decrypted_backup_path
            
        except Exception as e:
            logger.error(f"解密备份文件失败: {str(e)}")
            raise
    
    def _restore_with_sqlalchemy(
        self,
        backup_path: Path,
        tenant_id: Optional[UUID],
        db: Session
    ):
        """
        使用SQLAlchemy导入数据（备用方法）
        
        Args:
            backup_path: 备份文件路径
            tenant_id: 租户ID
            db: 数据库会话
        """
        # TODO: 实现SQLAlchemy数据导入
        logger.warning("SQLAlchemy数据导入功能待实现")
    
    def list_backups(
        self,
        tenant_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出备份文件
        
        Args:
            tenant_id: 租户ID（如果指定，只列出该租户的备份）
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 备份文件列表
        """
        try:
            backups = []
            
            # 扫描备份目录
            for backup_file in self.backup_dir.glob("*.encrypted.gz"):
                try:
                    stat = backup_file.stat()
                    backups.append({
                        'backup_id': backup_file.stem.replace('.encrypted', ''),
                        'backup_path': str(backup_file),
                        'backup_size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                except Exception as e:
                    logger.warning(f"读取备份文件信息失败: {backup_file}, {str(e)}")
            
            # 按创建时间倒序排序
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            # 应用限制
            if limit > 0:
                backups = backups[:limit]
            
            return backups
            
        except Exception as e:
            logger.error(f"列出备份文件失败: {str(e)}")
            raise
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        删除备份文件
        
        Args:
            backup_path: 备份文件路径
        
        Returns:
            bool: 是否删除成功
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            backup_file.unlink()
            
            logger.info(f"备份文件删除成功: {backup_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"删除备份文件失败: {str(e)}")
            raise


# 创建全局备份服务实例
backup_service = BackupService()


"""
收费服务：费用计算、账单管理、支付管理
"""
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from app.api.v1.module_payment.model import Bill, Payment
from app.repositories.payment_repository import BillRepository, PaymentRepository
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger
from app.utils.common import generate_id


class PaymentService:
    """收费服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.bill_repo = BillRepository(db)
        self.payment_repo = PaymentRepository(db)
    
    def calculate_bill_amount(
        self,
        registration_price: Decimal = Decimal("0"),
        treatment_price: Decimal = Decimal("0"),
        pharmacy_price: Decimal = Decimal("0"),
        discount: Decimal = Decimal("0"),
        insurance_amount: Decimal = Decimal("0")
    ) -> Dict[str, Any]:
        """
        计算账单金额
        
        Args:
            registration_price: 挂号费
            treatment_price: 诊疗费
            pharmacy_price: 药费
            discount: 优惠金额
            insurance_amount: 医保支付金额
        
        Returns:
            Dict[str, Any]: 费用计算结果
        """
        total_amount = registration_price + treatment_price + pharmacy_price
        actual_amount = total_amount - discount - insurance_amount
        
        return {
            "total_amount": float(total_amount),
            "discount_amount": float(discount),
            "insurance_amount": float(insurance_amount),
            "actual_amount": float(actual_amount) if actual_amount > 0 else 0.0
        }
    
    def create_bill(
        self,
        bill_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> Bill:
        """创建账单"""
        # 生成账单号
        bill_no = f"BILL{generate_id()[:8].upper()}"
        bill_data["bill_no"] = bill_no
        
        # 计算总金额
        if "items" in bill_data and bill_data["items"]:
            total = Decimal("0")
            for item in bill_data["items"]:
                total += Decimal(str(item.get("amount", 0)))
            bill_data["total_amount"] = total
        
        bill = self.bill_repo.create_bill(bill_data, tenant_id)
        bill.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建账单: {bill.id} by {creator_id}")
        return bill
    
    def get_bill(self, bill_id: str, tenant_id: str) -> Bill:
        """获取账单详情"""
        bill = self.bill_repo.get_bill_by_id(bill_id, tenant_id)
        if not bill:
            raise NotFoundException("账单", bill_id)
        return bill
    
    def list_bills(
        self,
        tenant_id: str,
        patient_id: Optional[str] = None,
        registration_id: Optional[str] = None,
        status: Optional[str] = None,
        bill_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Bill], int]:
        """获取账单列表"""
        return self.bill_repo.get_bills(
            tenant_id, patient_id, registration_id, status, bill_type, skip, limit
        )
    
    def pay_bill(
        self,
        bill_id: str,
        tenant_id: str,
        payment_method: str,
        amount: Decimal,
        transaction_id: Optional[str] = None
    ) -> Payment:
        """支付账单"""
        bill = self.get_bill(bill_id, tenant_id)
        
        if bill.status == "paid":
            raise BusinessException("账单已支付", code=400)
        
        if amount < (bill.total_amount - bill.paid_amount - bill.insurance_amount):
            raise BusinessException("支付金额不足", code=400)
        
        # 创建支付记录
        payment_no = f"PAY{generate_id()[:8].upper()}"
        payment_data = {
            "payment_no": payment_no,
            "bill_id": bill_id,
            "patient_id": str(bill.patient_id),
            "payment_method": payment_method,
            "amount": amount,
            "status": "success",
            "transaction_id": transaction_id,
        }
        
        payment = self.payment_repo.create_payment(payment_data, tenant_id)
        
        # 更新账单状态
        bill.paid_amount += amount
        if bill.paid_amount >= (bill.total_amount - bill.insurance_amount):
            bill.status = "paid"
            bill.payment_method = payment_method
            from datetime import datetime
            bill.payment_time = datetime.now()
        
        # 如果是挂号费账单，同步更新挂号状态
        if bill.bill_type == "registration" and bill.registration_id:
            from app.repositories.registration_repository import RegistrationRepository
            from uuid import UUID
            
            registration_repo = RegistrationRepository(self.db)
            try:
                registration_id_uuid = UUID(bill.registration_id) if isinstance(bill.registration_id, str) else bill.registration_id
                registration = registration_repo.get_registration_by_id(str(registration_id_uuid), tenant_id)
                
                if registration:
                    # 更新挂号支付信息
                    registration.paid_amount = bill.paid_amount
                    
                    # 如果已全额支付，更新支付状态
                    if bill.paid_amount >= (bill.total_amount - bill.insurance_amount):
                        registration.payment_status = "paid"
                        registration.payment_method = payment_method
                    else:
                        registration.payment_status = "partial"
                    
                    logger.info(f"同步更新挂号支付状态: {registration.id}, 金额: {bill.paid_amount}")
            except Exception as e:
                logger.warning(f"同步更新挂号状态失败: {str(e)}", exc_info=True)
        
        self.db.commit()
        
        logger.info(f"支付账单: {bill_id}, 金额: {amount}")
        return payment
    
    def refund_bill(
        self,
        bill_id: str,
        tenant_id: str,
        refund_amount: Decimal,
        reason: Optional[str] = None
    ) -> Bill:
        """退费"""
        bill = self.get_bill(bill_id, tenant_id)
        
        if bill.status != "paid":
            raise BusinessException("只有已支付账单可以退费", code=400)
        
        if refund_amount > bill.paid_amount:
            raise BusinessException("退费金额不能超过已支付金额", code=400)
        
        # 更新账单
        bill.paid_amount -= refund_amount
        if bill.paid_amount == 0:
            bill.status = "refunded"
        else:
            bill.status = "partial_refunded"
        
        # 如果是挂号费账单，同步更新挂号状态
        if bill.bill_type == "registration" and bill.registration_id:
            from app.repositories.registration_repository import RegistrationRepository
            from uuid import UUID
            
            registration_repo = RegistrationRepository(self.db)
            try:
                registration_id_uuid = UUID(bill.registration_id) if isinstance(bill.registration_id, str) else bill.registration_id
                registration = registration_repo.get_registration_by_id(str(registration_id_uuid), tenant_id)
                
                if registration:
                    # 更新挂号支付信息
                    registration.paid_amount = bill.paid_amount
                    
                    # 更新支付状态
                    if bill.paid_amount <= 0:
                        registration.payment_status = "refunded"
                    else:
                        registration.payment_status = "partial"
                    
                    logger.info(f"同步更新挂号退费状态: {registration.id}, 金额: {bill.paid_amount}")
            except Exception as e:
                logger.warning(f"同步更新挂号状态失败: {str(e)}", exc_info=True)
        
        if reason:
            bill.remark = f"{bill.remark or ''}\n退费原因: {reason}"
        
        self.db.commit()
        
        logger.info(f"退费账单: {bill_id}, 金额: {refund_amount}")
        return bill
    
    def list_payments(
        self,
        tenant_id: str,
        bill_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Payment], int]:
        """获取支付记录列表"""
        return self.payment_repo.get_payments(
            tenant_id, bill_id, patient_id, status, skip, limit
        )


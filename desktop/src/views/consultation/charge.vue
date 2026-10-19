<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">收费</div>
      </div>
    </div>

    <div class="his-card charge-card">
      <div class="charge-header">
        <span class="charge-label">应收金额</span>
        <span class="charge-amount">{{ receivable.toFixed(2) }}元</span>
      </div>

      <div class="charge-form">
        <div class="charge-row">
          <label>优惠金额</label>
          <div class="charge-input-wrap">
            <input class="his-input" v-model="form.discount" />
            <span class="charge-unit">元</span>
          </div>
          <label class="charge-label-inline">折扣</label>
          <div class="charge-input-wrap short">
            <input class="his-input" v-model="form.discountRate" />
            <span class="charge-unit">折</span>
          </div>
        </div>

        <div class="charge-row">
          <label>医保支付</label>
          <div class="charge-input-wrap">
            <input class="his-input" v-model="form.insurance" />
            <span class="charge-unit">元</span>
          </div>
        </div>

        <div class="charge-row">
          <label>实收金额</label>
          <div class="charge-input-wrap">
            <input class="his-input actual-input" v-model="form.actual" />
            <span class="charge-unit">元</span>
          </div>
        </div>

        <div class="charge-row">
          <label>找零</label>
          <div class="charge-input-wrap">
            <input class="his-input change-input" :value="change.toFixed(2)" readonly />
            <span class="charge-unit">元</span>
          </div>
        </div>

        <div class="charge-row">
          <label>支付方式</label>
          <div class="pay-methods">
            <label v-for="method in payMethods" :key="method.key" class="pay-method">
              <input type="radio" :value="method.key" v-model="form.payMethod" />
              <span>{{ method.label }}</span>
            </label>
          </div>
        </div>

        <div class="charge-row">
          <label>收款备注</label>
          <input class="his-input" v-model="form.remark" style="flex: 1" />
        </div>
      </div>

      <div class="charge-actions">
        <button class="his-btn his-btn-default" @click="onCancel">取消</button>
        <button class="his-btn his-btn-primary" @click="onConfirm">确定收费</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPrescriptions } from '@/api/treatment'
import { createBill, payBill } from '@/api/payment'
import { getRegistration } from '@/api/registration'

const router = useRouter()
const route = useRoute()

const regId = computed(() => route.query.regId || '')
const patientId = ref('')
const registrationId = ref('')
const billingItems = ref([])

onMounted(async () => {
  if (regId.value) {
    try {
      const reg = await getRegistration(regId.value)
      registrationId.value = reg.id || regId.value
      patientId.value = reg.patient_id || ''
    } catch (e) { /* 忽略 */ }
  }
  await loadPrescription()
})

// 取当前挂号未结处方，作为收费项目
const loadPrescription = async () => {
  if (!patientId.value) return
  try {
    const res = await getPrescriptions({ patient_id: patientId.value, registration_id: registrationId.value, page: 1, page_size: 50 })
    const prescriptions = res.items || []
    const items = []
    prescriptions.forEach(p => {
      const list = Array.isArray(p.items) ? p.items : []
      list.forEach(it => {
        const price = Number(it.price || 0)
        const total = Number(it.total || 1)
        items.push({ name: it.name, amount: price * total })
      })
    })
    billingItems.value = items
    form.actual = receivable.value.toFixed(2)
  } catch (e) {
    billingItems.value = []
  }
}

const receivable = computed(() => {
  return billingItems.value.reduce((sum, it) => sum + Number(it.amount || 0), 0)
})

const payMethods = [
  { key: 'cash', label: '现金' },
  { key: 'alipay', label: '支付宝' },
  { key: 'wechat', label: '微信' },
  { key: 'card', label: '银行卡' },
  { key: 'member', label: '会员卡' },
]

const form = reactive({
  discount: '',
  discountRate: '',
  insurance: '',
  actual: '',
  payMethod: 'cash',
  remark: '',
})

const actualAmount = computed(() => Number(form.actual || receivable.value || 0))

const change = computed(() => {
  return Math.max(0, actualAmount.value - receivable.value)
})

const onCancel = () => router.back()
const onConfirm = async () => {
  if (!patientId.value) {
    ElMessage.warning('缺少就诊患者信息')
    return
  }
  try {
    const bill = await createBill({
      patient_id: patientId.value,
      registration_id: registrationId.value,
      bill_type: 'consultation',
      total_amount: receivable.value,
      items: billingItems.value,
    })
    const billId = bill.id || bill.data?.id
    await payBill(billId, {
      payment_method: form.payMethod,
      amount: actualAmount.value,
      remark: form.remark,
    })
    ElMessage.success('收费成功')
    router.push('/consultation/charge/confirm')
  } catch (e) {
    ElMessage.error('收费失败')
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';

.charge-card {
  max-width: 500px;
  margin: 0 auto;
  padding: 24px;
}
.charge-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 12px 16px;
  background: #e8eaff;
  border-radius: 6px;
  margin-bottom: 24px;
}
.charge-label {
  font-size: 14px;
  color: #4b5563;
}
.charge-amount {
  font-size: 20px;
  font-weight: 700;
  color: #374151;
}
.charge-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}
.charge-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.charge-row > label {
  width: 80px;
  font-size: 14px;
  color: #374151;
  text-align: right;
  flex-shrink: 0;
}
.charge-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}
.charge-input-wrap.short {
  flex: 0 0 140px;
}
.charge-input-wrap .his-input {
  flex: 1;
  text-align: right;
}
.actual-input {
  color: #f59e0b;
  font-weight: 600;
}
.change-input {
  background: #f3f4f6;
}
.charge-unit {
  font-size: 14px;
  color: #6b7280;
  width: 20px;
}
.charge-label-inline {
  width: auto !important;
}
.pay-methods {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.pay-method {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
}
.charge-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

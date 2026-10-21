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
        <div class="charge-items">
          <div class="charge-items-title">待收费项目</div>
          <div v-if="!billingBills.length" class="charge-items-empty">暂无待收费账单</div>
          <div v-for="b in billingBills" :key="b.id" class="charge-item">
            <span>{{ billTypeLabel[b.bill_type] || b.bill_type }}（{{ b.bill_no || '' }}）</span>
            <span class="charge-item-amount">¥{{ Number(b.total_amount || 0).toFixed(2) }}</span>
          </div>
        </div>

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
import { getBills, payBill } from '@/api/payment'
import { getRegistration } from '@/api/registration'

const router = useRouter()
const route = useRoute()

const regId = computed(() => route.query.regId || '')
const patientId = ref('')
const registrationId = ref('')
// 本次挂账下未结的账单（挂号费单 + 处方自动生成的处方单）
const billingBills = ref([])
const billTypeLabel = {
  registration: '挂号费',
  prescription: '处方费',
  consultation: '诊疗费',
  treatment: '治疗费',
  pharmacy: '药品费',
}

onMounted(async () => {
  if (regId.value) {
    try {
      const reg = await getRegistration(regId.value)
      registrationId.value = reg.id || regId.value
      patientId.value = reg.patient_id || ''
    } catch (e) { /* 忽略 */ }
  }
  if (route.query.patientId && !patientId.value) patientId.value = route.query.patientId
  await loadBills()
})

// 拉取患者未结账单；有挂号单时只收本次挂号的账，并过滤 0 元历史脏单
const loadBills = async () => {
  if (!patientId.value) return
  try {
    const res = await getBills({ patient_id: patientId.value, status: 'unpaid', page: 1, page_size: 100 })
    const all = res.items || []
    billingBills.value = all.filter(
      b => Number(b.total_amount || 0) > 0
        && (registrationId.value ? b.registration_id === registrationId.value : true)
    )
    form.actual = receivable.value.toFixed(2)
  } catch (e) {
    billingBills.value = []
  }
}

const receivable = computed(() => {
  return billingBills.value.reduce((sum, b) => sum + Number(b.total_amount || 0), 0)
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
  if (!billingBills.value.length) {
    ElMessage.warning('没有待收款的账单')
    return
  }
  try {
    // 逐单收款；处方单收费后后端会自动将处方标记为已收费，方可发药
    let firstBillId = ''
    for (const b of billingBills.value) {
      await payBill(b.id, {
        payment_method: form.payMethod,
        amount: Number(b.total_amount || 0),
        remark: form.remark,
      })
      if (!firstBillId) firstBillId = b.id
    }
    ElMessage.success('收费成功')
    // 跳转到账单详情（原 /consultation/charge/confirm 路由不存在，会进 404）
    router.push(`/charge/detail/${firstBillId}`)
  } catch (e) {
    ElMessage.error(e?.message || '收费失败')
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

.charge-items {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 12px 14px;
  margin-bottom: 18px;

  .charge-items-title {
    font-weight: 600;
    margin-bottom: 8px;
    color: #303133;
  }

  .charge-items-empty {
    color: #909399;
    font-size: 13px;
    padding: 6px 0;
  }

  .charge-item {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    padding: 4px 0;
    color: #606266;

    .charge-item-amount {
      color: #f56c6c;
      font-weight: 600;
    }
  }
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

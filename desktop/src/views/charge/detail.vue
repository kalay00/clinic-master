<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">账单详情</div>
      <div class="head-actions">
        <el-button v-if="bill.status === 'unpaid'" type="primary" :icon="Money" @click="showPay = true">收费</el-button>
        <el-button v-if="bill.status === 'paid'" type="warning" :icon="RefreshLeft" @click="onRefund">退费</el-button>
        <el-button type="primary" plain :icon="Printer" @click="onPrint">打印收费单</el-button>
        <el-button :icon="Back" @click="onBack">返回</el-button>
      </div>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="16">
        <el-card class="page-card" shadow="never">
          <div class="section-title">项目明细</div>
          <el-table :data="items" border stripe>
            <el-table-column type="index" label="序号" width="55" />
            <el-table-column prop="name" label="收费名称" min-width="160" />
            <el-table-column prop="price" label="单价（元）" width="100">
              <template #default="{ row }">{{ formatMoney(row.price) }}</template>
            </el-table-column>
            <el-table-column prop="qty" label="数量" width="70" />
            <el-table-column prop="unit" label="单位" width="70" />
            <el-table-column prop="amount" label="金额（元）" width="110">
              <template #default="{ row }">{{ formatMoney(row.amount) }}</template>
            </el-table-column>
          </el-table>
          <div class="summary-bar">
            <span>应收金额：{{ formatMoney(bill.total_amount) }}元</span>
            <span class="ml-lg">优惠：{{ formatMoney(bill.discount_amount) }}元</span>
            <span class="ml-lg">医保：{{ formatMoney(bill.insurance_amount) }}元</span>
            <span class="ml-lg total">实收：{{ formatMoney(bill.paid_amount) }}</span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="page-card" shadow="never">
          <div class="section-title">账单信息</div>
          <el-descriptions :column="1" border class="info-list">
            <el-descriptions-item label="账单编号">{{ bill.bill_no }}</el-descriptions-item>
            <el-descriptions-item label="账单类型">{{ billTypeMap[bill.bill_type] || bill.bill_type }}</el-descriptions-item>
            <el-descriptions-item label="应收金额（元）">{{ formatMoney(bill.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="实收金额（元）">{{ formatMoney(bill.paid_amount) }}</el-descriptions-item>
            <el-descriptions-item label="优惠金额（元）">{{ formatMoney(bill.discount_amount) }}</el-descriptions-item>
            <el-descriptions-item label="医保支付（元）">{{ formatMoney(bill.insurance_amount) }}</el-descriptions-item>
            <el-descriptions-item label="余额抵扣（元）">{{ formatMoney(bill.balance_deduction) }}</el-descriptions-item>
            <el-descriptions-item label="积分抵扣">{{ bill.points_deduction || 0 }}</el-descriptions-item>
            <el-descriptions-item label="支付方式">{{ bill.payment_method ? payMethodMap[bill.payment_method] || bill.payment_method : '-' }}</el-descriptions-item>
            <el-descriptions-item label="收费状态">
              <el-tag :type="statusTag(bill.status)" size="small">{{ statusMap[bill.status] || bill.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="收费时间">{{ bill.payment_time || '-' }}</el-descriptions-item>
          </el-descriptions>

          <div class="section-title">患者信息</div>
          <el-descriptions :column="1" border class="info-list">
            <el-descriptions-item label="患者姓名">{{ bill.patient_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="账单备注">{{ bill.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 收费弹窗 -->
    <el-dialog v-model="showPay" title="确认收费" width="520px" :close-on-click-modal="false">
      <el-form label-width="110px">
        <el-form-item label="应收金额">
          <span class="money">{{ formatMoney(payable) }} 元</span>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="payForm.payment_method">
            <el-radio label="cash">现金</el-radio>
            <el-radio label="wechat">微信</el-radio>
            <el-radio label="alipay">支付宝</el-radio>
            <el-radio label="unionpay">银联</el-radio>
            <el-radio label="insurance">医保</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="收款金额（元）">
          <el-input v-model="payForm.amount" type="number" style="width: 180px" />
        </el-form-item>
        <el-form-item label="使用余额">
          <el-switch v-model="payForm.use_balance" />
          <span class="ml-lg tip">余额：{{ formatMoney(patientBalance) }} 元</span>
        </el-form-item>
        <el-form-item label="使用积分">
          <el-input-number v-model="payForm.use_points" :min="0" :max="patientPoints" />
          <span class="ml-lg tip">可用积分：{{ patientPoints }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPay = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onConfirmPay">确认收款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Money, RefreshLeft, Printer, Back } from '@element-plus/icons-vue'
import { getBill, payBill } from '@/api/payment'

defineOptions({ name: 'OrderDetail' })

const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.id)
const mode = computed(() => route.query.mode || '')

const loading = ref(false)
const submitting = ref(false)
const bill = reactive({})
const items = ref([])
const patientBalance = ref(0)
const patientPoints = ref(0)

const showPay = ref(false)
const payForm = reactive({ payment_method: 'cash', amount: '', use_balance: false, use_points: 0 })

const billTypeMap = { registration: '挂号', treatment: '诊疗', prescription: '处方', pharmacy: '药房' }
const payMethodMap = { cash: '现金', wechat: '微信', alipay: '支付宝', unionpay: '银联', insurance: '医保', medical_insurance: '医保' }
const statusMap = { unpaid: '待收费', paid: '已收费', refunded: '已退费', partial_refunded: '部分退费' }
const statusTag = (s) => s === 'unpaid' ? 'warning' : (s === 'paid' ? 'success' : 'info')
const formatMoney = (v) => v == null ? '0.00' : Number(v).toFixed(2)

const payable = computed(() => {
  const total = Number(bill.total_amount || 0)
  const insurance = Number(bill.insurance_amount || 0)
  const paid = Number(bill.paid_amount || 0)
  return Math.max(0, round2(total - insurance - paid))
})

async function fetchDetail() {
  loading.value = true
  try {
    const data = await getBill(id.value)
    Object.assign(bill, data)
    items.value = Array.isArray(data.items) ? data.items : []
  } catch (e) {
    ElMessage.error('加载账单详情失败')
  } finally {
    loading.value = false
  }
}

const round2 = (n) => Math.round(n * 100) / 100

const onConfirmPay = async () => {
  if (!payForm.amount && !payForm.use_balance && !payForm.use_points) {
    ElMessage.warning('请填写收款金额或选择抵扣方式')
    return
  }
  const amount = round2(Number(payForm.amount) || 0)
  if (amount < round2(payable.value) && !payForm.use_balance && !payForm.use_points) {
    ElMessage.warning(`收款金额不足，还需 ¥${payable.value.toFixed(2)}`)
    return
  }
  submitting.value = true
  try {
    await payBill(id.value, {
      payment_method: payForm.payment_method,
      amount,
      use_balance: payForm.use_balance,
      use_points: payForm.use_points
    })
    ElMessage.success('收费成功')
    showPay.value = false
    await fetchDetail()
  } catch (e) {
    ElMessage.error(e?.message || '收费失败')
  } finally {
    submitting.value = false
  }
}

const onRefund = () => router.push(`/charge/refund/${id.value}`)
const onPrint = () => ElMessage.info('打印功能开发中')
const onBack = () => router.back()

onMounted(() => {
  fetchDetail()
  if (mode.value === 'pay') showPay.value = true
})
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.head-actions { display: flex; gap: 10px; }
.section-title { font-size: 16px; font-weight: 600; color: #5b7cff; margin: 0 0 16px; padding-left: 12px; border-left: 4px solid #5b7cff; }
.summary-bar { margin-top: 16px; text-align: right; font-size: 14px; color: #606266; .total { color: #f56c6c; font-weight: 600; } }
.info-list { margin-bottom: 20px; }
.money { color: #f56c6c; font-weight: 600; font-size: 16px; }
.tip { color: #909399; font-size: 13px; }
.ml-lg { margin-left: 16px; }
</style>

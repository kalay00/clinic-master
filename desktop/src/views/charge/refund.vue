<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">退费办理</div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="16">
        <el-card class="page-card" shadow="never">
          <div class="section-title">收费项目</div>
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
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="page-card" shadow="never">
          <div class="section-title">账单信息</div>
          <el-descriptions :column="1" border class="info-list">
            <el-descriptions-item label="账单编号">{{ bill.bill_no }}</el-descriptions-item>
            <el-descriptions-item label="患者姓名">{{ bill.patient_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="账单类型">{{ billTypeMap[bill.bill_type] || bill.bill_type }}</el-descriptions-item>
            <el-descriptions-item label="实收金额（元）">{{ formatMoney(bill.paid_amount) }}</el-descriptions-item>
            <el-descriptions-item label="收费状态">
              <el-tag :type="statusTag(bill.status)" size="small">{{ statusMap[bill.status] || bill.status }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <div class="section-title">退费</div>
          <el-form label-width="90px">
            <el-form-item label="退费金额">
              <el-input v-model="refundForm.amount" type="number" style="width: 160px">
                <template #append>元</template>
              </el-input>
            </el-form-item>
            <el-form-item label="退费原因">
              <el-input v-model="refundForm.reason" type="textarea" :rows="3" placeholder="请输入退费原因" />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" :loading="submitting" :icon="RefreshLeft" @click="onConfirmRefund">确认退费</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshLeft, Back } from '@element-plus/icons-vue'
import { getBill, refundBill } from '@/api/payment'

defineOptions({ name: 'ChargeRefund' })

const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.billId)

const loading = ref(false)
const submitting = ref(false)
const bill = reactive({})
const items = ref([])

const refundForm = reactive({ amount: '', reason: '' })

const billTypeMap = { registration: '挂号', treatment: '诊疗', prescription: '处方', pharmacy: '药房' }
const statusMap = { unpaid: '待收费', paid: '已收费', refunded: '已退费', partial_refunded: '部分退费' }
const statusTag = (s) => s === 'unpaid' ? 'warning' : (s === 'paid' ? 'success' : 'info')
const formatMoney = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function fetchDetail() {
  loading.value = true
  try {
    const data = await getBill(id.value)
    Object.assign(bill, data)
    items.value = Array.isArray(data.items) ? data.items : []
    refundForm.amount = formatMoney(bill.paid_amount)
  } catch (e) {
    ElMessage.error('加载账单失败')
  } finally {
    loading.value = false
  }
}

const onConfirmRefund = async () => {
  const amount = Number(refundForm.amount) || 0
  if (amount <= 0) { ElMessage.warning('请输入有效的退费金额'); return }
  try {
    await ElMessageBox.confirm(`确认退费 ¥${amount.toFixed(2)} ？`, '退费确认', { type: 'warning' })
  } catch { return }
  submitting.value = true
  try {
    await refundBill(id.value, { refund_amount: amount, reason: refundForm.reason })
    ElMessage.success('退费成功')
    router.push('/charge/refunded')
  } catch (e) {
    ElMessage.error(e?.message || '退费失败')
  } finally {
    submitting.value = false
  }
}

const onBack = () => router.back()

onMounted(fetchDetail)
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-title { font-size: 16px; font-weight: 600; color: #5b7cff; margin: 0 0 16px; padding-left: 12px; border-left: 4px solid #5b7cff; }
.info-list { margin-bottom: 20px; }
</style>

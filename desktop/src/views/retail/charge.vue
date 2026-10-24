<template>
  <div class="retail-charge-page">
    <el-card class="page-card" shadow="never" v-loading="loading">
      <div class="card-header">
        <span class="card-title">零售收费</span>
        <el-button :icon="Back" @click="onBack">返回</el-button>
      </div>

      <div class="page-body">
        <div class="his-section-title">患者信息</div>
        <div class="retail-patient-form">
          <el-select v-model="patientId" filterable remote placeholder="输入姓名/档案号/手机号搜索患者" :remote-method="searchPatients" :loading="pLoading" style="width: 320px" @change="onPatientChange">
            <el-option v-for="p in patientOptions" :key="p.id" :label="`${p.name}（${p.patient_no}）`" :value="p.id" />
          </el-select>
          <el-button link type="primary" @click="onAddPatient">新增患者</el-button>
          <el-input v-model="patientName" placeholder="散客姓名（可选）" style="width: 160px" />
        </div>

        <div class="his-section-title" style="margin-top:20px">药品明细</div>
        <div class="table-wrap" ref="wrapRef">
          <el-table :data="items" border stripe ref="tableRef" :height="tableHeight">
            <el-table-column type="index" label="序号" width="55" />
            <el-table-column prop="name" label="药品名称" min-width="160" />
            <el-table-column prop="specification" label="规格" width="120" />
            <el-table-column prop="price" label="单价（元）" width="100">
              <template #default="{ row }">{{ fmt(row.price) }}</template>
            </el-table-column>
            <el-table-column label="数量" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.qty" :min="1" :max="999" size="small" @change="recount" />
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="70" />
            <el-table-column label="金额（元）" width="110">
              <template #default="{ row }">{{ fmt(row.price * row.qty) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row, $index }">
                <el-button type="danger" link @click="items.splice($index, 1); recount()">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="retail-add">
          <el-button type="primary" plain :icon="Plus" @click="onPick">添加药品</el-button>
        </div>

        <div class="retail-summary">
          <span>合计金额：<b class="retail-total">{{ fmt(totalAmount) }}</b> 元</span>
        </div>

        <div class="his-section-title" style="margin-top:20px">收费方式</div>
        <el-form label-width="100px">
          <el-form-item label="支付方式">
            <el-radio-group v-model="payForm.payment_method">
              <el-radio label="cash">现金</el-radio>
              <el-radio label="wechat">微信</el-radio>
              <el-radio label="alipay">支付宝</el-radio>
              <el-radio label="unionpay">银联</el-radio>
              <el-radio label="insurance">医保</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    <div class="his-footer-bar">
      <el-button @click="onBack">取消</el-button>
      <el-button type="primary" :loading="submitting" :icon="Check" @click="onSubmit">确认收费</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Plus, Check } from '@element-plus/icons-vue'
import { getDrug } from '@/api/pharmacy'
import { createBill, payBill } from '@/api/payment'
import { getPatients } from '@/api/patient'
import { useTableHeight } from '@/composables/useTableHeight'

defineOptions({ name: 'RetailCharge' })

const route = useRoute()
const router = useRouter()
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const loading = ref(false)
const submitting = ref(false)
const pLoading = ref(false)

const patientId = ref('')
const patientName = ref('')
const patientOptions = ref([])
const items = ref([])
const totalAmount = ref(0)
const payForm = reactive({ payment_method: 'cash' })

const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function searchPatients(keyword) {
  if (!keyword) { patientOptions.value = []; return }
  pLoading.value = true
  try { const res = await getPatients({ keyword, page: 1, page_size: 20 }); patientOptions.value = res.items || [] } catch (e) { /* ignore */ }
  finally { pLoading.value = false }
}
const onPatientChange = (id) => { const p = patientOptions.value.find(x => x.id === id); if (p) patientName.value = p.name }
const onAddPatient = () => router.push('/patients/create')

async function addDrug(drugId) {
  if (items.value.find(x => x.drug_id === drugId)) { ElMessage.warning('该药品已添加'); return }
  const d = await getDrug(drugId)
  items.value.push({ drug_id: d.id, name: d.name, specification: d.specification, unit: d.unit, price: d.price, qty: 1 })
  recount()
  refresh()
}
const onPick = () => router.push('/retail/select')

function recount() {
  totalAmount.value = items.value.reduce((s, x) => s + Number(x.price || 0) * Number(x.qty || 0), 0)
}

const onSubmit = async () => {
  if (!items.value.length) { ElMessage.warning('请先添加药品'); return }
  if (!patientId.value && !patientName.value) { ElMessage.warning('请选择或填写患者'); return }
  submitting.value = true
  try {
    const billItems = items.value.map(x => ({ name: x.name, price: x.price, qty: x.qty, unit: x.unit, amount: Number(x.price) * x.qty }))
    const bill = await createBill({
      patient_id: patientId.value || '00000000-0000-0000-0000-000000000000',
      patient_name: patientName.value || (patientOptions.value.find(p => p.id === patientId.value)?.name) || '散客',
      bill_type: 'pharmacy',
      total_amount: Number(totalAmount.value.toFixed(2)),
      items: billItems
    })
    const bid = bill.id || (bill.data && bill.data.id)
    await payBill(bid, { payment_method: payForm.payment_method, amount: Number(totalAmount.value.toFixed(2)) })
    ElMessage.success('零售收费成功')
    router.push('/retail/select')
  } catch (e) {
    ElMessage.error(e?.message || '收费失败')
  } finally {
    submitting.value = false
  }
}

const onBack = () => router.back()

onMounted(async () => {
  const drugId = route.query.drugId
  if (drugId) {
    loading.value = true
    try { await addDrug(drugId) } catch (e) { ElMessage.error('加载药品失败') } finally { loading.value = false }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
/* 固定高度布局：页面不滚动，底部操作栏固定，明细表内部滚动 */
.retail-charge-page {
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  padding: 16px 16px 76px;
  overflow: hidden;
}
.page-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  :deep(.el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
    padding: 16px 20px;
  }
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-shrink: 0;
  margin-bottom: 12px;
  .card-title { font-size: 15px; font-weight: 600; color: #303133; }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.table-wrap { flex: 1; min-height: 0; overflow: hidden; }
.retail-patient-form { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; flex-shrink: 0; }
.retail-add { margin-top: 12px; flex-shrink: 0; }
.retail-summary { margin-top: 16px; text-align: right; font-size: 15px; color: #606266; flex-shrink: 0; .retail-total { color: #f56c6c; font-size: 20px; } }
</style>

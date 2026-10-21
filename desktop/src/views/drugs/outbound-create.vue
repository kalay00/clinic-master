<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">新增出库</div>
        <div class="his-page-subtitle">采购退货出库（选择已入库的采购单）</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="采购单" prop="purchase_order_id">
          <el-select
            v-model="form.purchase_order_id"
            filterable
            placeholder="请选择已入库的采购单"
            style="width: 460px"
            @change="onOrderChange"
          >
            <el-option
              v-for="o in orders"
              :key="o.id"
              :label="`${o.order_no}（${o.supplier_name || '未知供应商'} ¥${fmt(o.total_amount)}）`"
              :value="o.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" style="width: 460px" />
        </el-form-item>
      </el-form>

      <div class="his-section-title">退货明细（来自采购单，按可退数量填写）</div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column label="药品名称" min-width="200">
          <template #default="{ row }">{{ row.drug_name || row.drug_id }}</template>
        </el-table-column>
        <el-table-column label="单价（元）" width="120">
          <template #default="{ row }">{{ fmt(row.unit_price) }}</template>
        </el-table-column>
        <el-table-column label="可退数量" width="100">
          <template #default="{ row }">{{ row.max_quantity }}</template>
        </el-table-column>
        <el-table-column label="退货数量" width="140">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="0" :max="row.max_quantity" size="small" @change="recount" />
          </template>
        </el-table-column>
        <el-table-column label="金额（元）" width="110">
          <template #default="{ row }">{{ fmt(row.quantity * row.unit_price) }}</template>
        </el-table-column>
      </el-table>
      <div class="retail-summary"><span>合计金额：<b class="retail-total">{{ fmt(totalAmount) }}</b> 元</span></div>
    </div>
    <div class="his-footer-bar">
      <el-button @click="onBack">取消</el-button>
      <el-button type="primary" :loading="submitting" :icon="Check" @click="onSubmit">保存</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Check } from '@element-plus/icons-vue'
import { getPurchaseOrders, getPurchaseOrder, createReturnOrder } from '@/api/inventory'

defineOptions({ name: 'OutboundCreate' })

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const orders = ref([])
const items = ref([])
const totalAmount = ref(0)
const form = reactive({ purchase_order_id: '', remark: '' })
const rules = { purchase_order_id: [{ required: true, message: '请选择采购单', trigger: 'change' }] }
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

// 已入库的采购单才能退货（后端要求 po.status == received）
async function loadOrders() {
  loading.value = true
  try {
    const res = await getPurchaseOrders({ status: 'received', page_size: 100 })
    orders.value = res.items || []
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

// 选中采购单：带出明细与可退数量（已入库数量 - 已退数量）
async function onOrderChange(id) {
  if (!id) { items.value = []; recount(); return }
  loading.value = true
  try {
    const po = await getPurchaseOrder(id)
    const list = Array.isArray(po.items) ? po.items : []
    items.value = list.map(it => ({
      purchase_order_item_id: it.id,
      drug_name: it.drug_name || (it.drug && it.drug.name) || it.drug_id,
      unit_price: Number(it.unit_price || 0),
      max_quantity: Math.max(0, Number(it.received_quantity || 0) - Number(it.returned_quantity || 0)),
      quantity: 0,
    }))
    recount()
  } catch (e) {
    ElMessage.error('采购单明细加载失败')
    items.value = []
  } finally {
    loading.value = false
  }
}

function recount() {
  totalAmount.value = items.value.reduce((s, x) => s + (Number(x.quantity) || 0) * (Number(x.unit_price) || 0), 0)
}

const onSubmit = async () => {
  if (!form.purchase_order_id) { ElMessage.warning('请选择采购单'); return }
  const validItems = items.value.filter(x => x.quantity > 0)
  if (!validItems.length) { ElMessage.warning('请填写退货数量'); return }
  if (validItems.some(x => x.quantity > x.max_quantity)) { ElMessage.warning('退货数量超过可退数量'); return }
  submitting.value = true
  try {
    const stamp = Date.now().toString()
    const rand = Math.floor(Math.random() * 100).toString().padStart(2, '0')
    await createReturnOrder({
      purchase_order_id: form.purchase_order_id,
      // 后端不生成退货单号/日期，模型均非空，需前端补齐
      return_no: `RET${stamp.slice(-8)}${rand}`,
      return_date: new Date().toISOString().slice(0, 10),
      remark: form.remark,
      items: validItems.map(x => ({
        purchase_order_item_id: x.purchase_order_item_id,
        quantity: Number(x.quantity),
        unit_price: Number(x.unit_price || 0),
      })),
    })
    ElMessage.success('保存成功')
    router.push('/drugs/outbound')
  } catch (e) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}
const onBack = () => router.back()
onMounted(loadOrders)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.retail-add { margin-top: 12px; }
.retail-summary { margin-top: 16px; text-align: right; font-size: 15px; color: #606266; .retail-total { color: #f56c6c; font-size: 20px; } }
</style>

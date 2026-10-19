<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">新增出库</div>
        <div class="his-page-subtitle">采购退货 / 其他出库</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="出库类型" prop="order_type">
          <el-radio-group v-model="form.order_type">
            <el-radio label="purchase_return">采购退货</el-radio>
            <el-radio label="other">其他出库</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="form.supplier_id" filterable clearable placeholder="可选" style="width: 320px">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" style="width: 460px" />
        </el-form-item>
      </el-form>

      <div class="his-section-title">药品明细</div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column label="药品名称" min-width="200">
          <template #default="{ row }">
            <el-select v-model="row.drug_id" filterable remote placeholder="搜索药品" :remote-method="searchDrugs" :loading="dLoading" style="width:100%" @change="onDrugChange(row)">
              <el-option v-for="d in drugOptions" :key="d.id" :label="`${d.name}（${d.drug_code}）`" :value="d.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="120"><template #default="{ row }"><el-input-number v-model="row.quantity" :min="1" size="small" @change="recount" /></template></el-table-column>
        <el-table-column label="单价（元）" width="140"><template #default="{ row }"><el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" @change="recount" /></template></el-table-column>
        <el-table-column label="金额（元）" width="110"><template #default="{ row }">{{ fmt(row.quantity * row.unit_price) }}</template></el-table-column>
        <el-table-column label="操作" width="80"><template #default="{ row, $index }"><el-button type="danger" link @click="items.splice($index, 1); recount()">移除</el-button></template></el-table-column>
      </el-table>
      <div class="retail-add"><el-button type="primary" plain :icon="Plus" @click="onAddRow">添加药品</el-button></div>
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
import { Back, Plus, Check } from '@element-plus/icons-vue'
import { createReturnOrder, getSuppliers } from '@/api/inventory'
import { getDrugs } from '@/api/pharmacy'

defineOptions({ name: 'OutboundCreate' })

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const dLoading = ref(false)
const suppliers = ref([])
const drugOptions = ref([])
const items = ref([])
const totalAmount = ref(0)
const form = reactive({ order_type: 'purchase_return', supplier_id: '', remark: '' })
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function loadSuppliers() { try { const res = await getSuppliers({ page_size: 100 }); suppliers.value = res.items || [] } catch (e) { /* ignore */ } }
async function searchDrugs(keyword) {
  if (!keyword) { drugOptions.value = []; return }
  dLoading.value = true
  try { const res = await getDrugs({ page: 1, page_size: 20, search: keyword }); drugOptions.value = res.items || [] } catch (e) { /* ignore */ }
  finally { dLoading.value = false }
}
const onDrugChange = (row) => { const d = drugOptions.value.find(x => x.id === row.drug_id); if (d) row.unit_price = d.price || 0; recount() }
const onAddRow = () => items.value.push({ drug_id: '', quantity: 1, unit_price: 0 })
function recount() { totalAmount.value = items.value.reduce((s, x) => s + (Number(x.quantity) || 0) * (Number(x.unit_price) || 0), 0) }

const onSubmit = async () => {
  if (!items.value.length) { ElMessage.warning('请添加药品'); return }
  if (items.value.some(x => !x.drug_id)) { ElMessage.warning('请选择药品'); return }
  submitting.value = true
  try {
    await createReturnOrder({ order_type: form.order_type, supplier_id: form.supplier_id || undefined, remark: form.remark, items: items.value.map(x => ({ drug_id: x.drug_id, quantity: x.quantity, unit_price: x.unit_price })) })
    ElMessage.success('保存成功')
    router.push('/drugs/outbound')
  } catch (e) { ElMessage.error(e?.message || '保存失败') }
  finally { submitting.value = false }
}
const onBack = () => router.back()
onMounted(loadSuppliers)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.retail-add { margin-top: 12px; }
.retail-summary { margin-top: 16px; text-align: right; font-size: 15px; color: #606266; .retail-total { color: #f56c6c; font-size: 20px; } }
</style>

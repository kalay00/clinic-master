<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">新增调价</div>
        <div class="his-page-subtitle">调整药品零售价</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <el-form label-width="100px">
        <el-form-item label="调价日期">
          <el-date-picker v-model="adjustDate" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 220px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="remark" type="textarea" :rows="2" style="width: 460px" />
        </el-form-item>
      </el-form>

      <div class="his-section-title">调价明细</div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column label="药品名称" min-width="200">
          <template #default="{ row }">
            <el-select v-model="row.drug_id" filterable remote placeholder="搜索药品" :remote-method="searchDrugs" :loading="dLoading" style="width:100%" @change="onDrugChange(row)">
              <el-option v-for="d in drugOptions" :key="d.id" :label="`${d.name}（${d.drug_code}）`" :value="d.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="原价（元）" width="120">
          <template #default="{ row }">{{ fmt(row.old_price) }}</template>
        </el-table-column>
        <el-table-column label="新价（元）" width="140">
          <template #default="{ row }"><el-input-number v-model="row.new_price" :min="0" :precision="2" size="small" /></template>
        </el-table-column>
        <el-table-column label="调价原因" min-width="140">
          <template #default="{ row }"><el-input v-model="row.reason" /></template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row, $index }"><el-button type="danger" link @click="items.splice($index, 1)">移除</el-button></template>
        </el-table-column>
      </el-table>
      <div class="retail-add"><el-button type="primary" plain :icon="Plus" @click="onAddRow">添加药品</el-button></div>
    </div>
    <div class="his-footer-bar">
      <el-button @click="onBack">取消</el-button>
      <el-button type="primary" :loading="submitting" :icon="Check" @click="onSubmit">保存调价</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Plus, Check } from '@element-plus/icons-vue'
import { createPriceAdjustment, getDrug } from '@/api/pharmacy'
import { getDrugs } from '@/api/pharmacy'

defineOptions({ name: 'PriceCreate' })

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const dLoading = ref(false)
const drugOptions = ref([])
const items = ref([])
const adjustDate = ref(new Date().toISOString().slice(0, 10))
const remark = ref('')
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function searchDrugs(keyword) {
  if (!keyword) { drugOptions.value = []; return }
  dLoading.value = true
  try { const res = await getDrugs({ page: 1, page_size: 20, search: keyword }); drugOptions.value = res.items || [] } catch (e) { /* ignore */ }
  finally { dLoading.value = false }
}
const onDrugChange = async (row) => { if (row.drug_id) { const d = await getDrug(row.drug_id); row.old_price = d.price || 0; row.new_price = d.price || 0 } }
const onAddRow = () => items.value.push({ drug_id: '', old_price: 0, new_price: 0, reason: '' })

const onSubmit = async () => {
  if (!items.value.length) { ElMessage.warning('请添加药品'); return }
  if (items.value.some(x => !x.drug_id)) { ElMessage.warning('请选择药品'); return }
  submitting.value = true
  try {
    await createPriceAdjustment({ adjust_date: adjustDate.value, remark: remark.value, items: items.value.map(x => ({ drug_id: x.drug_id, new_price: x.new_price, reason: x.reason })) })
    ElMessage.success('调价单已保存，待审批生效')
    router.push('/drugs/price')
  } catch (e) { ElMessage.error(e?.message || '保存失败') }
  finally { submitting.value = false }
}
const onBack = () => router.back()

onMounted(async () => {
  const drugId = route.query.drugId
  if (drugId) {
    const d = await getDrug(drugId)
    items.value.push({ drug_id: d.id, old_price: d.price || 0, new_price: d.price || 0, reason: '' })
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.retail-add { margin-top: 12px; }
</style>

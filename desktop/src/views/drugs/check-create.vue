<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">新增盘点</div>
        <div class="his-page-subtitle">库存盘点开单</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <div class="his-filter-bar">
        <el-button type="primary" plain :icon="Refresh" @click="onLoadStock">从库存加载</el-button>
      </div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column label="药品名称" min-width="200">
          <template #default="{ row }">
            <el-select v-model="row.drug_id" filterable remote placeholder="搜索药品" :remote-method="searchDrugs" :loading="dLoading" style="width:100%" @change="onDrugChange(row)">
              <el-option v-for="d in drugOptions" :key="d.id" :label="`${d.name}（${d.drug_code}）`" :value="d.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="账面数量" width="120">
          <template #default="{ row }">{{ row.book_quantity }}</template>
        </el-table-column>
        <el-table-column label="实盘数量" width="140">
          <template #default="{ row }"><el-input-number v-model="row.actual_quantity" :min="0" size="small" /></template>
        </el-table-column>
        <el-table-column label="差异" width="100">
          <template #default="{ row }">{{ row.actual_quantity - (row.book_quantity || 0) }}</template>
        </el-table-column>
        <el-table-column label="备注" min-width="140">
          <template #default="{ row }"><el-input v-model="row.reason" placeholder="差异原因" /></template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row, $index }"><el-button type="danger" link @click="items.splice($index, 1)">移除</el-button></template>
        </el-table-column>
      </el-table>
      <div class="retail-add"><el-button type="primary" plain :icon="Plus" @click="onAddRow">添加药品</el-button></div>
    </div>
    <div class="his-footer-bar">
      <el-button @click="onBack">取消</el-button>
      <el-button type="primary" :loading="submitting" :icon="Check" @click="onSubmit">保存盘点</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Refresh, Plus, Check } from '@element-plus/icons-vue'
import { createInventoryCheck } from '@/api/inventory'
import { getInventory, getDrugs } from '@/api/pharmacy'
import { fetchAllPages } from '@/utils/paging'

defineOptions({ name: 'CheckCreate' })

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const dLoading = ref(false)
const drugOptions = ref([])
const items = ref([])

async function searchDrugs(keyword) {
  if (!keyword) { drugOptions.value = []; return }
  dLoading.value = true
  try { const res = await getDrugs({ page: 1, page_size: 20, search: keyword }); drugOptions.value = res.items || [] } catch (e) { /* ignore */ }
  finally { dLoading.value = false }
}
const onDrugChange = (row) => { const d = drugOptions.value.find(x => x.id === row.drug_id); if (d) row.book_quantity = d.quantity || 0 }
const onAddRow = () => items.value.push({ drug_id: '', book_quantity: 0, actual_quantity: 0, reason: '' })

async function onLoadStock() {
  loading.value = true
  try {
    // 库存接口分页参数为 page_no，统一转换为公共分页工具的 page
    const list = await fetchAllPages(p => getInventory({ page_no: p.page, page_size: p.page_size }))
    items.value = list.map(x => ({ drug_id: x.drug_id, book_quantity: x.quantity || 0, actual_quantity: x.quantity || 0, reason: '' }))
    ElMessage.success(`已加载 ${items.value.length} 条库存`)
  } catch (e) { ElMessage.error('加载库存失败') }
  finally { loading.value = false }
}

const onSubmit = async () => {
  if (!items.value.length) { ElMessage.warning('请添加盘点药品'); return }
  if (items.value.some(x => !x.drug_id)) { ElMessage.warning('请选择药品'); return }
  submitting.value = true
  try {
    await createInventoryCheck({ items: items.value.map(x => ({ drug_id: x.drug_id, book_quantity: x.book_quantity, actual_quantity: x.actual_quantity, reason: x.reason })) })
    ElMessage.success('盘点单已保存')
    router.push('/drugs/check')
  } catch (e) { ElMessage.error(e?.message || '保存失败') }
  finally { submitting.value = false }
}
const onBack = () => router.back()
onMounted(onLoadStock)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.his-filter-bar { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.retail-add { margin-top: 12px; }
</style>

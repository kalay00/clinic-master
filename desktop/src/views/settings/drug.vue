<template>
  <div class="settings-drug-page">
    <el-card class="page-card" shadow="never">
    <div class="filter-bar">
      <el-input v-model="query.keyword" placeholder="药品名称 / 编码" clearable style="width: 220px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-select v-model="query.category_id" placeholder="药品分类" clearable style="width: 180px" @change="onSearch">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px" @change="onSearch">
        <el-option label="启用" value="active" />
        <el-option label="停用" value="inactive" />
      </el-select>
      <el-button type="primary" @click="onSearch">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增药品</el-button>
    </div>

    <div class="table-wrap" ref="wrapRef">
      <el-table ref="tableRef" :height="tableHeight" :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="drug_code" label="药品编码" width="130" />
      <el-table-column prop="name" label="药品名称" min-width="160" show-overflow-tooltip />
      <el-table-column prop="generic_name" label="通用名" min-width="140" show-overflow-tooltip />
      <el-table-column prop="specification" label="规格" width="120" show-overflow-tooltip />
      <el-table-column prop="unit" label="单位" width="80" align="center" />
      <el-table-column label="分类" width="130">
        <template #default="{ row }">{{ categoryName(row) }}</template>
      </el-table-column>
      <el-table-column prop="manufacturer" label="生产厂家" min-width="140" show-overflow-tooltip />
      <el-table-column label="单价" width="110" align="right">
        <template #default="{ row }">{{ formatMoney(row.price) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
      </div>

    <div class="pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchList"
        @current-change="fetchList"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑药品' : '新增药品'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="药品编码" required>
              <el-input v-model="form.drug_code" placeholder="唯一编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="药品名称" required>
              <el-input v-model="form.name" placeholder="如：阿莫西林胶囊" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="通用名">
              <el-input v-model="form.generic_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规格">
              <el-input v-model="form.specification" placeholder="如：0.25g*24粒" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="form.unit" placeholder="盒 / 瓶 / 支" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="药品分类">
              <el-select v-model="form.category_id" clearable placeholder="请选择" style="width: 100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生产厂家">
              <el-input v-model="form.manufacturer" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-select v-model="form.supplier_id" clearable placeholder="请选择" style="width: 100%">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价">
              <el-input-number v-model="form.price" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.status">
                <el-radio value="active">启用</el-radio>
                <el-radio value="inactive">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDrugs, createDrug, updateDrug, deleteDrug, getDrugCategories } from '@/api/pharmacy'
import { getSuppliers } from '@/api/inventory'
import { fetchAllPages } from '@/utils/paging'

import { useTableHeight } from '@/composables/useTableHeight'
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const categories = ref([])
const suppliers = ref([])
const query = reactive({ page: 1, pageSize: 10, keyword: '', category_id: '', status: '' })

function formatMoney(v) {
  return `¥${Number(v || 0).toFixed(2)}`
}

function categoryName(row) {
  if (row.category_name) return row.category_name
  const hit = categories.value.find(c => c.id === row.category_id)
  return hit ? hit.name : row.category || '-'
}

async function fetchList() {
  loading.value = true
  try {
    const data = await getDrugs({
      page: query.page,
      page_size: query.pageSize,
      keyword: query.keyword || undefined,
      category: query.category_id || undefined,
      status: query.status || undefined,
    })
    tableData.value = data.items || []
    total.value = data.total || 0
  } finally { loading.value = false; refresh() }
}

async function fetchOptions() {
  try {
    categories.value = await fetchAllPages(p => getDrugCategories(p))
  } catch {
    categories.value = []
  }
  try {
    suppliers.value = await fetchAllPages(p => getSuppliers(p))
  } catch {
    suppliers.value = []
  }
}

function onSearch() {
  query.page = 1
  fetchList()
}

function onReset() {
  query.keyword = ''
  query.category_id = ''
  query.status = ''
  query.page = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const emptyForm = () => ({
  id: null,
  drug_code: '',
  name: '',
  generic_name: '',
  specification: '',
  unit: '',
  category_id: '',
  manufacturer: '',
  supplier_id: '',
  price: 0,
  status: 'active',
})
const form = reactive(emptyForm())

function openDialog(row) {
  if (row) {
    Object.assign(form, {
      id: row.id,
      drug_code: row.drug_code || '',
      name: row.name || '',
      generic_name: row.generic_name || '',
      specification: row.specification || '',
      unit: row.unit || '',
      category_id: row.category_id || '',
      manufacturer: row.manufacturer || '',
      supplier_id: row.supplier_id || '',
      price: Number(row.price || 0),
      status: row.status || 'active',
    })
  } else {
    Object.assign(form, emptyForm())
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.drug_code || !form.name) {
    ElMessage.warning('请输入药品编码和名称')
    return
  }
  submitting.value = true
  const payload = {
    drug_code: form.drug_code,
    name: form.name,
    generic_name: form.generic_name || undefined,
    specification: form.specification || undefined,
    unit: form.unit || undefined,
    category_id: form.category_id || undefined,
    manufacturer: form.manufacturer || undefined,
    supplier_id: form.supplier_id || undefined,
    price: form.price,
    status: form.status,
  }
  try {
    if (form.id) {
      await updateDrug(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createDrug(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除药品「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  await deleteDrug(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(() => {
  fetchOptions()
  fetchList()
})
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，筛选/分页固定，仅列表内部滚动 */
.settings-drug-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; display: flex; flex-direction: column; }
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
  .head-actions { display: flex; gap: 10px; flex-wrap: wrap; }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.table-wrap { flex: 1; min-height: 0; overflow: hidden; }
.filter-form, .filter-bar { flex-shrink: 0; margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.list-pagination, .pagination { flex-shrink: 0; justify-content: flex-end; margin-top: 12px; }
</style>

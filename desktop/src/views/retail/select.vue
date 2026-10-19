<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">药品选择</div>
        <div class="his-page-subtitle">选择零售药品</div>
      </div>
    </div>
    <div class="his-card">
      <div class="his-filter-bar">
        <el-input v-model="query.search" placeholder="药品编码/名称/通用名" style="width: 240px" @keyup.enter="onSearch" />
        <el-select v-model="query.category" placeholder="全部分类" clearable style="width: 160px" @change="onSearch">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
        <el-button :icon="Refresh" @click="onReset">重置</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="drug_code" label="药品编码" width="120" />
        <el-table-column prop="name" label="药品名称" min-width="140" />
        <el-table-column prop="generic_name" label="通用名" min-width="120" />
        <el-table-column prop="specification" label="规格" width="120" />
        <el-table-column prop="manufacturer" label="生产厂家" min-width="140" />
        <el-table-column prop="price" label="零售价（元）" width="100">
          <template #default="{ row }">{{ fmt(row.price) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">{{ row.status === 'active' ? '在用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Plus" @click="onSelect(row)">选药</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination class="his-pagination" v-model:current-page="query.page" v-model:page-size="query.pageSize" layout="total, prev, pager, next, jumper" :total="total" @current-change="fetchList" @size-change="onSizeChange" />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getDrugs, getDrugCategories } from '@/api/pharmacy'

defineOptions({ name: 'RetailSelect' })

const router = useRouter()
const loading = ref(false)
const total = ref(0)
const categories = ref([])
const query = reactive({ page: 1, pageSize: 10, search: '', category: '' })
const tableData = ref([])
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function fetchCategories() {
  try { const res = await getDrugCategories({ page_size: 100 }); categories.value = res.items || [] } catch (e) { /* ignore */ }
}
async function fetchList() {
  loading.value = true
  try {
    const res = await getDrugs({ page: query.page, page_size: query.pageSize, search: query.search || undefined, category: query.category || undefined })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) { ElMessage.error('加载药品失败') }
  finally { loading.value = false }
}
const onSearch = () => { query.page = 1; fetchList() }
const onReset = () => { query.search = ''; query.category = ''; query.page = 1; fetchList() }
const onSizeChange = () => { query.page = 1; fetchList() }
const onSelect = (row) => router.push(`/retail/charge?drugId=${row.id}`)

onMounted(() => { fetchCategories(); fetchList() })
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.his-filter-bar { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
</style>

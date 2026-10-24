<template>
  <div class="drugs-page">
    <el-card class="page-card" shadow="never">
      <div class="card-header">
        <span class="card-title">药品信息维护</span>
        <div class="head-actions">
          <el-button type="primary" :icon="Plus" @click="goCreate">新增药品</el-button>
          <el-button type="primary" plain :icon="FullScreen" @click="scanCreate">扫码录入</el-button>
          <el-button :icon="Upload" @click="onImport">导入</el-button>
          <el-button :icon="Download" @click="onExport">导出</el-button>
        </div>
      </div>

      <div class="page-body">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="药品分类">
          <el-select v-model="query.category_id" placeholder="全部" clearable style="width: 130px">
            <el-option label="全部" value="" />
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="药品状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 130px">
            <el-option label="全部" value="" />
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="query.dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="输入药品名称/编码/生产厂家" style="width: 240px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <div class="table-wrap" ref="wrapRef">
        <el-table :data="tableData" border stripe v-loading="loading" ref="tableRef" :height="tableHeight">
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="drug_code" label="编码" min-width="100" />
        <el-table-column prop="name" label="药品名称" min-width="180" />
        <el-table-column prop="specification" label="规格" min-width="120" />
        <el-table-column label="收费类别" width="110">
          <template #default="{ row }">{{ categoryName(row) }}</template>
        </el-table-column>
        <el-table-column label="采购价" width="90"><template #default>-</template></el-table-column>
        <el-table-column label="售药价" width="90">
          <template #default="{ row }">{{ row.price != null ? `¥${Number(row.price).toFixed(2)}` : '-' }}</template>
        </el-table-column>
        <el-table-column prop="manufacturer" label="生产厂家" min-width="180" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Edit" @click="onEdit(row)">编辑</el-button>
            <el-button type="primary" link :icon="CopyDocument" @click="onCopy(row)">复制</el-button>
            <el-button type="danger" link :icon="CircleClose" @click="onToggleStatus(row)">停用</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      </div>

      <el-pagination
        class="list-pagination"
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        layout="total, prev, pager, next, jumper"
        :total="total"
        @current-change="onSearch"
        @size-change="onSearch"
      />
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, FullScreen, Upload, Download, Search, Edit, CopyDocument, CircleClose
} from '@element-plus/icons-vue'
import { getDrugs, updateDrug, getDrugCategories } from '@/api/pharmacy'
import { fetchAllPages } from '@/utils/paging'
import { useTableHeight } from '@/composables/useTableHeight'

defineOptions({ name: 'DrugMaintain' })

const router = useRouter()
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const loading = ref(false)
const total = ref(0)
const categories = ref([])
const tableData = ref([])

const query = reactive({
  page: 1, pageSize: 10,
  category_id: '', status: '', keyword: ''
})

function categoryName(row) {
  if (row.category_name) return row.category_name
  const hit = categories.value.find(c => c.id === row.category_id)
  return hit ? hit.name : row.category || '-'
}

async function onSearch() {
  loading.value = true
  try {
    const data = await getDrugs({
      page: query.page,
      page_size: query.pageSize,
      keyword: query.keyword || undefined,
      category: query.category_id || undefined,
      status: query.status || undefined
    })
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载药品列表失败')
  } finally {
    loading.value = false
    refresh()
  }
}
const onImport = () => ElMessage.info('导入功能开发中')
const onExport = () => ElMessage.info('导出功能开发中')
const goCreate = () => router.push('/drugs/create-western')
const scanCreate = () => ElMessage.info('扫码录入开发中')
const onEdit = (row) => router.push(`/drugs/create-western?id=${row.id}`)
const onCopy = (row) => ElMessage.info('复制功能开发中')
const onToggleStatus = async (row) => {
  const next = row.status === 'active' ? 'inactive' : 'active'
  const action = next === 'inactive' ? '停用' : '启用'
  try {
    await ElMessageBox.confirm(`确定${action}药品 ${row.name} 吗？`, '提示', { type: 'warning' })
    await updateDrug(row.id, { status: next })
    ElMessage.success(`${action}成功`)
    onSearch()
  } catch (e) { /* cancel */ }
}

async function loadCategories() {
  try {
    categories.value = await fetchAllPages(p => getDrugCategories(p))
  } catch (e) { /* 分类非强依赖 */ }
}

onMounted(() => {
  loadCategories()
  onSearch()
})
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，筛选/分页固定，仅列表内部滚动 */
.drugs-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
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
  .head-actions {
    display: flex;
    gap: 10px;
  }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.table-wrap { flex: 1; min-height: 0; overflow: hidden; }
.filter-form {
  flex-shrink: 0;
  margin-bottom: 12px;
  :deep(.el-form-item) {
    margin-bottom: 10px;
  }
}
.list-pagination {
  flex-shrink: 0;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>

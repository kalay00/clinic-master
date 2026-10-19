<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">库存盘点</div>
      <el-button type="primary" :icon="Plus" @click="goCreate">新增盘点</el-button>
    </div>

    <el-card class="page-card" shadow="never">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="盘点状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 130px" @change="onSearch">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="已盘点" value="counted" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="输入盘点单号" style="width: 200px" @keyup.enter="onSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          <el-button :icon="Refresh" @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="check_no" label="盘点单号" min-width="160" />
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
        <el-table-column prop="status" label="盘点状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="onDetail(row)">查看</el-button>
            <el-button v-if="row.status !== 'completed'" type="success" link :icon="Check" @click="onComplete(row)">完成</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination class="list-pagination" v-model:current-page="query.page" v-model:page-size="query.pageSize" layout="total, prev, pager, next, jumper" :total="total" @current-change="fetchList" @size-change="onSizeChange" />
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Check } from '@element-plus/icons-vue'
import { getInventoryChecks, completeInventoryCheck, deleteInventoryCheck } from '@/api/inventory'

defineOptions({ name: 'DrugCheck' })

const router = useRouter()
const loading = ref(false)
const total = ref(0)
const query = reactive({ page: 1, pageSize: 10, status: '', keyword: '' })
const tableData = ref([])
const statusMap = { draft: '草稿', counted: '已盘点', completed: '已完成' }
const statusType = (s) => ({ draft: 'info', counted: 'warning', completed: 'success' }[s] || 'info')

async function fetchList() {
  loading.value = true
  try {
    const res = await getInventoryChecks({ page: query.page, page_size: query.pageSize, status: query.status || undefined, keyword: query.keyword || undefined })
    tableData.value = res.items || []
    total.value = res.pagination?.total || 0
  } catch (e) { ElMessage.error('加载盘点单失败') }
  finally { loading.value = false }
}
const onSearch = () => { query.page = 1; fetchList() }
const onReset = () => { query.status = ''; query.keyword = ''; query.page = 1; fetchList() }
const onSizeChange = () => { query.page = 1; fetchList() }
const goCreate = () => router.push('/drugs/check/create')
const onDetail = (row) => router.push(`/drugs/check/detail/${row.id}`)
const onComplete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定完成盘点单 ${row.check_no}？`, '提示', { type: 'warning' })
    await completeInventoryCheck(row.id)
    ElMessage.success('盘点完成')
    fetchList()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}
onMounted(fetchList)
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.page-title { font-size: 16px; font-weight: 600; color: #303133; }
.filter-form { margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.list-pagination { justify-content: flex-end; margin-top: 12px; }
</style>

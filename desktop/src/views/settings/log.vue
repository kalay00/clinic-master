<template>
  <div class="page-card">
    <div class="page-title">操作日志</div>
    <div class="filter-bar">
      <el-select v-model="query.operation_type" placeholder="操作类型" clearable style="width: 150px" @change="fetchList">
        <el-option label="创建" value="create" />
        <el-option label="更新" value="update" />
        <el-option label="删除" value="delete" />
        <el-option label="查询" value="query" />
      </el-select>
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="成功" value="success" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-input v-model="query.keyword" placeholder="描述关键字" clearable style="width: 200px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="operation_type" label="操作类型" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="row.operation_type === 'delete' ? 'danger' : (row.operation_type === 'create' ? 'success' : 'info')">
            {{ { create: '创建', update: '更新', delete: '删除', query: '查询' }[row.operation_type] || row.operation_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="resource_type" label="资源类型" width="140" />
      <el-table-column prop="operation_desc" label="操作描述" min-width="220" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP" width="140" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
            {{ row.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" min-width="170" />
      <el-table-column label="操作" width="90" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLogs, deleteLog } from '@/api/log'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 20, operation_type: '', status: '', keyword: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getLogs({
      page: query.page,
      page_size: query.pageSize,
      operation_type: query.operation_type || undefined,
      status: query.status || undefined,
      keyword: query.keyword || undefined,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function onReset() {
  query.operation_type = ''
  query.status = ''
  query.keyword = ''
  query.page = 1
  fetchList()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确认删除该日志？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteLog(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    // ignore
  }
}

onMounted(fetchList)
</script>

<style scoped lang="scss">
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

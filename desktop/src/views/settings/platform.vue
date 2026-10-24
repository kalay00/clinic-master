<template>
  <div class="settings-platform-page">
    <el-card class="page-card" shadow="never">
      <div class="page-body">
      <el-row :gutter="16" class="stat-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-label">租户总数</div>
          <div class="stat-value">{{ stats.tenant_count ?? '-' }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-label">用户总数</div>
          <div class="stat-value">{{ stats.user_count ?? '-' }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-label">活跃租户</div>
          <div class="stat-value">{{ stats.active_tenant_count ?? '-' }}</div>
        </el-card>
      </el-col>
    </el-row>

      <div class="card-header">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="租户列表" name="tenants" />
          <el-tab-pane label="审计日志" name="logs" />
        </el-tabs>
      </div>

    <template v-if="activeTab === 'tenants'">
      <div class="table-wrap" ref="wrapRef">
        <el-table :data="tenants" border stripe v-loading="loadingTenants" ref="tableRef" :height="tableHeight">
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="tenant_code" label="租户编码" width="140" />
        <el-table-column prop="name" label="诊所名称" min-width="160" />
        <el-table-column prop="admin_phone" label="管理员手机号" width="160" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="过期时间" width="160">
          <template #default="{ row }">{{ row.expire_at || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="toggleTenant(row)">{{ row.is_active ? '停用' : '启用' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      <div class="pagination">
        <el-pagination
          v-model:current-page="tenantQuery.page"
          v-model:page-size="tenantQuery.pageSize"
          :total="tenantTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchTenants"
          @current-change="fetchTenants"
        />
      </div>
    </template>

    <template v-else>
      <div class="table-wrap" ref="wrapRef">
        <el-table :data="logs" border stripe v-loading="loadingLogs" ref="tableRef" :height="tableHeight">
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="tenant_name" label="租户" width="160" />
        <el-table-column prop="action" label="操作" min-width="140" />
        <el-table-column prop="operator" label="操作人" width="140" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ row.created_at || '-' }}</template>
        </el-table-column>
      </el-table>
      </div>
      <div class="pagination">
        <el-pagination
          v-model:current-page="logQuery.page"
          v-model:page-size="logQuery.pageSize"
          :total="logTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </template>
      </div>
  </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTenants, getStatistics, getAuditLogs, updateTenant } from '@/api/platform'

import { useTableHeight } from '@/composables/useTableHeight'
const activeTab = ref('tenants')
const stats = ref({})
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const loadingTenants = ref(false)
const loadingLogs = ref(false)

const tenants = ref([])
const tenantTotal = ref(0)
const tenantQuery = reactive({ page: 1, pageSize: 10 })

const logs = ref([])
const logTotal = ref(0)
const logQuery = reactive({ page: 1, pageSize: 10 })

async function fetchStats() {
  try {
    stats.value = await getStatistics()
  } catch (e) {
    // 拦截器处理
  }
}

async function fetchTenants() {
  loadingTenants.value = true
  try {
    const res = await getTenants({ page: tenantQuery.page, page_size: tenantQuery.pageSize })
    tenants.value = res.items || res.data || []
    tenantTotal.value = res.total || (Array.isArray(tenants.value) ? tenants.value.length : 0)
  } finally {
    loadingTenants.value = false
  }
}

async function fetchLogs() {
  loadingLogs.value = true
  try {
    const res = await getAuditLogs({ page: logQuery.page, page_size: logQuery.pageSize })
    logs.value = res.items || res.data || []
    logTotal.value = res.total || (Array.isArray(logs.value) ? logs.value.length : 0)
  } finally {
    loadingLogs.value = false
  }
}

async function toggleTenant(row) {
  try {
    await ElMessageBox.confirm(`确认${row.is_active ? '停用' : '启用'}租户「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await updateTenant(row.id, { is_active: !row.is_active })
    ElMessage.success('操作成功')
    fetchTenants()
  } catch (e) {
    // 拦截器处理
  }
}

onMounted(() => {
  fetchStats()
  fetchTenants()
  fetchLogs()
})
</script>

<style scoped lang="scss">
/* 固定高度布局：页面不滚动，仅列表内部滚动 */
.settings-platform-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
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
  :deep(.el-tabs__header) { margin-bottom: 0; }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.stat-row { margin-bottom: 8px; flex-shrink: 0; }
.stat-label { color: #888; font-size: 13px; }
.stat-value { font-size: 26px; font-weight: 600; margin-top: 6px; color: #5b7cff; }
.mt-16 { margin-top: 16px; }
.table-wrap { flex: 1; min-height: 0; overflow: hidden; }
.pagination { display: flex; justify-content: flex-end; margin-top: 16px; flex-shrink: 0; }
</style>

<template>
  <div class="settings-fee-page">
    <el-card class="page-card" shadow="never">
    <el-tabs v-model="activeType" @tab-change="onTabChange">
      <el-tab-pane label="挂号费" name="registration" />
      <el-tab-pane label="治疗费" name="treatment" />
      <el-tab-pane label="附加费" name="extra" />
      <el-tab-pane label="其它" name="other" />
    </el-tabs>

    <div class="filter-bar">
      <el-input v-model="query.name" placeholder="费用名称" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="启用" :value="true" />
        <el-option label="停用" :value="false" />
      </el-select>
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增费用</el-button>
    </div>

    <div class="table-wrap" ref="wrapRef">
      <el-table ref="tableRef" :height="tableHeight" :data="tableData" border stripe v-loading="loading">
      <el-table-column prop="name" label="费用名称" min-width="200" />
      <el-table-column label="金额" min-width="120" align="right">
        <template #default="{ row }">{{ row.amount != null ? `¥${Number(row.amount).toFixed(2)}` : '-' }}</template>
      </el-table-column>
      <el-table-column label="成本" min-width="120" align="right">
        <template #default="{ row }">{{ row.cost_price != null ? `¥${Number(row.cost_price).toFixed(2)}` : '-' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status ? 'success' : 'info'" size="small">{{ row.status ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑费用' : '新增费用'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="费用类型" required>
          <el-select v-model="form.fee_type" style="width: 100%">
            <el-option label="挂号费" value="registration" />
            <el-option label="治疗费" value="treatment" />
            <el-option label="附加费" value="extra" />
            <el-option label="其它" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="费用名称" required>
          <el-input v-model="form.name" placeholder="请输入费用名称" />
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="form.amount" :min="0" :precision="2" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="成本">
          <el-input-number v-model="form.cost_price" :min="0" :precision="2" :step="1" style="width: 100%" />
          <div class="tip">用于后续利润统计</div>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
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
import { getFees, createFee, updateFee, deleteFee } from '@/api/fee'

import { useTableHeight } from '@/composables/useTableHeight'
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const activeType = ref('registration')
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, name: '', status: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getFees({
      page: query.page,
      page_size: query.pageSize,
      fee_type: activeType.value,
      name: query.name || undefined,
      status: query.status === '' ? undefined : query.status,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false; refresh() }
}

function onTabChange() {
  query.page = 1
  fetchList()
}

function onReset() {
  query.name = ''
  query.status = ''
  query.page = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({
  id: null,
  fee_type: 'registration',
  name: '',
  amount: 0,
  cost_price: 0,
  status: true,
})

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.fee_type = row.fee_type || 'registration'
    form.name = row.name
    form.amount = Number(row.amount) || 0
    form.cost_price = Number(row.cost_price) || 0
    form.status = row.status !== false
  } else {
    Object.assign(form, { id: null, fee_type: activeType.value, name: '', amount: 0, cost_price: 0, status: true })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入费用名称')
    return
  }
  submitting.value = true
  const payload = {
    fee_type: form.fee_type,
    name: form.name,
    amount: form.amount,
    cost_price: form.cost_price || 0,
    status: form.status,
  }
  try {
    if (form.id) {
      await updateFee(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createFee(payload)
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
    await ElMessageBox.confirm(`确认删除费用「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteFee(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    // 拦截器处理
  }
}

onMounted(fetchList)
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，筛选/分页固定，仅列表内部滚动 */
.settings-fee-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; display: flex; flex-direction: column; }
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

/* 页面特有样式 */
.tip {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
  line-height: 1.4;
}
</style>

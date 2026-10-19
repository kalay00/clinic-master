<template>
  <div class="page-card">
    <div class="page-title">附加费设置</div>
    <div class="filter-bar">
      <el-input v-model="query.name" placeholder="费用名称" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="启用" :value="true" />
        <el-option label="停用" :value="false" />
      </el-select>
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增附加费</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="name" label="费用名称" min-width="160" />
      <el-table-column prop="code" label="编码" width="140" />
      <el-table-column label="金额" width="120" align="right">
        <template #default="{ row }">{{ row.amount != null ? `¥${Number(row.amount).toFixed(2)}` : '-' }}</template>
      </el-table-column>
      <el-table-column prop="unit" label="计费单位" width="120" />
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑附加费' : '新增附加费'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="费用名称" required>
          <el-input v-model="form.name" placeholder="请输入费用名称" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" placeholder="选填" />
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="form.amount" :min="0" :precision="2" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="计费单位">
          <el-input v-model="form.unit" placeholder="如：次 / 人 / 项" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :step="1" />
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFees, createFee, updateFee, deleteFee, FEE_TYPE } from '@/api/fee'

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
      fee_type: FEE_TYPE.EXTRA,
      name: query.name || undefined,
      status: query.status === '' ? undefined : query.status,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
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
  name: '',
  code: '',
  amount: 0,
  unit: '',
  sort: 0,
  status: true,
  remark: '',
})

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.name = row.name
    form.code = row.code || ''
    form.amount = Number(row.amount) || 0
    form.unit = row.unit || ''
    form.sort = row.sort || 0
    form.status = row.status !== false
    form.remark = row.remark || ''
  } else {
    Object.assign(form, { id: null, name: '', code: '', amount: 0, unit: '', sort: 0, status: true, remark: '' })
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
    fee_type: FEE_TYPE.EXTRA,
    name: form.name,
    code: form.code || undefined,
    amount: form.amount,
    unit: form.unit || undefined,
    sort: form.sort,
    status: form.status,
    remark: form.remark || undefined,
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

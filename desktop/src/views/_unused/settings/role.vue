<template>
  <div class="page-card">
    <div class="page-title">角色管理</div>
    <div class="filter-bar">
      <el-input v-model="query.keyword" placeholder="角色名称 / 编码" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增角色</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="name" label="角色名称" min-width="140" />
      <el-table-column prop="code" label="角色编码" width="160" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="系统角色" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_system ? 'warning' : 'info'" size="small">
            {{ row.is_system ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" :disabled="row.is_system" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑角色' : '新增角色'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="角色名称" required>
          <el-input v-model="form.name" placeholder="角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" required>
          <el-input v-model="form.code" placeholder="如 doctor_admin" :disabled="form.is_system" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
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
import { getRoles, createRole, updateRole, deleteRole } from '@/api/role'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, keyword: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getRoles({
      page: query.page,
      page_size: query.pageSize,
      keyword: query.keyword || undefined,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function onReset() {
  query.keyword = ''
  query.page = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({ id: null, name: '', code: '', description: '', is_system: false })

function openDialog(row) {
  if (row) {
    Object.assign(form, {
      id: row.id, name: row.name, code: row.code,
      description: row.description || '', is_system: !!row.is_system,
    })
  } else {
    Object.assign(form, { id: null, name: '', code: '', description: '', is_system: false })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.name || !form.code) {
    ElMessage.warning('请填写角色名称和编码')
    return
  }
  submitting.value = true
  const payload = { name: form.name, code: form.code, description: form.description || undefined }
  try {
    if (form.id) {
      await updateRole(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createRole(payload)
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
    await ElMessageBox.confirm(`确认删除角色「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteRole(row.id)
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

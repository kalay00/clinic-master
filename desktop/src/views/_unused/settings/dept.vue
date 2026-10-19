<template>
  <div class="page-card">
    <div class="page-title">科室管理</div>
    <div class="filter-bar">
      <el-input v-model="query.keyword" placeholder="科室名称 / 编码" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="启用" value="enabled" />
        <el-option label="停用" value="disabled" />
      </el-select>
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增科室</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="name" label="科室名称" min-width="160" />
      <el-table-column prop="code" label="科室编码" width="160" />
      <el-table-column prop="description" label="科室描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'enabled' ? 'success' : 'info'" size="small">
            {{ row.status === 'enabled' ? '启用' : '停用' }}
          </el-tag>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑科室' : '新增科室'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="科室名称" required>
          <el-input v-model="form.name" placeholder="请输入科室名称" />
        </el-form-item>
        <el-form-item label="科室编码">
          <el-input v-model="form.code" placeholder="选填" />
        </el-form-item>
        <el-form-item label="科室描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="enabled">启用</el-radio>
            <el-radio value="disabled">停用</el-radio>
          </el-radio-group>
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
import { getDepartments, createDepartment, updateDepartment, deleteDepartment } from '@/api/department'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, keyword: '', status: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getDepartments({
      page: query.page,
      page_size: query.pageSize,
      keyword: query.keyword || undefined,
      status: query.status || undefined,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function onReset() {
  query.keyword = ''
  query.status = ''
  query.page = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({ id: null, name: '', code: '', description: '', status: 'enabled' })

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.name = row.name
    form.code = row.code || ''
    form.description = row.description || ''
    form.status = row.status || 'enabled'
  } else {
    form.id = null
    form.name = ''
    form.code = ''
    form.description = ''
    form.status = 'enabled'
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入科室名称')
    return
  }
  submitting.value = true
  const payload = {
    name: form.name,
    code: form.code || undefined,
    description: form.description || undefined,
    status: form.status,
  }
  try {
    if (form.id) {
      await updateDepartment(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createDepartment(payload)
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
    await ElMessageBox.confirm(`确认删除科室「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteDepartment(row.id)
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

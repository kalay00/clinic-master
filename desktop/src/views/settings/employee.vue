<template>
  <div class="page-card">
    <div class="page-title">员工管理</div>
    <div class="filter-bar">
      <el-input v-model="query.keyword" placeholder="用户名 / 姓名" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="正常" value="active" />
        <el-option label="停用" value="inactive" />
        <el-option label="锁定" value="locked" />
      </el-select>
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增员工</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="username" label="用户名" width="140" />
      <el-table-column prop="real_name" label="姓名" width="120" />
      <el-table-column prop="phone" label="手机号" width="160" />
      <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : (row.status === 'locked' ? 'danger' : 'info')" size="small">
            {{ row.status === 'active' ? '正常' : (row.status === 'locked' ? '锁定' : '停用') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="角色" min-width="160">
        <template #default="{ row }">
          <template v-if="row.roles && row.roles.length">
            <el-tag v-for="r in row.roles" :key="r" type="primary" effect="plain" class="role-tag">{{ r }}</el-tag>
          </template>
          <span v-else class="muted">—</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="primary" @click="openRole(row)">分配角色</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑员工' : '新增员工'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" :disabled="!!form.id" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="密码" v-if="!form.id">
          <el-input v-model="form.password" type="password" placeholder="初始密码" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="active">正常</el-radio>
            <el-radio value="inactive">停用</el-radio>
            <el-radio value="locked">锁定</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="roleVisible" title="分配角色" width="420px">
      <el-select v-model="roleForm.roleId" placeholder="选择角色" style="width: 100%">
        <el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" />
      </el-select>
      <template #footer>
        <el-button @click="roleVisible = false">取消</el-button>
        <el-button type="primary" :loading="roleSubmitting" @click="submitRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser, assignUserRole } from '@/api/user'
import { getRoles } from '@/api/role'

async function sha256(str) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str))
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('')
}

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, keyword: '', status: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getUsers({
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
const form = reactive({ id: null, username: '', real_name: '', phone: '', email: '', password: '', status: 'active' })

function openDialog(row) {
  if (row) {
    Object.assign(form, {
      id: row.id, username: row.username, real_name: row.real_name || '',
      phone: row.phone || '', email: row.email || '', password: '', status: row.status || 'active',
    })
  } else {
    Object.assign(form, {
      id: null, username: '', real_name: '', phone: '', email: '', password: '', status: 'active',
    })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.username) {
    ElMessage.warning('请输入用户名')
    return
  }
  submitting.value = true
  try {
    if (form.id) {
      await updateUser(form.id, {
        username: form.username,
        real_name: form.real_name || undefined,
        phone: form.phone || undefined,
        email: form.email || undefined,
        status: form.status,
      })
      ElMessage.success('更新成功')
    } else {
      if (!form.password) {
        ElMessage.warning('请输入初始密码')
        submitting.value = false
        return
      }
      const password_hash = await sha256(form.password)
      await createUser({
        username: form.username,
        password_hash,
        real_name: form.real_name || undefined,
        phone: form.phone || undefined,
        email: form.email || undefined,
        status: form.status,
      })
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
    await ElMessageBox.confirm(`确认删除员工「${row.username}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    // ignore
  }
}

const roleVisible = ref(false)
const roleSubmitting = ref(false)
const roleForm = reactive({ userId: null, roleId: '' })
const roleOptions = ref([])

async function openRole(row) {
  roleForm.userId = row.id
  roleForm.roleId = ''
  const res = await getRoles()
  roleOptions.value = res.items || res || []
  roleVisible.value = true
}

async function submitRole() {
  if (!roleForm.roleId) {
    ElMessage.warning('请选择角色')
    return
  }
  roleSubmitting.value = true
  try {
    await assignUserRole(roleForm.userId, roleForm.roleId)
    ElMessage.success('分配成功')
    roleVisible.value = false
  } finally {
    roleSubmitting.value = false
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
.role-tag {
  margin-right: 6px;
}
.muted {
  color: #c0c4cc;
}
</style>

<template>
  <div class="page-card">
    <div class="page-title">供应商管理</div>
    <div class="filter-bar">
      <el-input v-model="query.keyword" placeholder="供应商名称 / 编码" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="启用" value="active" />
        <el-option label="停用" value="inactive" />
      </el-select>
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增供应商</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="name" label="供应商名称" min-width="160" />
      <el-table-column prop="code" label="编码" width="140" />
      <el-table-column prop="contact_name" label="联系人" width="120" />
      <el-table-column prop="contact_phone" label="联系电话" width="160" />
      <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : '停用' }}
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑供应商' : '新增供应商'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="名称" required>
              <el-input v-model="form.name" placeholder="供应商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="编码">
              <el-input v-model="form.code" placeholder="留空自动生成" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="form.contact_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="form.contact_phone" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱">
          <el-input v-model="form.contact_email" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
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
import { getSuppliers, createSupplier, updateSupplier, deleteSupplier } from '@/api/inventory'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, keyword: '', status: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getSuppliers({
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
const form = reactive({
  id: null, name: '', code: '', contact_name: '', contact_phone: '',
  contact_email: '', address: '', status: 'active', remark: '',
})

function openDialog(row) {
  if (row) {
    Object.assign(form, {
      id: row.id, name: row.name, code: row.code || '',
      contact_name: row.contact_name || '', contact_phone: row.contact_phone || '',
      contact_email: row.contact_email || '', address: row.address || '',
      status: row.status || 'active', remark: row.remark || '',
    })
  } else {
    Object.assign(form, {
      id: null, name: '', code: '', contact_name: '', contact_phone: '',
      contact_email: '', address: '', status: 'active', remark: '',
    })
  }
  dialogVisible.value = true
}

// 后端要求 code 必填，未填写时自动生成
function generateSupplierCode() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  const rand = Math.random().toString(36).slice(2, 6).toUpperCase()
  return `SUP${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}${rand}`
}

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入供应商名称')
    return
  }
  submitting.value = true
  const payload = {
    name: form.name, code: form.code || generateSupplierCode(),
    contact_name: form.contact_name || undefined, contact_phone: form.contact_phone || undefined,
    contact_email: form.contact_email || undefined, address: form.address || undefined,
    status: form.status, remark: form.remark || undefined,
  }
  try {
    if (form.id) {
      await updateSupplier(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createSupplier(payload)
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
    await ElMessageBox.confirm(`确认删除供应商「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteSupplier(row.id)
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

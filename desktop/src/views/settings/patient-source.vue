<template>
  <div class="page-card">
    <div class="page-title">患者来源管理</div>
    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="来源内容" clearable style="width: 220px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增来源</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="content" label="来源内容" min-width="200" />
      <el-table-column prop="code" label="编码" width="140" />
      <el-table-column prop="sort" label="排序" width="90" align="center" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchList"
        @current-change="fetchList"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑来源' : '新增来源'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="来源内容" required>
          <el-input v-model="form.content" placeholder="如 微信 / 广告 / 转介绍" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" placeholder="选填" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
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
import { getDictionaryList, createDictionary, updateDictionary, deleteDictionary } from '@/api/dictionary'

const SUB_TYPE = 'patient_source'
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')

async function fetchList() {
  loading.value = true
  try {
    const res = await getDictionaryList({
      category: 'patient', sub_type: SUB_TYPE,
      keyword: keyword.value || undefined, page: page.value, page_size: pageSize.value,
    })
    tableData.value = res.data.items || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

function onReset() {
  keyword.value = ''
  page.value = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({ id: null, content: '', code: '', sort: 0, status: 'active', remark: '' })

function openDialog(row) {
  if (row) {
    Object.assign(form, {
      id: row.id, content: row.content, code: row.code || '',
      sort: row.sort || 0, status: row.status || 'active', remark: row.remark || '',
    })
  } else {
    Object.assign(form, { id: null, content: '', code: '', sort: 0, status: 'active', remark: '' })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.content) {
    ElMessage.warning('请输入来源内容')
    return
  }
  submitting.value = true
  const payload = {
    category: 'patient', sub_type: SUB_TYPE,
    content: form.content, code: form.code || undefined,
    sort: form.sort, status: form.status, remark: form.remark || undefined,
  }
  try {
    if (form.id) {
      await updateDictionary(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createDictionary(payload)
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
    await ElMessageBox.confirm('确认删除该来源？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteDictionary(row.id)
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

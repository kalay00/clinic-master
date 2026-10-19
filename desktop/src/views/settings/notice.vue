<template>
  <div class="page-card">
    <div class="page-title">系统公告</div>
    <div class="filter-bar">
      <el-input v-model="query.keyword" placeholder="标题 / 内容" clearable style="width: 240px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增公告</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="content" label="内容" min-width="320" show-overflow-tooltip />
      <el-table-column prop="sort" label="排序" width="90" align="center" />
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑公告' : '新增公告'" width="520px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="内容" required>
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="公告内容" />
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
import {
  getDictionaryList,
  createDictionary,
  updateDictionary,
  deleteDictionary,
} from '@/api/dictionary'

const CATEGORY = 'system'
const SUB_TYPE = 'notice'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, keyword: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await getDictionaryList({
      category: CATEGORY,
      sub_type: SUB_TYPE,
      keyword: query.keyword || undefined,
      page: query.page,
      page_size: query.pageSize,
    })
    tableData.value = res.data.items || []
    total.value = res.data.total || 0
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
const form = reactive({ id: null, content: '', sort: 0, status: true })

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.content = row.content || ''
    form.sort = row.sort || 0
    form.status = row.status !== false
  } else {
    Object.assign(form, { id: null, content: '', sort: 0, status: true })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.content) {
    ElMessage.warning('请输入公告内容')
    return
  }
  submitting.value = true
  const payload = {
    category: CATEGORY,
    sub_type: SUB_TYPE,
    content: form.content,
    sort: form.sort,
    status: form.status,
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
    await ElMessageBox.confirm('确认删除该公告？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteDictionary(row.id)
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

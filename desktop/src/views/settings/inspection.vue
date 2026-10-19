<template>
  <div class="page-card">
    <div class="page-title">检查项目</div>

    <el-tabs v-model="activeType" @tab-change="onTabChange">
      <el-tab-pane v-for="t in TYPES" :key="t.key" :label="t.label" :name="t.key" />
    </el-tabs>

    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="名称关键字" clearable style="width: 220px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-button type="primary" @click="onSearch">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增{{ currentLabel }}</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="content" label="名称" min-width="200" />
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
      <el-table-column label="操作" width="150" fixed="right">
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

    <el-dialog v-model="dialogVisible" :title="`${form.id ? '编辑' : '新增'}${currentLabel}`" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="form.content" :placeholder="currentPlaceholder" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDictionaryList, createDictionary, updateDictionary, deleteDictionary } from '@/api/dictionary'

const CATEGORY = 'inspection'
const TYPES = [
  { key: 'inspection_item', label: '检查项目', placeholder: '如 血常规 / CT' },
  { key: 'inspection_part', label: '检查部位', placeholder: '如 胸部 / 腹部' },
]

const activeType = ref(TYPES[0].key)
const currentLabel = computed(() => TYPES.find(t => t.key === activeType.value)?.label || '')
const currentPlaceholder = computed(() => TYPES.find(t => t.key === activeType.value)?.placeholder || '')

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
      category: CATEGORY,
      sub_type: activeType.value,
      keyword: keyword.value || undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    tableData.value = res.data.items || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

function onTabChange() {
  page.value = 1
  keyword.value = ''
  fetchList()
}

function onSearch() {
  page.value = 1
  fetchList()
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
      id: row.id,
      content: row.content || '',
      code: row.code || '',
      sort: row.sort || 0,
      status: row.status || 'active',
      remark: row.remark || '',
    })
  } else {
    Object.assign(form, { id: null, content: '', code: '', sort: 0, status: 'active', remark: '' })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.content) {
    ElMessage.warning(`请输入${currentLabel.value}名称`)
    return
  }
  submitting.value = true
  const payload = {
    category: CATEGORY,
    sub_type: activeType.value,
    content: form.content,
    code: form.code || undefined,
    sort: form.sort,
    status: form.status,
    remark: form.remark || undefined,
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
    await ElMessageBox.confirm(`确认删除「${row.content}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  await deleteDictionary(row.id)
  ElMessage.success('删除成功')
  fetchList()
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

<template>
  <div class="page-card">
    <div class="page-title">病历模板设置</div>

    <div class="filter-bar">
      <el-button type="primary" plain @click="openDialog()">新增病历模板</el-button>
      <el-button @click="fetchList">刷新</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="name" label="模板名称" min-width="200" />
      <el-table-column label="默认模板" width="110" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
          <el-button v-else link type="primary" @click="handleSetDefault(row)">设为默认</el-button>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="primary" @click="handleDuplicate(row)">复制</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑病历模板' : '新增病历模板'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="模板名称" required>
          <el-input v-model="form.name" placeholder="如：普通门诊病历" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="模板内容">
          <el-input
            v-model="form.configText"
            type="textarea"
            :rows="12"
            placeholder='JSON 格式，如：{"sections":[{"title":"主诉","key":"chief_complaint"}]}'
          />
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
  getPrintTemplates,
  createPrintTemplate,
  updatePrintTemplate,
  deletePrintTemplate,
  setDefaultPrintTemplate,
  duplicatePrintTemplate,
} from '@/api/printTemplate'

const TEMPLATE_TYPE = 'medical_record'

const DEFAULT_CONFIG = {
  sections: [
    { title: '主诉', key: 'chief_complaint' },
    { title: '现病史', key: 'present_illness' },
    { title: '既往史', key: 'past_history' },
    { title: '体格检查', key: 'physical_exam' },
    { title: '诊断', key: 'diagnosis' },
    { title: '处理意见', key: 'treatment_advice' },
  ],
}

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10 })

function formatTime(v) {
  if (!v) return '-'
  return String(v).replace('T', ' ').slice(0, 19)
}

async function fetchList() {
  loading.value = true
  try {
    const data = await getPrintTemplates({
      type: TEMPLATE_TYPE,
      page: query.page,
      page_size: query.pageSize,
    })
    tableData.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({ id: null, name: '', is_default: false, configText: '' })

function openDialog(row) {
  if (row) {
    Object.assign(form, {
      id: row.id,
      name: row.name || '',
      is_default: !!row.is_default,
      configText: JSON.stringify(row.template_config || DEFAULT_CONFIG, null, 2),
    })
  } else {
    Object.assign(form, {
      id: null,
      name: '',
      is_default: false,
      configText: JSON.stringify(DEFAULT_CONFIG, null, 2),
    })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  let config
  try {
    config = JSON.parse(form.configText || '{}')
  } catch {
    ElMessage.error('模板内容不是合法的 JSON')
    return
  }
  submitting.value = true
  const payload = {
    name: form.name,
    type: TEMPLATE_TYPE,
    template_config: config,
    is_default: form.is_default,
  }
  try {
    if (form.id) {
      await updatePrintTemplate(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createPrintTemplate(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

async function handleSetDefault(row) {
  await setDefaultPrintTemplate(row.id)
  ElMessage.success('已设为默认模板')
  fetchList()
}

async function handleDuplicate(row) {
  await duplicatePrintTemplate(row.id, `${row.name}-副本`)
  ElMessage.success('复制成功')
  fetchList()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除模板「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  await deletePrintTemplate(row.id)
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

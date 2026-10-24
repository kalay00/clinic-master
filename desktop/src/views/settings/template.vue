<template>
  <div class="settings-template-page">
    <el-card class="page-card" shadow="never">
    <el-tabs v-model="activeTab" class="tpl-tabs" @tab-change="onTabChange">
      <el-tab-pane label="病历模板" name="medical_record" />
      <el-tab-pane label="处方模板" name="prescription" />
      <el-tab-pane label="打印模板" name="bill" />
    </el-tabs>

    <div class="filter-bar">
      <el-button type="primary" @click="fetchList">刷新</el-button>
      <el-button type="primary" plain @click="openDialog()">新增模板</el-button>
    </div>

    <div class="table-wrap" ref="wrapRef">
      <el-table ref="tableRef" :height="tableHeight" :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="name" label="模板名称" min-width="180" />
      <el-table-column label="默认" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_default ? 'success' : 'info'" size="small">{{ row.is_default ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" min-width="170" />
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑模板' : '新增模板'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="模板名称" required>
          <el-input v-model="form.name" placeholder="模板名称" />
        </el-form-item>
        <el-form-item label="模板类型" required>
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="票据" value="bill" />
            <el-option label="处方" value="prescription" />
            <el-option label="病历" value="medical_record" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认模板">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="模板配置">
          <el-input v-model="configText" type="textarea" :rows="8" placeholder="JSON 配置" />
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
import { getPrintTemplates, createPrintTemplate, updatePrintTemplate, deletePrintTemplate } from '@/api/printTemplate'

import { useTableHeight } from '@/composables/useTableHeight'
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10 })

// 三类模板共用 /print-templates 接口，通过 type 区分
const activeTab = ref('medical_record')

async function fetchList() {
  loading.value = true
  try {
    const res = await getPrintTemplates({
      page: query.page,
      page_size: query.pageSize,
      type: activeTab.value,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false; refresh() }
}

function onTabChange() {
  query.page = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const configText = ref('{}')
const form = reactive({ id: null, name: '', type: 'medical_record', is_default: false })

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.name = row.name
    form.type = row.type
    form.is_default = !!row.is_default
    configText.value = typeof row.template_config === 'string'
      ? row.template_config
      : JSON.stringify(row.template_config || {}, null, 2)
  } else {
    form.id = null
    form.name = ''
    form.type = activeTab.value
    form.is_default = false
    configText.value = '{}'
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  let template_config
  try {
    template_config = JSON.parse(configText.value || '{}')
  } catch {
    ElMessage.warning('模板配置不是合法 JSON')
    return
  }
  submitting.value = true
  const payload = { name: form.name, type: form.type, is_default: form.is_default, template_config }
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

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除模板「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deletePrintTemplate(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    // ignore
  }
}

onMounted(fetchList)
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，筛选/分页固定，仅列表内部滚动 */
.settings-template-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; display: flex; flex-direction: column; }
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
.tpl-tabs {
  margin-bottom: 16px;
}
</style>

<template>
  <div class="page-card">
    <div class="page-title">第三方配置</div>
    <div class="filter-bar">
      <el-select v-model="query.service_type" placeholder="服务类型" clearable style="width: 160px" @change="fetchList">
        <el-option label="短信" value="sms" />
        <el-option label="微信" value="wechat" />
        <el-option label="支付" value="payment" />
        <el-option label="地图" value="map" />
        <el-option label="存储" value="storage" />
        <el-option label="其它" value="other" />
      </el-select>
      <el-select v-model="query.is_enabled" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="启用" :value="true" />
        <el-option label="停用" :value="false" />
      </el-select>
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新增配置</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="service_type" label="服务类型" width="120" />
      <el-table-column prop="provider" label="服务商" min-width="140" />
      <el-table-column label="配置摘要" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.config_data">{{ maskConfig(row.config_data) }}</span>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_enabled ? 'success' : 'info'" size="small">{{ row.is_enabled ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="success" @click="handleTest(row)">测试</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑配置' : '新增配置'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="服务类型" required>
          <el-select v-model="form.service_type" style="width: 100%">
            <el-option label="短信" value="sms" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付" value="payment" />
            <el-option label="地图" value="map" />
            <el-option label="存储" value="storage" />
            <el-option label="其它" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务商">
          <el-input v-model="form.provider" placeholder="如：阿里云 / 腾讯云" />
        </el-form-item>
        <el-form-item label="配置(JSON)" required>
          <el-input v-model="configText" type="textarea" :rows="6" placeholder='{"key": "value"}' />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.is_enabled">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">停用</el-radio>
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
import {
  getThirdPartyConfigs,
  createThirdPartyConfig,
  updateThirdPartyConfig,
  deleteThirdPartyConfig,
  testThirdPartyConfig,
} from '@/api/thirdPartyConfig'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, service_type: '', is_enabled: '' })

function maskConfig(data) {
  try {
    const obj = typeof data === 'string' ? JSON.parse(data) : data
    const keys = Object.keys(obj || {})
    if (!keys.length) return '-'
    return keys.map(k => `${k}: ${String(obj[k]).slice(0, 6)}${String(obj[k]).length > 6 ? '***' : ''}`).join('，')
  } catch {
    return String(data).slice(0, 40)
  }
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getThirdPartyConfigs({
      page: query.page,
      page_size: query.pageSize,
      service_type: query.service_type || undefined,
      is_enabled: query.is_enabled === '' ? undefined : query.is_enabled,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function onReset() {
  query.service_type = ''
  query.is_enabled = ''
  query.page = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const configText = ref('{}')
const form = reactive({
  id: null,
  service_type: 'sms',
  provider: '',
  config_data: {},
  is_enabled: true,
  remark: '',
})

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.service_type = row.service_type || 'sms'
    form.provider = row.provider || ''
    form.config_data = row.config_data || {}
    form.is_enabled = row.is_enabled !== false
    form.remark = row.remark || ''
    configText.value = typeof row.config_data === 'string'
      ? row.config_data
      : JSON.stringify(row.config_data || {}, null, 2)
  } else {
    Object.assign(form, { id: null, service_type: 'sms', provider: '', config_data: {}, is_enabled: true, remark: '' })
    configText.value = '{}'
  }
  dialogVisible.value = true
}

async function submit() {
  let parsed
  try {
    parsed = JSON.parse(configText.value || '{}')
  } catch {
    ElMessage.warning('配置格式不是合法 JSON')
    return
  }
  submitting.value = true
  const payload = {
    service_type: form.service_type,
    provider: form.provider || undefined,
    config_data: parsed,
    is_enabled: form.is_enabled,
    remark: form.remark || undefined,
  }
  try {
    if (form.id) {
      await updateThirdPartyConfig(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createThirdPartyConfig(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

async function handleTest(row) {
  try {
    await testThirdPartyConfig(row.id)
    ElMessage.success('测试通过')
  } catch (e) {
    // 拦截器处理
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除配置「${row.service_type}/${row.provider}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteThirdPartyConfig(row.id)
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
.muted {
  color: #bbb;
}
</style>

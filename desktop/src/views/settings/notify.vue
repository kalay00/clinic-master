<template>
  <div class="page-card">
    <div class="page-title">通知管理</div>
    <div class="filter-bar">
      <el-select v-model="query.notification_type" placeholder="类型" clearable style="width: 140px" @change="fetchList">
        <el-option label="短信" value="sms" />
        <el-option label="微信" value="wechat" />
        <el-option label="邮件" value="email" />
      </el-select>
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="fetchList">
        <el-option label="待发送" value="pending" />
        <el-option label="已发送" value="sent" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-button type="primary" @click="fetchList">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="primary" plain @click="openDialog()">新建通知</el-button>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="title" label="标题" min-width="160" />
      <el-table-column label="类型" width="90" align="center">
        <template #default="{ row }">
          <el-tag size="small">{{ typeText(row.notification_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="recipient_info" label="接收者" min-width="140" />
      <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发送时间" width="160">
        <template #default="{ row }">{{ row.sent_at || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="success" @click="handleSend(row)">发送</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑通知' : '新建通知'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="类型" required>
          <el-select v-model="form.notification_type" style="width: 100%">
            <el-option label="短信" value="sms" />
            <el-option label="微信" value="wechat" />
            <el-option label="邮件" value="email" />
          </el-select>
        </el-form-item>
        <el-form-item label="接收者类型" required>
          <el-radio-group v-model="form.recipient_type">
            <el-radio value="patient">患者</el-radio>
            <el-radio value="user">员工</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="接收者ID" required>
          <el-input v-model="form.recipient_id" placeholder="接收者 UUID" />
        </el-form-item>
        <el-form-item label="接收信息">
          <el-input v-model="form.recipient_info" placeholder="手机号 / OpenID 等" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="选填" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="form.content" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待发送" value="pending" />
            <el-option label="已发送" value="sent" />
            <el-option label="失败" value="failed" />
          </el-select>
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
  getNotifications,
  createNotification,
  updateNotification,
  deleteNotification,
  sendSMS,
  sendWeChat,
} from '@/api/notification'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, notification_type: '', status: '' })

function typeText(t) {
  return { sms: '短信', wechat: '微信', email: '邮件' }[t] || t
}
function statusText(s) {
  return { pending: '待发送', sent: '已发送', failed: '失败' }[s] || s || '待发送'
}
function statusType(s) {
  return { pending: 'info', sent: 'success', failed: 'danger' }[s] || 'info'
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getNotifications({
      page: query.page,
      page_size: query.pageSize,
      notification_type: query.notification_type || undefined,
      status: query.status || undefined,
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function onReset() {
  query.notification_type = ''
  query.status = ''
  query.page = 1
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({
  id: null,
  notification_type: 'sms',
  recipient_type: 'patient',
  recipient_id: '',
  recipient_info: '',
  title: '',
  content: '',
  status: 'pending',
})

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.notification_type = row.notification_type || 'sms'
    form.recipient_type = row.recipient_type || 'patient'
    form.recipient_id = row.recipient_id || ''
    form.recipient_info = row.recipient_info || ''
    form.title = row.title || ''
    form.content = row.content || ''
    form.status = row.status || 'pending'
  } else {
    Object.assign(form, {
      id: null, notification_type: 'sms', recipient_type: 'patient',
      recipient_id: '', recipient_info: '', title: '', content: '', status: 'pending',
    })
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.recipient_id) {
    ElMessage.warning('请输入接收者ID')
    return
  }
  if (!form.content) {
    ElMessage.warning('请输入内容')
    return
  }
  submitting.value = true
  const payload = {
    notification_type: form.notification_type,
    recipient_type: form.recipient_type,
    recipient_id: form.recipient_id,
    recipient_info: form.recipient_info || undefined,
    title: form.title || undefined,
    content: form.content,
    status: form.status,
  }
  try {
    if (form.id) {
      await updateNotification(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createNotification(payload)
      ElMessage.success('新建成功')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

async function handleSend(row) {
  try {
    await ElMessageBox.confirm(`确认发送通知「${row.title || row.content}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    if (row.notification_type === 'sms') {
      await sendSMS({ phone: row.recipient_info, message: row.content })
    } else if (row.notification_type === 'wechat') {
      await sendWeChat({ openid: row.recipient_info, template_id: '', data: { content: row.content } })
    } else {
      ElMessage.info('该类型暂不支持直接发送')
      return
    }
    ElMessage.success('发送成功')
    fetchList()
  } catch (e) {
    // 拦截器处理
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除该通知？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteNotification(row.id)
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

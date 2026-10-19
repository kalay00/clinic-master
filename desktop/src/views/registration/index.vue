<template>
  <div class="reg-list-page">
    <div class="page-head">
      <div class="page-title">挂号记录</div>
      <div class="head-actions">
        <el-button type="primary" :icon="Plus" @click="goCreate">新增挂号</el-button>
        <el-button :icon="Download" @click="onExport">导出</el-button>
      </div>
    </div>

    <el-card class="page-card" shadow="never">
      <el-radio-group v-model="statusTab" class="status-tabs" fill="#5b7cff" @change="onTabChange">
        <el-radio-button label="pending">未就诊</el-radio-button>
        <el-radio-button label="completed">已就诊</el-radio-button>
        <el-radio-button label="cancelled">已退号</el-radio-button>
      </el-radio-group>

      <el-form :inline="true" class="filter-form">
        <el-form-item label="挂号科室">
          <el-select v-model="query.department_id" placeholder="全部" clearable filterable style="width: 140px" @change="fetchList">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="挂号医生">
          <el-select v-model="query.doctor_id" placeholder="全部" clearable filterable style="width: 140px" @change="fetchList">
            <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="就诊时间">
          <el-date-picker v-model="query.dateRange" type="daterange" range-separator="-" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 260px" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="患者姓名/单号/档案号" style="width: 200px" @keyup.enter="onSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          <el-button :icon="Refresh" @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="registration_no" label="挂号单号" min-width="150" />
        <el-table-column prop="patient_name" label="患者姓名" width="100" />
        <el-table-column prop="patient_no" label="档案号" width="120" />
        <el-table-column prop="department_name" label="科室" width="100" />
        <el-table-column prop="doctor_name" label="接诊医生" width="100" />
        <el-table-column prop="registration_date" label="挂号日期" width="120" />
        <el-table-column prop="price" label="应收（元）" width="100">
          <template #default="{ row }">{{ fmt(row.price) }}</template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="已收（元）" width="100">
          <template #default="{ row }">{{ fmt(row.paid_amount) }}</template>
        </el-table-column>
        <el-table-column label="支付状态" width="90">
          <template #default="{ row }">
            <el-tag :type="payTag(row.payment_status)" size="small">{{ payMap[row.payment_status] || row.payment_status || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="就诊状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="onEdit(row)">编辑</el-button>
            <el-button type="success" link :disabled="row.status !== 'pending'" @click="onVisit(row)">就诊</el-button>
            <el-button type="danger" link :disabled="row.status === 'cancelled'" @click="onRefund(row)">退号</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="list-pagination"
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        layout="total, prev, pager, next, jumper"
        :total="total"
        @current-change="fetchList"
        @size-change="onSizeChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Search, Refresh } from '@element-plus/icons-vue'
import { getRegistrations, updateRegistration } from '@/api/registration'
import { getDepartments } from '@/api/department'
import { getDoctors } from '@/api/doctor'

defineOptions({ name: 'RegistrationList' })

const router = useRouter()
const loading = ref(false)
const total = ref(0)
const departments = ref([])
const doctors = ref([])

const statusTab = ref('pending')
const query = reactive({ page: 1, pageSize: 10, department_id: '', doctor_id: '', dateRange: [], keyword: '' })

const statusMap = { pending: '未就诊', completed: '已就诊', cancelled: '已退号' }
const payMap = { unpaid: '未支付', paid: '已支付', refunded: '已退费', cancelled: '已取消' }
const statusType = (s) => s === 'pending' ? 'warning' : (s === 'completed' ? 'success' : 'info')
const payTag = (s) => s === 'paid' ? 'success' : (s === 'unpaid' ? 'warning' : 'info')
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function fetchOptions() {
  try {
    const [d, doc] = await Promise.all([getDepartments({ page_size: 100 }), getDoctors({ page_size: 100 })])
    departments.value = d.items || []
    doctors.value = doc.items || []
  } catch (e) { /* ignore */ }
}

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: query.page, page_size: query.pageSize,
      status: statusTab.value,
      department_id: query.department_id || undefined,
      doctor_id: query.doctor_id || undefined,
      keyword: query.keyword || undefined,
    }
    if (query.dateRange && query.dateRange.length === 2) {
      params.start_date = query.dateRange[0]
      params.end_date = query.dateRange[1]
    }
    const res = await getRegistrations(params)
    tableData.value = res.items || []
    total.value = res.pagination?.total || 0
  } catch (e) {
    ElMessage.error('加载挂号列表失败')
  } finally {
    loading.value = false
  }
}

const tableData = ref([])
const goCreate = () => router.push('/registration/create')
const onSearch = () => { query.page = 1; fetchList() }
const onReset = () => { query.department_id = ''; query.doctor_id = ''; query.dateRange = []; query.keyword = ''; query.page = 1; fetchList() }
const onSizeChange = () => { query.page = 1; fetchList() }
const onTabChange = () => { query.page = 1; fetchList() }
const onExport = () => ElMessage.info('导出功能开发中')
const onEdit = (row) => router.push(`/registration/edit/${row.id}`)
const onVisit = (row) => router.push(`/consultation/western?regId=${row.id}`)

const onRefund = async (row) => {
  try {
    await ElMessageBox.confirm(`确定对挂号单 ${row.registration_no} 进行退号？`, '提示', { type: 'warning' })
    await updateRegistration(row.id, { status: 'cancelled' })
    ElMessage.success('退号成功')
    fetchList()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('退号失败')
  }
}

onMounted(() => { fetchOptions(); fetchList() })
</script>

<style lang="scss" scoped>
.reg-list-page { background: #f5f7fa; padding: 12px 16px 16px; }
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.page-title { font-size: 16px; font-weight: 600; color: #303133; }
.head-actions { display: flex; gap: 10px; }
.page-card { border-radius: 8px; }
.status-tabs { margin-bottom: 16px; }
.filter-form { margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.list-pagination { justify-content: flex-end; margin-top: 12px; }
</style>

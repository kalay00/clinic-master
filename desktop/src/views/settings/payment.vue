<template>
  <div class="page-card">
    <div class="page-title">支付记录</div>

    <div class="filter-bar">
      <el-select v-model="query.status" placeholder="支付状态" clearable style="width: 140px" @change="onSearch">
        <el-option label="待支付" value="pending" />
        <el-option label="成功" value="success" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-input v-model="query.patient_id" placeholder="患者ID" clearable style="width: 260px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-button type="primary" @click="onSearch">查询</el-button>
      <el-button @click="onReset">重置</el-button>
    </div>

    <div class="summary-bar">
      <span>共 <b>{{ total }}</b> 条记录</span>
      <span>本页合计：<b class="amount">{{ formatMoney(pageAmount) }}</b></span>
    </div>

    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="payment_no" label="支付单号" min-width="200" show-overflow-tooltip />
      <el-table-column label="支付方式" width="120" align="center">
        <template #default="{ row }">{{ methodText(row.payment_method) }}</template>
      </el-table-column>
      <el-table-column label="金额" width="130" align="right">
        <template #default="{ row }">
          <span class="amount">{{ formatMoney(row.amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="bill_id" label="账单ID" min-width="200" show-overflow-tooltip />
      <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
      <el-table-column label="支付时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getPayments } from '@/api/payment'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, pageSize: 10, status: '', patient_id: '' })

const pageAmount = computed(() =>
  tableData.value.reduce((sum, r) => sum + Number(r.amount || 0), 0)
)

const METHOD_MAP = {
  cash: '现金',
  wechat: '微信',
  alipay: '支付宝',
  card: '银行卡',
  balance: '余额',
  points: '积分',
}
const STATUS_MAP = { pending: '待支付', success: '成功', failed: '失败' }

function methodText(v) {
  return METHOD_MAP[v] || v || '-'
}
function statusText(v) {
  return STATUS_MAP[v] || v || '-'
}
function statusType(v) {
  if (v === 'success') return 'success'
  if (v === 'failed') return 'danger'
  return 'warning'
}
function formatMoney(v) {
  return `¥${Number(v || 0).toFixed(2)}`
}
function formatTime(v) {
  if (!v) return '-'
  return String(v).replace('T', ' ').slice(0, 19)
}

async function fetchList() {
  loading.value = true
  try {
    const data = await getPayments({
      page: query.page,
      page_size: query.pageSize,
      status: query.status || undefined,
      patient_id: query.patient_id || undefined,
    })
    tableData.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  query.page = 1
  fetchList()
}

function onReset() {
  query.status = ''
  query.patient_id = ''
  query.page = 1
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped lang="scss">
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.summary-bar {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  color: #606266;
  font-size: 13px;
}
.amount {
  color: #f56c6c;
  font-weight: 600;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

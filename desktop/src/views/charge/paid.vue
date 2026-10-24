<template>
  <div class="charge-page">
    <el-card class="page-card" shadow="never">
      <div class="card-header">
        <el-radio-group v-model="activeTab" class="status-tabs" fill="#5b7cff" @change="onTabChange">
          <el-radio-button label="unpaid">待收费</el-radio-button>
          <el-radio-button label="paid">已收费</el-radio-button>
          <el-radio-button label="refunded">已退费</el-radio-button>
        </el-radio-group>
      </div>

      <div class="page-body">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="账单类型">
          <el-select v-model="query.bill_type" placeholder="全部" clearable style="width: 130px" @change="fetchList">
            <el-option label="全部" value="" />
            <el-option label="挂号" value="registration" />
            <el-option label="诊疗" value="treatment" />
            <el-option label="处方" value="prescription" />
            <el-option label="药房" value="pharmacy" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker v-model="query.dateRange" type="daterange" range-separator="-" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 240px" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="输入账单号/患者姓名" style="width: 240px" @keyup.enter="onSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          <el-button :icon="Refresh" @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="table-wrap" ref="wrapRef">
        <el-table :data="tableData" border stripe v-loading="loading" ref="tableRef" :height="tableHeight">
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="bill_no" label="账单编号" min-width="160" />
        <el-table-column label="账单类型" width="100">
          <template #default="{ row }">{{ billTypeMap[row.bill_type] || row.bill_type }}</template>
        </el-table-column>
        <el-table-column prop="patient_name" label="患者姓名" width="100" />
        <el-table-column prop="total_amount" label="应收金额（元）" width="120">
          <template #default="{ row }">{{ formatMoney(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="实收金额（元）" width="120">
          <template #default="{ row }">{{ formatMoney(row.paid_amount) }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">{{ row.payment_method ? payMethodMap[row.payment_method] || row.payment_method : '-' }}</template>
        </el-table-column>
        <el-table-column prop="payment_time" label="收费时间" min-width="160">
          <template #default="{ row }">{{ row.payment_time || '-' }}</template>
        </el-table-column>
        <el-table-column label="收费状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="onDetail(row)">详情</el-button>
            <el-button v-if="row.status === 'unpaid'" type="success" link :icon="Money" @click="onPay(row)">收费</el-button>
            <el-button v-if="row.status === 'paid'" type="warning" link :icon="RefreshLeft" @click="onRefund(row)">退费</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      </div>

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
import { ElMessage } from 'element-plus'
import { Search, Refresh, Money, RefreshLeft, View } from '@element-plus/icons-vue'
import { getBills } from '@/api/payment'
import { useTableHeight } from '@/composables/useTableHeight'

defineOptions({ name: 'ChargePaid' })

const router = useRouter()
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const activeTab = ref('unpaid')
const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const query = reactive({
  page: 1, pageSize: 10, bill_type: '', dateRange: [], keyword: ''
})

const billTypeMap = { registration: '挂号', treatment: '诊疗', prescription: '处方', pharmacy: '药房' }
const payMethodMap = { cash: '现金', wechat: '微信', alipay: '支付宝', unionpay: '银联', insurance: '医保', medical_insurance: '医保' }
const statusMap = { unpaid: '待收费', paid: '已收费', refunded: '已退费', partial_refunded: '部分退费' }

const statusTag = (s) => s === 'unpaid' ? 'warning' : (s === 'paid' ? 'success' : 'info')
const formatMoney = (v) => v == null ? '0.00' : Number(v).toFixed(2)

function buildParams() {
  const p = { page: query.page, page_size: query.pageSize, status: activeTab.value }
  if (query.bill_type) p.bill_type = query.bill_type
  if (query.keyword) p.search = query.keyword
  return p
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getBills(buildParams())
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载收费列表失败')
  } finally {
    loading.value = false
    refresh()
  }
}

const onTabChange = () => { query.page = 1; fetchList() }
const onSearch = () => { query.page = 1; fetchList() }
const onReset = () => { query.bill_type = ''; query.dateRange = []; query.keyword = ''; query.page = 1; fetchList() }
const onSizeChange = () => { query.page = 1; fetchList() }

const onDetail = (row) => router.push(`/charge/detail/${row.id}`)
const onPay = (row) => router.push(`/charge/detail/${row.id}?mode=pay`)
const onRefund = (row) => router.push(`/charge/refund/${row.id}`)

onMounted(fetchList)
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，筛选/分页固定，仅列表内部滚动 */
.charge-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
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
  .status-tabs { margin-bottom: 0; }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.table-wrap { flex: 1; min-height: 0; overflow: hidden; }
.filter-form {
  flex-shrink: 0;
  margin-bottom: 12px;
  :deep(.el-form-item) { margin-bottom: 10px; }
}
.list-pagination {
  flex-shrink: 0;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>

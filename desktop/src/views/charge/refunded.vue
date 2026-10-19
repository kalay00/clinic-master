<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">退费记录</div>
    </div>

    <el-card class="page-card" shadow="never">
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
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="账单号/患者姓名" style="width: 240px" @keyup.enter="onSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          <el-button :icon="Refresh" @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="bill_no" label="账单编号" min-width="160" />
        <el-table-column label="账单类型" width="100">
          <template #default="{ row }">{{ billTypeMap[row.bill_type] || row.bill_type }}</template>
        </el-table-column>
        <el-table-column prop="patient_name" label="患者姓名" width="100" />
        <el-table-column prop="total_amount" label="应收（元）" width="110">
          <template #default="{ row }">{{ formatMoney(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="退费金额（元）" width="120">
          <template #default="{ row }">{{ formatMoney(row.paid_amount) }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="原支付方式" width="100">
          <template #default="{ row }">{{ row.payment_method ? payMethodMap[row.payment_method] || row.payment_method : '-' }}</template>
        </el-table-column>
        <el-table-column prop="payment_time" label="收费时间" min-width="160">
          <template #default="{ row }">{{ row.payment_time || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="onDetail(row)">详情</el-button>
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
import { ElMessage } from 'element-plus'
import { Search, Refresh, View } from '@element-plus/icons-vue'
import { getBills } from '@/api/payment'

defineOptions({ name: 'ChargeRefunded' })

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const query = reactive({ page: 1, pageSize: 10, bill_type: '', keyword: '' })

const billTypeMap = { registration: '挂号', treatment: '诊疗', prescription: '处方', pharmacy: '药房' }
const payMethodMap = { cash: '现金', wechat: '微信', alipay: '支付宝', unionpay: '银联', insurance: '医保', medical_insurance: '医保' }
const formatMoney = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function fetchList() {
  loading.value = true
  try {
    const res = await getBills({ page: query.page, page_size: query.pageSize, status: 'refunded', bill_type: query.bill_type || undefined, search: query.keyword || undefined })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载退费记录失败')
  } finally {
    loading.value = false
  }
}

const onSearch = () => { query.page = 1; fetchList() }
const onReset = () => { query.bill_type = ''; query.keyword = ''; query.page = 1; fetchList() }
const onSizeChange = () => { query.page = 1; fetchList() }
const onDetail = (row) => router.push(`/charge/detail/${row.id}`)

onMounted(fetchList)
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; }
.filter-form { margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.list-pagination { justify-content: flex-end; margin-top: 12px; }
</style>

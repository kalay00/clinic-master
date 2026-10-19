<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">收费统计</div>
      <el-button :icon="Download" @click="onExport">导出</el-button>
    </div>

    <el-card class="page-card" shadow="never">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="时间范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="-" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 240px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="fetchData">查询</el-button>
          <el-button :icon="Refresh" @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-row :gutter="16" class="stat-cards" v-loading="loading">
        <el-col :span="6"><div class="stat-card"><div class="stat-label">总收入（元）</div><div class="stat-value">{{ fmt(report.total_revenue) }}</div></div></el-col>
        <el-col :span="6"><div class="stat-card"><div class="stat-label">充值（元）</div><div class="stat-value">{{ fmt(report.prepaid) }}</div></div></el-col>
        <el-col :span="6"><div class="stat-card"><div class="stat-label">医保（元）</div><div class="stat-value">{{ fmt(report.insurance) }}</div></div></el-col>
        <el-col :span="6"><div class="stat-card warn"><div class="stat-label">退费（元）</div><div class="stat-value">{{ fmt(report.refund) }}</div></div></el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top:16px">
        <el-col :span="14">
          <el-card shadow="never" class="sub-card" v-loading="loading">
            <div class="sub-title">日收费趋势</div>
            <div ref="chartDay" class="chart-box"></div>
          </el-card>
        </el-col>
        <el-col :span="10">
          <el-card shadow="never" class="sub-card" v-loading="loading">
            <div class="sub-title">收费类型占比</div>
            <el-table :data="typeRows" border stripe size="small" max-height="320">
              <el-table-column prop="name" label="类型" />
              <el-table-column prop="value" label="金额（元）" align="right">
                <template #default="{ row }">{{ fmt(row.value) }}</template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-card shadow="never" class="sub-card" style="margin-top:16px" v-loading="loading">
        <div class="sub-title">支付方式占比</div>
        <el-table :data="methodRows" border stripe size="small">
          <el-table-column prop="name" label="支付方式" />
          <el-table-column prop="value" label="金额（元）" align="right">
            <template #default="{ row }">{{ fmt(row.value) }}</template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getRevenueReport } from '@/api/report'

defineOptions({ name: 'StatCharge' })

const loading = ref(false)
const dateRange = ref([])
const report = reactive({ total_revenue: 0, prepaid: 0, refund: 0, insurance: 0, by_type: {}, by_day: {}, by_method: {} })
const chartDay = ref(null)
let chart = null

const typeRows = ref([])
const methodRows = ref([])

const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)
const payMethodMap = { cash: '现金', wechat: '微信', alipay: '支付宝', unionpay: '银联', insurance: '医保', medical_insurance: '医保' }

function buildParams() {
  const p = {}
  if (dateRange.value && dateRange.value.length === 2) {
    p.start_date = dateRange.value[0]
    p.end_date = dateRange.value[1]
  }
  return p
}

async function fetchData() {
  loading.value = true
  try {
    const data = await getRevenueReport(buildParams())
    Object.assign(report, data || {})
    typeRows.value = Object.entries(report.by_type || {}).map(([name, value]) => ({ name, value }))
    methodRows.value = Object.entries(report.by_method || {}).map(([key, value]) => ({ name: payMethodMap[key] || key, value }))
    renderChart()
  } catch (e) {
    ElMessage.error('加载收费统计失败')
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chartDay.value) return
  if (!chart) chart = echarts.init(chartDay.value)
  const byDay = report.by_day || {}
  const days = Object.keys(byDay).sort()
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value' },
    series: [{ name: '收费金额', type: 'line', smooth: true, areaStyle: {}, data: days.map(d => byDay[d]) }]
  })
}

const onReset = () => { dateRange.value = []; fetchData() }
const onExport = () => ElMessage.info('导出功能开发中')

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; }
.filter-form { margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.stat-cards { margin-bottom: 4px; }
.stat-card { background: linear-gradient(135deg, #eef3ff, #f7f9ff); border-radius: 12px; padding: 18px 20px; border: 1px solid #e8eeff;
  .stat-label { color: #909399; font-size: 13px; }
  .stat-value { color: #5b7cff; font-size: 26px; font-weight: 700; margin-top: 6px; }
  &.warn .stat-value { color: #ffb347; }
}
.sub-card { .sub-title { font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 12px; } }
.chart-box { width: 100%; height: 300px; }
</style>

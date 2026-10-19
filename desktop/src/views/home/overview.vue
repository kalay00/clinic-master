<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">概况</div>
        <div class="his-page-subtitle">诊所今日经营概况</div>
      </div>
    </div>
    <div class="his-stat-row" v-loading="loading">
      <div class="his-stat-card" v-for="s in stats" :key="s.label">
        <div class="his-stat-icon" :style="{ background: s.color }">{{ s.icon }}</div>
        <div>
          <div class="his-stat-value">{{ s.value }}</div>
          <div class="his-stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>
    <div class="his-card his-mb-16">
      <div class="his-section-title">近7日收费趋势</div>
      <div ref="chartRef" style="height: 260px"></div>
    </div>
    <div class="his-card">
      <div class="his-section-title">待办事项（最近挂号）</div>
      <div class="his-table-wrap">
        <table class="his-table">
          <thead>
            <tr>
              <th>挂号单号</th>
              <th>患者姓名</th>
              <th>类型</th>
              <th>挂号日期</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in recent" :key="r.id">
              <td>{{ r.registration_no }}</td>
              <td>{{ r.patient_name || '-' }}</td>
              <td>{{ regTypeMap[r.registration_type] || r.registration_type || '-' }}</td>
              <td>{{ r.registration_date || '-' }}</td>
              <td>
                <span class="his-status-tag" :class="r.status === 'pending' ? 'his-status-orange' : 'his-status-green'">
                  {{ statusMap[r.status] || r.status }}
                </span>
              </td>
            </tr>
            <tr v-if="!recent.length">
              <td colspan="5" style="text-align: center; color: #909399">暂无待接诊挂号</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getDashboardData } from '@/api/dashboard'

defineOptions({ name: 'HomeOverview' })

const loading = ref(false)
const chartRef = ref(null)
let chart = null

const stats = ref([])
const recent = ref([])

const regTypeMap = { normal: '普通号', expert: '专家号', emergency: '急诊号' }
const statusMap = { pending: '待就诊', completed: '已就诊', cancelled: '已退号' }

function buildStats(d) {
  return [
    { label: '今日挂号', value: d.today_registrations ?? 0, icon: '+', color: 'linear-gradient(135deg,#5b7cff,#8aa4ff)' },
    { label: '今日收费（元）', value: '¥ ' + Number(d.today_revenue || 0).toLocaleString(), icon: '¥', color: 'linear-gradient(135deg,#4cd1a4,#6fdebb)' },
    { label: '待接诊', value: d.pending_registrations ?? 0, icon: '!', color: 'linear-gradient(135deg,#ffb347,#ffc670)' },
    { label: '患者总数', value: d.patient_total ?? 0, icon: 'U', color: 'linear-gradient(135deg,#ff6b6b,#ff8e8e)' },
  ]
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getDashboardData()
    const d = res.data || res || {}
    stats.value = buildStats(d)
    recent.value = d.recent_registrations || []
    const chart = d.chart || { dates: [], revenue: [], registrations: [] }
    renderChart(chart)
  } catch (e) {
    // 静默失败，保留占位
  } finally {
    loading.value = false
  }
}

function renderChart(c) {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['挂号数', '收费（元）'] },
    grid: { left: 50, right: 50, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: c.dates || [] },
    yAxis: [
      { type: 'value', name: '挂号数' },
      { type: 'value', name: '收费（元）' }
    ],
    series: [
      { name: '挂号数', type: 'bar', data: c.registrations || [] },
      { name: '收费（元）', type: 'line', yAxisIndex: 1, data: c.revenue || [] }
    ]
  })
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
</style>

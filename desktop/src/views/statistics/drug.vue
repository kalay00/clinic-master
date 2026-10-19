<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">药品统计</div>
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
        <el-col :span="8"><div class="stat-card"><div class="stat-label">药品销售总额（元）</div><div class="stat-value">{{ fmt(report.total_sales) }}</div></div></el-col>
        <el-col :span="8"><div class="stat-card"><div class="stat-label">库存总值（元）</div><div class="stat-value">{{ fmt(report.inventory_value) }}</div></div></el-col>
        <el-col :span="8"><div class="stat-card warn"><div class="stat-label">库存预警品种</div><div class="stat-value">{{ report.low_stock || 0 }}</div></div></el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top:16px">
        <el-col :span="12">
          <el-card shadow="never" class="sub-card" v-loading="loading">
            <div class="sub-title">药品分类销售占比</div>
            <el-table :data="categoryRows" border stripe size="small" max-height="300">
              <el-table-column prop="name" label="分类" />
              <el-table-column prop="value" label="销售额（元）" align="right">
                <template #default="{ row }">{{ fmt(row.value) }}</template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never" class="sub-card" v-loading="loading">
            <div class="sub-title">销售 TOP 药品</div>
            <el-table :data="topRows" border stripe size="small" max-height="300">
              <el-table-column type="index" label="排名" width="55" />
              <el-table-column prop="name" label="药品名称" />
              <el-table-column prop="value" label="销售额（元）" align="right">
                <template #default="{ row }">{{ fmt(row.value) }}</template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import { getDrugsReport } from '@/api/report'

defineOptions({ name: 'StatDrug' })

const loading = ref(false)
const dateRange = ref([])
const report = reactive({ total_sales: 0, inventory_value: 0, low_stock: 0, by_category: {}, top_drugs: {} })
const categoryRows = ref([])
const topRows = ref([])

const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

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
    const data = await getDrugsReport(buildParams())
    Object.assign(report, data || {})
    categoryRows.value = Object.entries(report.by_category || {}).map(([name, value]) => ({ name, value }))
    topRows.value = Object.entries(report.top_drugs || {}).map(([name, value]) => ({ name, value }))
  } catch (e) {
    ElMessage.error('加载药品统计失败')
  } finally {
    loading.value = false
  }
}

const onReset = () => { dateRange.value = []; fetchData() }
const onExport = () => ElMessage.info('导出功能开发中')

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; }
.filter-form { margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.stat-card { background: linear-gradient(135deg, #eef3ff, #f7f9ff); border-radius: 12px; padding: 18px 20px; border: 1px solid #e8eeff;
  .stat-label { color: #909399; font-size: 13px; }
  .stat-value { color: #5b7cff; font-size: 26px; font-weight: 700; margin-top: 6px; }
  &.warn .stat-value { color: #ffb347; }
}
.sub-card { .sub-title { font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 12px; } }
</style>

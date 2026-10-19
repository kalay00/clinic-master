<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">患者统计</div>
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
        <el-col :span="6"><div class="stat-card"><div class="stat-label">患者总数</div><div class="stat-value">{{ report.total_patients || 0 }}</div></div></el-col>
        <el-col :span="6"><div class="stat-card"><div class="stat-label">新增患者</div><div class="stat-value">{{ report.new_patients || 0 }}</div></div></el-col>
        <el-col :span="6"><div class="stat-card"><div class="stat-label">活跃患者</div><div class="stat-value">{{ report.active_patients || 0 }}</div></div></el-col>
        <el-col :span="6"><div class="stat-card warn"><div class="stat-label">会员患者</div><div class="stat-value">{{ report.member_patients || 0 }}</div></div></el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top:16px">
        <el-col :span="12">
          <el-card shadow="never" class="sub-card" v-loading="loading">
            <div class="sub-title">性别分布</div>
            <el-table :data="genderRows" border stripe size="small" max-height="300">
              <el-table-column prop="name" label="性别" />
              <el-table-column prop="value" label="人数" align="right" />
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never" class="sub-card" v-loading="loading">
            <div class="sub-title">年龄分布</div>
            <el-table :data="ageRows" border stripe size="small" max-height="300">
              <el-table-column prop="name" label="年龄段" />
              <el-table-column prop="value" label="人数" align="right" />
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
import { getPatientsReport } from '@/api/report'

defineOptions({ name: 'StatPatient' })

const loading = ref(false)
const dateRange = ref([])
const report = reactive({ total_patients: 0, new_patients: 0, active_patients: 0, member_patients: 0, by_gender: {}, by_age_group: {} })
const genderRows = ref([])
const ageRows = ref([])

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
    const data = await getPatientsReport(buildParams())
    Object.assign(report, data || {})
    genderRows.value = Object.entries(report.by_gender || {}).map(([name, value]) => ({ name, value }))
    ageRows.value = Object.entries(report.by_age_group || {}).map(([name, value]) => ({ name, value }))
  } catch (e) {
    ElMessage.error('加载患者统计失败')
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

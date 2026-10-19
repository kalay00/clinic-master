<template>
  <div class="schedule-week">
    <!-- 顶部工具栏 -->
    <div class="page-head">
      <div class="week-nav">
        <el-button :type="weekMode === 'prev' ? 'primary' : 'default'" plain @click="goPrevWeek">上一周</el-button>
        <el-button :type="weekMode === 'current' ? 'primary' : 'default'" plain @click="goThisWeek">本周</el-button>
        <el-button :type="weekMode === 'next' ? 'primary' : 'default'" plain @click="goNextWeek">下一周</el-button>
      </div>
      <el-select v-model="query.department_id" placeholder="请选择科室" clearable filterable style="width: 180px" @change="onSearch">
        <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
      </el-select>
      <el-input v-model="query.keyword" placeholder="请输入医生姓名" clearable style="width: 220px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
    </div>

    <!-- 周范围提示 -->
    <div class="week-tip">
      当前：{{ weekRangeText }}（{{ weekMode === 'current' ? '本周' : weekMode === 'prev' ? '上一周' : '下一周' }}）
    </div>

    <!-- 周表格 -->
    <el-card shadow="never" class="week-card">
      <el-table
        :data="doctorRows"
        border
        stripe
        v-loading="loading"
        :empty-text="emptyText"
      >
        <el-table-column prop="name" label="医生姓名" width="100" fixed />
        <el-table-column prop="dept_name" label="科室" width="120" fixed />

        <el-table-column
          v-for="d in weekDays"
          :key="d.iso"
          :label="`${d.monthDay} ${d.weekday}`"
          min-width="110"
          align="center"
        >
          <template #default="{ row }">
            <div class="day-cell" :class="{ 'is-past': d.iso < todayStr }">
              <div
                class="slot"
                :class="slotClass(row, d.iso, 'morning')"
                @click="d.iso < todayStr ? null : openScheduleDialog(row, d.iso, 'morning')"
              >
                {{ slotText(row, d.iso, 'morning') }}
              </div>
              <div
                class="slot"
                :class="slotClass(row, d.iso, 'afternoon')"
                @click="d.iso < todayStr ? null : openScheduleDialog(row, d.iso, 'afternoon')"
              >
                {{ slotText(row, d.iso, 'afternoon') }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="80" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              :icon="Setting"
              :disabled="weekRangeEnd < todayStr"
              @click="openScheduleDialog(row)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 设置排班弹窗（按医生 + 当前月） -->
    <el-dialog
      v-model="dialogVisible"
      :title="`${activeDoctor?.name || ''} 医生排班详情`"
      width="900px"
      top="5vh"
    >
      <div class="schedule-detail" v-if="activeDoctor">
        <!-- 左侧橙色信息栏 -->
        <div class="left-panel">
          <div class="doctor-name">{{ activeDoctor.name }}</div>
          <div class="date-info">{{ activeDateText }}</div>
          <div class="block">
            <div class="block-title">上午</div>
            <div>接诊时间：08:00-12:00</div>
            <div>号源数：{{ morningQuota }}</div>
            <div>接诊人数：{{ morningUsed }}</div>
          </div>
          <div class="block">
            <div class="block-title">下午</div>
            <div>接诊时间：14:00-18:00</div>
            <div>号源数：{{ afternoonQuota }}</div>
            <div>接诊人数：{{ afternoonUsed }}</div>
          </div>
        </div>

        <!-- 右侧月历 -->
        <div class="right-panel">
          <div class="month-bar">
            <el-select v-model="monthStr" style="width: 180px" @change="onMonthChange">
              <el-option v-for="m in monthOptions" :key="m.value" :label="m.label" :value="m.value" />
            </el-select>
            <el-button type="primary" @click="onSetSchedule">设置排班</el-button>
            <el-button @click="onCloseBooking">关闭预约</el-button>
          </div>

          <div class="weekday-row">
            <div v-for="w in weekdayNames" :key="w">{{ w }}</div>
          </div>
          <div class="month-grid">
            <div
              v-for="day in monthDays"
              :key="day.iso"
              class="month-cell"
              :class="{
                'is-past': day.iso < todayStr,
                'is-today': day.iso === todayStr,
                'is-active': day.iso === activeDate,
                'has-schedule': day.morning || day.afternoon,
                'is-closed': day.closed,
              }"
              @click="day.iso < todayStr ? null : onDayClick(day)"
            >
              <div class="num">{{ day.day }}</div>
              <div v-if="day.iso >= todayStr" class="status">
                <template v-if="day.closed"><span class="s-closed">休息</span></template>
                <template v-else-if="day.morning && day.afternoon"><span class="s-active">号源 {{ day.morning.total_quota }}</span></template>
                <template v-else-if="day.morning"><span class="s-active">上午号源 {{ day.morning.total_quota }}</span></template>
                <template v-else-if="day.afternoon"><span class="s-active">下午号源 {{ day.afternoon.total_quota }}</span></template>
                <template v-else><span class="s-none">未排班</span></template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Setting } from '@element-plus/icons-vue'
import { getSchedules, createSchedule, updateSchedule, deleteSchedule, pauseSchedule } from '@/api/registration'
import { getDepartments } from '@/api/department'
import { getDoctors } from '@/api/doctor'
import { fetchAllPages } from '@/utils/paging'

defineOptions({ name: 'RegistrationSchedule' })

const loading = ref(false)
const emptyText = ref('加载中…')
const departments = ref([])
const doctorList = ref([]) // 全部医生

const query = reactive({ department_id: '', keyword: '' })

// ========== 日期工具 ==========
const today = new Date()
const todayStr = formatDate(today)

function formatDate(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getMonday(d) {
  const x = new Date(d)
  const dow = (x.getDay() + 6) % 7 // 0=Mon
  x.setDate(x.getDate() - dow)
  x.setHours(0, 0, 0, 0)
  return x
}

// 当前周锚点（周一）
const weekAnchor = ref(getMonday(today))
const weekMode = ref('current')

const weekDays = computed(() => {
  const arr = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekAnchor.value)
    d.setDate(d.getDate() + i)
    arr.push({
      iso: formatDate(d),
      date: d,
      monthDay: `${d.getMonth() + 1}/${d.getDate()}`,
      weekday: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][i],
    })
  }
  return arr
})

const weekRangeStart = computed(() => weekDays.value[0].iso)
const weekRangeEnd = computed(() => weekDays.value[6].iso)
const weekRangeText = computed(() => `${weekRangeStart.value} ~ ${weekRangeEnd.value}`)

function goPrevWeek() { weekMode.value = 'prev'; weekAnchor.value = addDays(weekAnchor.value, -7); fetchSchedules() }
function goNextWeek() { weekMode.value = 'next'; weekAnchor.value = addDays(weekAnchor.value, 7); fetchSchedules() }
function goThisWeek() { weekMode.value = 'current'; weekAnchor.value = getMonday(today); fetchSchedules() }
function addDays(d, n) { const x = new Date(d); x.setDate(x.getDate() + n); return x }

// ========== 排班数据 ==========
// scheduleMap: { [doctor_id]: { [dateIso]: { morning?: scheduleObj, afternoon?: scheduleObj } } }
const scheduleMap = ref({})

async function fetchSchedules() {
  loading.value = true
  try {
    // 拉本周全部排班（接口为 skip/limit 分页，需分页取完）
    const items = await fetchAllPages(p => getSchedules({
      start_date: weekRangeStart.value,
      end_date: weekRangeEnd.value,
      department_id: query.department_id || undefined,
      ...p,
    }))
    const map = {}
    items.forEach(s => {
      const dateKey = s.schedule_date?.slice(0, 10)
      if (!dateKey) return
      map[s.doctor_id] ??= {}
      map[s.doctor_id][dateKey] ??= {}
      map[s.doctor_id][dateKey][s.time_slot] = s
    })
    scheduleMap.value = map
    emptyText.value = '本周暂无排班'
  } catch {
    scheduleMap.value = {}
  } finally {
    loading.value = false
  }
}

// 医生行（按筛选/搜索）
const doctorRows = computed(() => {
  let list = doctorList.value
  if (query.department_id) list = list.filter(d => d.department_id === query.department_id || d.department?.id === query.department_id)
  if (query.keyword.trim()) {
    const kw = query.keyword.trim()
    list = list.filter(d => (d.name || '').includes(kw))
  }
  return list.map(d => ({
    id: d.id,
    name: d.name,
    dept_name: deptNameOf(d),
  }))
})

const deptNameOf = (doc) => {
  if (doc.department_name) return doc.department_name
  if (doc.department?.name) return doc.department.name
  if (doc.department_id) return departments.value.find(x => x.id === doc.department_id)?.name || '-'
  return '-'
}

function onSearch() { fetchSchedules() }

// ========== 单元格渲染 ==========
function getCell(doctorId, iso, slot) {
  return scheduleMap.value[doctorId]?.[iso]?.[slot] || null
}

function slotText(row, iso, slot) {
  const s = getCell(row.id, iso, slot)
  if (!s) return '休'
  if (s.status === 'cancelled') return '取消'
  if (s.status === 'paused') return '暂停'
  return `${s.used_quota || 0}/${s.total_quota || 0}`
}

function slotClass(row, iso, slot) {
  const s = getCell(row.id, iso, slot)
  if (!s) return 'slot-rest'
  if (s.status === 'cancelled') return 'slot-cancelled'
  if (s.status === 'paused') return 'slot-paused'
  return 'slot-active'
}

// ========== 排班弹窗（按医生 + 月历） ==========
const dialogVisible = ref(false)
const activeDoctor = ref(null)
const activeDate = ref(todayStr)
const activeDateText = computed(() => {
  if (!activeDate.value) return ''
  const d = new Date(activeDate.value)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${weekdayNames[d.getDay() === 0 ? 6 : d.getDay() - 1]}`
})

const monthStr = ref(formatDate(today).slice(0, 7))
const monthOptions = computed(() => {
  const arr = []
  const start = new Date(today.getFullYear() - 1, today.getMonth(), 1)
  for (let i = 0; i < 24; i++) {
    const d = new Date(start.getFullYear(), start.getMonth() + i, 1)
    arr.push({ value: formatDate(d).slice(0, 7), label: `${d.getFullYear()}年${d.getMonth() + 1}月` })
  }
  return arr
})

const weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

// 当月排班（医生维度）
const monthSchedules = ref([])

const monthDays = computed(() => {
  const [y, m] = monthStr.value.split('-').map(Number)
  const first = new Date(y, m - 1, 1)
  const startWeekday = (first.getDay() + 6) % 7 // 0=Mon
  const daysInMonth = new Date(y, m, 0).getDate()
  const cells = []
  // 上月填充
  for (let i = 0; i < startWeekday; i++) {
    const d = new Date(y, m - 1, -startWeekday + i + 1)
    cells.push(makeCell(d, true))
  }
  for (let i = 1; i <= daysInMonth; i++) {
    cells.push(makeCell(new Date(y, m - 1, i), false))
  }
  while (cells.length % 7) {
    const last = cells[cells.length - 1].date
    const next = new Date(last)
    next.setDate(next.getDate() + 1)
    cells.push(makeCell(next, true))
  }
  return cells
})

function makeCell(d, otherMonth) {
  const iso = formatDate(d)
  const morning = monthSchedules.value.find(s => s.schedule_date?.slice(0, 10) === iso && s.time_slot === 'morning') || null
  const afternoon = monthSchedules.value.find(s => s.schedule_date?.slice(0, 10) === iso && s.time_slot === 'afternoon') || null
  return {
    iso, day: d.getDate(), date: d, otherMonth,
    morning, afternoon,
    closed: morning?.status === 'cancelled' || afternoon?.status === 'cancelled',
  }
}

async function fetchMonthSchedules() {
  if (!activeDoctor.value) return
  const [y, m] = monthStr.value.split('-').map(Number)
  const start = formatDate(new Date(y, m - 1, 1))
  const end = formatDate(new Date(y, m, 0))
  try {
    monthSchedules.value = await fetchAllPages(p => getSchedules({
      doctor_id: activeDoctor.value.id,
      start_date: start, end_date: end,
      ...p,
    }))
  } catch {
    monthSchedules.value = []
  }
}

function onMonthChange() { fetchMonthSchedules() }

// 当前查看日的上午/下午数据（用于左侧信息栏）
const activeScheduleMorning = computed(() => monthSchedules.value.find(s => s.schedule_date?.slice(0, 10) === activeDate.value && s.time_slot === 'morning') || null)
const activeScheduleAfternoon = computed(() => monthSchedules.value.find(s => s.schedule_date?.slice(0, 10) === activeDate.value && s.time_slot === 'afternoon') || null)
const morningQuota = computed(() => activeScheduleMorning.value?.total_quota ?? 20)
const morningUsed = computed(() => activeScheduleMorning.value?.used_quota ?? 0)
const afternoonQuota = computed(() => activeScheduleAfternoon.value?.total_quota ?? 20)
const afternoonUsed = computed(() => activeScheduleAfternoon.value?.used_quota ?? 0)

// 打开弹窗（来自周视图单元格 / 操作齿轮）
async function openScheduleDialog(doctor, iso, slot) {
  activeDoctor.value = doctor
  const dateIso = iso || (slot ? activeDate.value : todayStr)
  activeDate.value = dateIso
  monthStr.value = dateIso.slice(0, 7)
  dialogVisible.value = true
  await fetchMonthSchedules()
}

function onDayClick(day) {
  activeDate.value = day.iso
}

async function onSetSchedule() {
  if (!activeDoctor.value) return
  const date = activeDate.value
  const existM = activeScheduleMorning.value
  const existA = activeScheduleAfternoon.value
  const buildPayload = (slot) => ({
    doctor_id: activeDoctor.value.id,
    department_id: departments.value.find(d => d.name === activeDoctor.value.dept_name)?.id || undefined,
    schedule_date: date,
    time_slot: slot,
    start_time: slot === 'morning' ? '08:00:00' : '14:00:00',
    end_time: slot === 'morning' ? '12:00:00' : '18:00:00',
    total_quota: 20,
    price: 0,
    status: 'active',
  })
  try {
    if (existM) await updateSchedule(existM.id, buildPayload('morning'))
    else await createSchedule(buildPayload('morning'))
    if (existA) await updateSchedule(existA.id, buildPayload('afternoon'))
    else await createSchedule(buildPayload('afternoon'))
    ElMessage.success('已设置排班')
    await fetchMonthSchedules()
    fetchSchedules()
  } catch (e) {
    ElMessage.error(e?.message || '设置失败')
  }
}

async function onCloseBooking() {
  const targets = [activeScheduleMorning.value, activeScheduleAfternoon.value].filter(Boolean)
  if (!targets.length) { ElMessage.warning('该日尚未排班，无需关闭'); return }
  try { await ElMessageBox.confirm('确认将该日上午/下午的预约关闭（取消）？', '提示', { type: 'warning' }) } catch { return }
  try {
    for (const s of targets) {
      // 用 pause 保留记录；用户也可后端支持 cancelled
      await pauseSchedule(s.id)
    }
    ElMessage.success('已关闭预约')
    await fetchMonthSchedules()
    fetchSchedules()
  } catch { /* ignore */ }
}

// ========== 初始化 ==========
async function fetchOptions() {
  try {
    const [d, doc] = await Promise.all([
      fetchAllPages(p => getDepartments({ ...p })),
      fetchAllPages(p => getDoctors({ ...p })),
    ])
    departments.value = d || []
    doctorList.value = doc || []
  } catch { /* ignore */ }
}

onMounted(async () => {
  await fetchOptions()
  await fetchSchedules()
})
</script>

<style lang="scss" scoped>
.schedule-week { background: #f5f7fa; padding: 12px 16px 16px; min-height: 100vh; box-sizing: border-box; }
.page-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.week-nav { display: flex; gap: 6px; }
.week-tip { color: #606266; font-size: 13px; margin-bottom: 10px; }
.week-card { border-radius: 8px; }
.day-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px 2px;
  &.is-past { opacity: 0.5; }
}
.slot {
  font-size: 12px;
  padding: 4px 0;
  border-radius: 4px;
  cursor: pointer;
  &.slot-active { color: #f56c6c; background: #fff5f5; }
  &.slot-rest { color: #c0c4cc; background: #f5f7fa; }
  &.slot-paused { color: #e6a23c; background: #fdf6ec; }
  &.slot-cancelled { color: #909399; background: #f5f7fa; }
  &.slot-rest { cursor: default; }
}
.day-cell.is-past .slot { cursor: not-allowed; }

// 设置弹窗
.schedule-detail { display: flex; gap: 16px; min-height: 500px; }
.left-panel {
  width: 220px;
  background: #f5a623;
  color: #fff;
  border-radius: 8px;
  padding: 20px 18px;
  flex-shrink: 0;
}
.doctor-name { font-size: 18px; font-weight: 600; margin-bottom: 6px; }
.date-info { font-size: 14px; margin-bottom: 18px; opacity: 0.95; }
.block { margin-top: 16px; font-size: 13px; line-height: 1.9; }
.block-title { font-weight: 600; margin-bottom: 4px; }
.right-panel { flex: 1; min-width: 0; }
.month-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; justify-content: flex-end; }
.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  font-size: 13px;
  color: #606266;
  text-align: center;
  padding: 6px 0;
  border-bottom: 1px solid #ebeef5;
}
.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}
.month-cell {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  min-height: 76px;
  padding: 8px 6px;
  cursor: pointer;
  transition: all 0.15s;
  &.other-month { background: #fafafa; }
  &.is-past { background: #f4f4f5; color: #c0c4cc; cursor: not-allowed; }
  &.is-today .num { color: #5b7cff; font-weight: 700; }
  &.is-active { border-color: #5b7cff; box-shadow: 0 0 0 2px rgba(91,124,255,0.15); }
  &:hover:not(.is-past) { border-color: #5b7cff; }
  .num { font-size: 16px; font-weight: 600; }
  .status { font-size: 12px; margin-top: 6px; }
  .s-active { color: #5b7cff; }
  .s-closed { color: #909399; }
  .s-none { color: #c0c4cc; }
}
</style>
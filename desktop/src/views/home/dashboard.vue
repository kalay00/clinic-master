<template>
  <div class="db-page">
    <div class="db-toolbar">
      <div class="db-filter">
        <label class="filter-label">创建时间</label>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          size="default"
          class="db-date-picker"
        />
      </div>
      <div class="db-filter">
        <label class="filter-label">接诊状态</label>
        <el-select v-model="filters.status" placeholder="全部" class="db-status-select" style="width: 140px">
          <el-option label="全部" value="" />
          <el-option label="待接诊" value="pending" />
          <el-option label="已叫号" value="called" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
      <div class="db-filter db-search">
        <input v-model="filters.keyword" type="text" class="filter-input search-input" placeholder="输入患者姓名" />
        <button class="search-btn" @click="onSearch">
          <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="#fff"/></svg>
        </button>
      </div>
    </div>

    <div class="db-grid">
      <div
        v-for="item in list" :key="item.id"
        class="patient-card"
        :class="{ active: selectedId === item.id }"
        @click="selectedId = item.id"
      >
        <div class="card-main">
          <div class="card-avatar" :class="{ female: item.gender === '女', male: item.gender !== '女' }">
            <svg v-if="item.gender === '女'" viewBox="0 0 24 24">
              <path d="M12 2C9.24 2 7 4.24 7 7c0 2.1 1.18 3.93 2.91 4.86a5.002 5.002 0 0 0-4.27 4.95c0 2.76 2.24 5 5 5 .75 0 1.46-.17 2.1-.46.14 1.43 1.34 2.55 2.8 2.55.55 0 1-.45 1-1v-1h-1.17c-.41 0-.75-.31-.83-.72l-.23-1.14c1.25.84 2.75 1.36 4.36 1.36 2.76 0 5-2.24 5-5a5.002 5.002 0 0 0-4.27-4.95C15.82 10.93 17 9.1 17 7c0-2.76-2.24-5-5-5z" fill="currentColor"/>
            </svg>
            <svg v-else viewBox="0 0 24 24">
              <path d="M12 2a5 5 0 1 0 .01 10.01A5 5 0 0 0 12 2zm0 11c-3.31 0-10 1.67-10 5v2c0 .55.45 1 1 1h2c.55 0 1-.45 1-1v-1.5c0-.28.22-.5.5-.5h1c.28 0 .5.22.5.5V20c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-1.5c0-.28.22-.5.5-.5h1c.28 0 .5.22.5.5V20c0 .55.45 1 1 1h2c.55 0 1-.45 1-1v-2c0-3.33-6.69-5-10-5z" fill="currentColor"/>
            </svg>
          </div>
          <div class="card-info">
            <div class="card-row">
              <span class="card-name">{{ item.name }}</span>
              <span v-if="item.vipLevel" class="tag tag-vip">VIP{{ item.vipLevel }}</span>
              <span class="card-meta-text">{{ item.gender }} {{ item.age }}</span>
              <span class="tag tag-status">{{ item.statusText }}</span>
            </div>
            <div class="card-row card-detail">
              <span>创建时间：{{ item.createTime }}</span>
              <span>科室：{{ item.dept }}</span>
              <span>医生：{{ item.doctor }}</span>
            </div>
            <div class="card-row card-phone">手机号码：{{ item.phone }}</div>
          </div>
        </div>
        <div class="card-actions">
          <button class="action-btn action-primary" @click.stop="onReceive(item)">接诊</button>
          <span class="action-divider"></span>
          <button class="action-btn action-default" @click.stop="onView(item)">查看患者信息</button>
        </div>
      </div>
      <el-empty v-if="!loading && list.length === 0" description="暂无待接诊患者" />
    </div>

    <div class="db-pagination">
      <button class="page-btn" :disabled="page <= 1" @click="page--">
        <svg viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" fill="currentColor"/></svg>
      </button>
      <button class="page-btn page-active">{{ page }}</button>
      <button class="page-btn" @click="page++">
        <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" fill="currentColor"/></svg>
      </button>
      <span class="page-info">每页10条，共{{ total }}条</span>
      <span class="page-goto">前往第</span>
      <input v-model.number="gotoPage" type="number" class="page-input" min="1" @keyup.enter="page = gotoPage" />
      <span class="page-goto">页</span>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRegistrations } from '@/api/registration'

const router = useRouter()
const selectedId = ref('')
const page = ref(1)
const gotoPage = ref(1)
const total = ref(0)
const loading = ref(false)
const list = ref([])

const filters = reactive({
  dateRange: [],
  status: 'pending',
  keyword: ''
})

const statusMap = {
  pending: '待接诊',
  called: '已叫号',
  completed: '已完成',
  cancelled: '已取消',
}

function normalize(r) {
  return {
    id: r.id,
    patientId: r.patient_id,
    name: r.patient_name || '-',
    vipLevel: r.member_level || '',
    gender: r.gender || '-',
    age: r.age != null ? r.age : '-',
    statusText: statusMap[r.status] || r.status || '待接诊',
    createTime: r.created_at || r.registration_date || '-',
    dept: r.department_name || '-',
    doctor: r.doctor_name || '-',
    phone: r.patient_phone || '-',
  }
}

async function fetchList() {
  loading.value = true
  try {
    const [start_date, end_date] = Array.isArray(filters.dateRange) ? filters.dateRange : []
    const res = await getRegistrations({
      page: page.value,
      page_size: 10,
      status: filters.status || undefined,
      keyword: filters.keyword || undefined,
      start_date,
      end_date,
    })
    const items = res.items || []
    list.value = items.map(normalize)
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  gotoPage.value = 1
  fetchList()
}

watch(() => filters.status, () => {
  page.value = 1
  gotoPage.value = 1
  fetchList()
})
watch(() => filters.dateRange, () => {
  page.value = 1
  gotoPage.value = 1
  fetchList()
}, { deep: true })
watch(page, (v) => {
  gotoPage.value = v
  fetchList()
})

function onReceive(item) {
  if (item.id) {
    router.push(`/consultation/record?regId=${item.id}`)
  }
}

function onView(item) {
  if (item.patientId) {
    router.push(`/patients/index?patient_id=${item.patientId}`)
  }
}

onMounted(fetchList)
</script>

<style lang="scss" scoped>
.db-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.db-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.db-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

:deep(.db-date-picker) {
  .el-input__wrapper {
    border-radius: 4px;
  }
}

.filter-input {
  height: 34px;
  padding: 0 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  font-size: 13px;
  color: #303133;
  outline: none;
  transition: border-color 0.2s;
}

.filter-input:focus {
  border-color: #5b7cff;
}

.db-search {
  flex: 1;
  justify-content: flex-end;
}

.search-input {
  width: 220px;
  border-radius: 4px 0 0 4px;
  border-right: none;
}

.search-btn {
  width: 36px;
  height: 34px;
  border: none;
  background: #5b7cff;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.search-btn svg {
  width: 16px;
  height: 16px;
}

.db-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .db-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .db-grid { grid-template-columns: 1fr; }
}

.patient-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.patient-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.patient-card.active {
  border-color: #5b7cff;
  box-shadow: 0 0 0 1px #5b7cff;
}

.card-main {
  padding: 16px;
  display: flex;
  gap: 12px;
}

.card-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
}

.card-avatar.male {
  background: linear-gradient(135deg, #5b7cff 0%, #3d5eff 100%);
}

.card-avatar.female {
  background: linear-gradient(135deg, #ff8fab 0%, #ff6b9d 100%);
}

.card-avatar svg {
  width: 28px;
  height: 28px;
  opacity: 0.95;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.card-row:last-child {
  margin-bottom: 0;
}

.card-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.card-meta-text {
  font-size: 13px;
  color: #606266;
}

.tag {
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 10px;
  line-height: 1.5;
}

.tag-vip {
  background: #fff7e6;
  color: #ff9f00;
  font-weight: 600;
}

.tag-status {
  background: #fff0f3;
  color: #ff4d4f;
}

.card-detail,
.card-phone {
  font-size: 12px;
  color: #909399;
  gap: 12px;
}

.card-phone {
  color: #606266;
}

.card-actions {
  display: flex;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  height: 42px;
}

.action-btn {
  flex: 1;
  height: 100%;
  border: none;
  background: transparent;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s;
}

.action-primary {
  color: #5b7cff;
}

.action-primary:hover {
  color: #3d5eff;
  background: #f5f7ff;
}

.action-default {
  color: #606266;
}

.action-default:hover {
  color: #303133;
  background: #f5f7fa;
}

.action-divider {
  width: 1px;
  height: 18px;
  background: #e4e7ed;
}

.db-pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.page-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #dcdfe6;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #606266;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #5b7cff;
  color: #5b7cff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn svg {
  width: 16px;
  height: 16px;
}

.page-active {
  background: #5b7cff;
  border-color: #5b7cff;
  color: #fff;
}

.page-info {
  margin: 0 8px;
}

.page-input {
  width: 40px;
  height: 28px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  text-align: center;
  font-size: 13px;
}
</style>

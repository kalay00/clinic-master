<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">患者管理</div>
      <div class="head-actions">
        <el-button type="primary" :icon="Plus" @click="goCreate">新增患者</el-button>
        <el-button :icon="Download" @click="onExport">导出</el-button>
      </div>
    </div>

    <el-card class="page-card" shadow="never">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="患者姓名/手机号/编号" style="width: 220px" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="query.gender" placeholder="全部" clearable style="width: 100px">
            <el-option label="全部" value="" />
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border stripe v-loading="loading" style="width: 100%">
        <el-table-column type="index" label="序号" width="55" align="center" />
        <el-table-column prop="patient_no" label="患者编码" min-width="120" />
        <el-table-column prop="name" label="患者姓名" min-width="100" />
        <el-table-column label="性别" width="60" align="center">
          <template #default="{ row }">{{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '未知' }}</template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70" align="center" />
        <el-table-column prop="phone" label="手机号码" min-width="130" />
        <el-table-column label="会员等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="levelName(row.member_level_id) === '非会员' ? 'info' : 'warning'" size="small">{{ levelName(row.member_level_id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" min-width="160" />
        <el-table-column label="操作" width="300" align="center" class-name="op-cell">
          <template #default="{ row }">
            <el-button type="primary" link :icon="FirstAidKit" @click="onRegister(row)">挂号</el-button>
            <el-button type="primary" link :icon="Edit" @click="onEdit(row)">编辑</el-button>
            <el-button type="warning" link :icon="User" @click="onSetMember(row)">设置会员</el-button>
            <el-button type="danger" link :icon="Delete" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="list-pagination"
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        layout="total, prev, pager, next, jumper"
        :total="total"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </el-card>

    <el-dialog v-model="showSetMember" title="设置会员" width="440px" append-to-body>
      <el-form :model="memberForm" label-width="80px">
        <el-form-item label="患者">
          <span>{{ memberForm.name }}（{{ memberForm.phone || '无手机号' }}）</span>
        </el-form-item>
        <el-form-item label="当前状态">
          <el-tag :type="statusType(memberForm.member_status)" size="small">{{ statusText(memberForm.member_status) }}</el-tag>
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="memberForm.member_level_id" placeholder="请选择等级" clearable style="width: 100%">
            <el-option v-for="lv in levelOptions" :key="lv.id" :label="lv.name" :value="lv.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="会员状态">
          <el-select v-model="memberForm.member_status" placeholder="请选择状态" style="width: 100%">
            <el-option label="正常" value="active" />
            <el-option label="已停用" value="inactive" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item label="到期时间">
          <el-date-picker v-model="memberForm.expire_date" type="date" value-format="YYYY-MM-DD" placeholder="不填则永久" clearable style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="memberForm.remark" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSetMember = false">取消</el-button>
        <el-button type="primary" :loading="memberLoading" @click="saveMemberLevel">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Search, FirstAidKit, Edit, User, Delete } from '@element-plus/icons-vue'
import { getPatients, getMemberLevels, deletePatient } from '@/api/patient'
import { setMemberLevel, updateMember } from '@/api/member'

defineOptions({ name: 'PatientList' })

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const levelMap = ref({})
const query = reactive({
  page: 1,
  pageSize: 10,
  keyword: '',
  gender: '',
  memberType: '',
  dateRange: []
})

function levelName(id) {
  return (id && levelMap.value[id]) || '非会员'
}

async function loadLevels() {
  try {
    const res = await getMemberLevels({ page: 1, page_size: 100 })
    ;(res.items || []).forEach(l => { levelMap.value[l.id] = l.name })
  } catch (e) { /* 等级非强依赖 */ }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getPatients({
      keyword: query.keyword,
      gender: query.gender,
      page: query.page,
      pageSize: query.pageSize
    })
    tableData.value = res.items || []
    total.value = (res.pagination && res.pagination.total) || 0
  } catch (e) {
    ElMessage.error('加载患者列表失败')
  } finally {
    loading.value = false
  }
}

const onSearch = () => { query.page = 1; fetchData() }
const onExport = () => ElMessage.info('导出功能开发中')
const goCreate = () => router.push('/patients/create')
const onRegister = (row) => router.push('/registration/create?patientId=' + row.id)
const onEdit = (row) => router.push('/patients/edit/' + row.id)

const showSetMember = ref(false)
const memberLoading = ref(false)
const levelOptions = ref([])
const memberForm = reactive({
  id: '',
  name: '',
  phone: '',
  member_level_id: '',
  member_status: 'active',
  expire_date: '',
  remark: ''
})

const statusText = (s) => ({ active: '正常', inactive: '已停用', expired: '已过期' }[s] || '正常')
const statusType = (s) => ({ active: 'success', inactive: 'info', expired: 'warning' }[s] || 'success')

const onSetMember = (row) => {
  memberForm.id = row.id
  memberForm.name = row.name
  memberForm.phone = row.phone || ''
  memberForm.member_level_id = row.member_level_id || ''
  memberForm.member_status = row.member_status || 'active'
  memberForm.expire_date = row.expire_date || ''
  memberForm.remark = ''
  levelOptions.value = Object.entries(levelMap.value).map(([id, name]) => ({ id, name }))
  showSetMember.value = true
}

const saveMemberLevel = async () => {
  memberLoading.value = true
  try {
    // 等级变更（含流水）
    await setMemberLevel(memberForm.id, {
      member_level_id: memberForm.member_level_id || null,
      remark: memberForm.remark || undefined
    })
    // 状态 / 到期时间
    await updateMember(memberForm.id, {
      member_status: memberForm.member_status,
      expire_date: memberForm.expire_date || null
    })
    ElMessage.success('设置成功')
    showSetMember.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('设置失败')
  } finally {
    memberLoading.value = false
  }
}

const onDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除患者 ${row.name} 吗？`, '提示', { type: 'warning' })
    await deletePatient(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { /* 取消或失败 */ }
}

onMounted(() => {
  loadLevels()
  fetchData()
})
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; }
.head-actions { display: flex; gap: 10px; }
.filter-form { margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.list-pagination { justify-content: flex-end; margin-top: 12px; }
:deep(.op-cell .cell) { white-space: nowrap; }
</style>

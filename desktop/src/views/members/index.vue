<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">会员管理</div>
      <el-button :icon="Download" @click="onExport">导出</el-button>
    </div>

    <el-card class="page-card" shadow="never">
      <el-radio-group v-model="activeTab" class="status-tabs" fill="#5b7cff">
        <el-radio-button label="list">会员列表</el-radio-button>
        <el-radio-button label="stored">储值管理</el-radio-button>
        <el-radio-button label="points">积分管理</el-radio-button>
        <el-radio-button label="settings">会员设置</el-radio-button>
      </el-radio-group>

      <template v-if="activeTab === 'list'">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="会员等级">
            <el-select v-model="listQuery.level_id" placeholder="全部" clearable style="width: 140px">
              <el-option label="全部" value="" />
              <el-option v-for="lv in levels" :key="lv.id" :label="lv.name" :value="lv.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-input v-model="listQuery.keyword" placeholder="患者姓名/手机号码/会员卡号" style="width: 240px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="listQuery.expireWarning">会员到期预警</el-checkbox>
          </el-form-item>
        </el-form>
        <el-table :data="members" border stripe v-loading="loading">
          <el-table-column type="index" label="序号" width="55" />
          <el-table-column prop="patient_no" label="卡号" width="130" />
          <el-table-column label="会员等级" width="100">
            <template #default="{ row }"><span class="vip">{{ row.member_level_name || '非会员' }}</span></template>
          </el-table-column>
          <el-table-column prop="name" label="会员姓名" width="100" />
          <el-table-column prop="phone" label="手机号码" width="130" />
          <el-table-column prop="consumption_total" label="累积消费（元）" width="110" />
          <el-table-column prop="balance" label="储值余额（元）" width="110" />
          <el-table-column prop="stored_total" label="累计储值（元）" width="110" />
          <el-table-column prop="points" label="积分" width="80" />
          <el-table-column prop="created_at" label="开卡时间" width="160" />
          <el-table-column prop="expire_date" label="到期时间" width="120">
            <template #default="{ row }">{{ row.expire_date || '永久' }}</template>
          </el-table-column>
          <el-table-column label="会员状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.member_status === 'active' ? 'success' : 'info'" size="small">
                {{ row.member_status === 'active' ? '正常' : row.member_status === 'expired' ? '已过期' : '已停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="320" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openEdit(row)">编辑</el-button>
              <el-button type="primary" link @click="openRecharge(row)">充值</el-button>
              <el-button type="primary" link @click="openLevel(row)">设置等级</el-button>
              <el-button type="primary" link @click="openPointsChange(row)">积分变动</el-button>
              <el-button type="primary" link @click="openRefund(row)">退款</el-button>
              <el-button type="primary" link @click="openChangeLog(row)">等级变更记录</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>

      <template v-else-if="activeTab === 'stored'">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="会员等级">
            <el-select v-model="storedQuery.level_id" placeholder="全部" clearable style="width: 140px">
              <el-option label="全部" value="" />
              <el-option v-for="lv in levels" :key="lv.id" :label="lv.name" :value="lv.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-input v-model="storedQuery.keyword" placeholder="患者姓名/手机号码/会员卡号" style="width: 240px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="members" border stripe v-loading="loading">
          <el-table-column type="index" label="序号" width="55" />
          <el-table-column prop="patient_no" label="卡号" width="130" />
          <el-table-column label="会员等级" width="100"><template #default="{ row }"><span class="vip">{{ row.member_level_name || '非会员' }}</span></template></el-table-column>
          <el-table-column prop="name" label="会员姓名" width="100" />
          <el-table-column prop="phone" label="手机号码" width="130" />
          <el-table-column prop="stored_total" label="累计储值（元）" width="120" />
          <el-table-column prop="gift_total" label="累计赠送（元）" width="120" />
          <el-table-column prop="balance" label="余额（元）" width="110" />
          <el-table-column prop="consumption_total" label="储值累计消费（元）" width="140" />
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openRecharge(row)">充值</el-button>
              <el-button type="primary" link @click="openRefund(row)">退款</el-button>
              <el-button type="primary" link @click="openRechargeLog(row)">充值/退款记录</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>

      <template v-else-if="activeTab === 'points'">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="会员等级">
            <el-select v-model="pointsQuery.level_id" placeholder="全部" clearable style="width: 140px">
              <el-option label="全部" value="" />
              <el-option v-for="lv in levels" :key="lv.id" :label="lv.name" :value="lv.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-input v-model="pointsQuery.keyword" placeholder="患者姓名/手机号码/会员卡号" style="width: 240px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="members" border stripe v-loading="loading">
          <el-table-column type="index" label="序号" width="55" />
          <el-table-column prop="patient_no" label="卡号" min-width="130" />
          <el-table-column label="会员等级" min-width="100"><template #default="{ row }"><span class="vip">{{ row.member_level_name || '非会员' }}</span></template></el-table-column>
          <el-table-column prop="name" label="会员姓名" min-width="100" />
          <el-table-column prop="phone" label="手机号码" min-width="130" />
          <el-table-column prop="points" label="积分" min-width="100" />
          <el-table-column label="操作" width="200" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="openPointsChange(row)">积分变动</el-button>
              <el-button type="primary" link @click="openPointsLog(row)">积分变动记录</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>

      <template v-else>
        <div class="filter-form">
          <el-button type="primary" :icon="Plus" @click="showMemberType = true">新增会员类型</el-button>
          <el-button type="warning" :icon="Setting" @click="showCondition = true">会员条件设置</el-button>
        </div>
        <el-table :data="settingsData" border stripe v-loading="levelsLoading">
          <el-table-column type="index" label="序号" width="55" />
          <el-table-column label="会员等级" min-width="120"><template #default="{ row }"><span class="vip">{{ row.name }}</span></template></el-table-column>
          <el-table-column prop="name" label="会员名称" min-width="160" />
          <el-table-column prop="discount_rate" label="折扣率" min-width="100" />
          <el-table-column prop="upgrade_threshold" label="升级阈值" min-width="140" />
          <el-table-column prop="status" label="状态" min-width="100"><template #default="{ row }"><el-switch :model-value="row.status === 'active'" /></template></el-table-column>
          <el-table-column label="操作" width="100" align="center"><template #default="{ row }"><el-button type="primary" link @click="openEditLevel(row)">编辑</el-button></template></el-table-column>
        </el-table>
      </template>

      <el-pagination class="list-pagination" v-model:current-page="page" :current-page="page" v-model:page-size="pageSize" layout="total, prev, pager, next, jumper" :total="total" @current-change="(p) => { page = p; fetchMembers() }" @size-change="(s) => { pageSize = s; fetchMembers() }" />
    </el-card>

    <MemberTypeDialog v-model="showMemberType" :edit-data="editLevelData" @saved="fetchLevels" />
    <ConditionDialog v-model="showCondition" />
    <LevelDialog v-model="showLevel" :member="selected" @confirmed="fetchMembers" />
    <RechargeDialog v-model="showRecharge" :member="selected" @confirmed="fetchMembers" />
    <RefundDialog v-model="showRefund" :member="selected" @confirmed="fetchMembers" />
    <RechargeLogDialog v-model="showRechargeLog" :member="selected" />
    <ChangeLogDialog v-model="showChangeLog" :member="selected" />
    <PointsChangeDialog v-model="showPointsChange" :member="selected" @confirmed="fetchMembers" />
    <PointsLogDialog v-model="showPointsLog" :member="selected" />

    <el-dialog v-model="showEdit" title="编辑会员" width="460px" append-to-body>
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editForm.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="editForm.member_level_id" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="lv in levels" :key="lv.id" :label="lv.name" :value="lv.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="会员状态">
          <el-select v-model="editForm.member_status" style="width: 100%">
            <el-option label="正常" value="active" />
            <el-option label="已停用" value="inactive" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item label="到期时间">
          <el-date-picker v-model="editForm.expire_date" type="date" value-format="YYYY-MM-DD" placeholder="永久" clearable style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search, Plus, Setting } from '@element-plus/icons-vue'
import MemberTypeDialog from './member-type.vue'
import ConditionDialog from './condition.vue'
import LevelDialog from './level.vue'
import RechargeDialog from './recharge.vue'
import RefundDialog from './refund.vue'
import RechargeLogDialog from './recharge-log.vue'
import ChangeLogDialog from './change-log.vue'
import PointsChangeDialog from './points-change.vue'
import PointsLogDialog from './points-log.vue'
import { getMembers, updateMember } from '@/api/member'
import { getMemberLevels as getLevels } from '@/api/patient'

defineOptions({ name: 'MemberManage' })

const activeTab = ref('list')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const levelsLoading = ref(false)
const members = ref([])
const levels = ref([])
const selected = ref({})

const listQuery = reactive({ level_id: '', keyword: '', expireWarning: false })
const storedQuery = reactive({ level_id: '', keyword: '' })
const pointsQuery = reactive({ level_id: '', keyword: '' })

const settingsData = ref([])

const showMemberType = ref(false)
const editLevelData = ref(null)
const openEditLevel = (row) => {
  editLevelData.value = row
  showMemberType.value = true
}
const showCondition = ref(false)
const showLevel = ref(false)
const showRecharge = ref(false)
const showRefund = ref(false)
const showRechargeLog = ref(false)
const showChangeLog = ref(false)
const showPointsChange = ref(false)
const showPointsLog = ref(false)
const showEdit = ref(false)
const editForm = reactive({
  id: '',
  name: '',
  gender: '',
  phone: '',
  member_level_id: '',
  member_status: 'active',
  expire_date: ''
})
const editLoading = ref(false)

async function fetchMembers() {
  loading.value = true
  try {
    const q = activeTab.value === 'stored' ? storedQuery : activeTab.value === 'points' ? pointsQuery : listQuery
    const res = await getMembers({
      page: page.value,
      pageSize: pageSize.value,
      keyword: q.keyword,
      level_id: q.level_id || undefined
    })
    members.value = res.items || []
    total.value = (res.pagination && res.pagination.total) || 0
  } catch (e) {
    ElMessage.error('加载会员列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchLevels() {
  levelsLoading.value = true
  try {
    const res = await getLevels({ page: 1, page_size: 100 })
    levels.value = res.items || []
    settingsData.value = levels.value
  } catch (e) { /* 等级非强依赖 */ }
  finally {
    levelsLoading.value = false
  }
}

const onSearch = () => { page.value = 1; fetchMembers() }
const onExport = () => ElMessage.info('导出功能开发中')

const openDialog = (dialogRef, member) => { selected.value = member; dialogRef.value = true }
const openLevel = (member) => openDialog(showLevel, member)
const openRecharge = (member) => openDialog(showRecharge, member)
const openRefund = (member) => openDialog(showRefund, member)
const openRechargeLog = (member) => openDialog(showRechargeLog, member)
const openChangeLog = (member) => openDialog(showChangeLog, member)
const openPointsChange = (member) => openDialog(showPointsChange, member)
const openPointsLog = (member) => openDialog(showPointsLog, member)

const openEdit = (member) => {
  editForm.id = member.id
  editForm.name = member.name
  editForm.gender = member.gender === 'male' ? '男' : member.gender === 'female' ? '女' : (member.gender || '')
  editForm.phone = member.phone || ''
  editForm.member_level_id = member.member_level_id || ''
  editForm.member_status = member.member_status || 'active'
  editForm.expire_date = member.expire_date || ''
  showEdit.value = true
}

const saveEdit = async () => {
  editLoading.value = true
  try {
    await updateMember(editForm.id, {
      name: editForm.name,
      gender: editForm.gender,
      phone: editForm.phone,
      member_level_id: editForm.member_level_id,
      member_status: editForm.member_status,
      expire_date: editForm.expire_date
    })
    ElMessage.success('保存成功')
    showEdit.value = false
    fetchMembers()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    editLoading.value = false
  }
}

onMounted(() => {
  fetchLevels()
  fetchMembers()
})
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; }
.status-tabs { margin-bottom: 16px; }
.filter-form { margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.list-pagination { justify-content: flex-end; margin-top: 12px; }
.vip { color: #ffb347; font-weight: 600; }
</style>

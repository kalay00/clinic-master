<template>
  <div class="patient-edit-page">
    <el-card class="page-card" shadow="never">
      <div class="card-header">
        <el-tabs v-model="activeTab" class="patient-tabs">
          <el-tab-pane label="个人信息" name="info"></el-tab-pane>
          <el-tab-pane label="电子病历" name="records"></el-tab-pane>
          <el-tab-pane label="收费记录" name="charges"></el-tab-pane>
        </el-tabs>
        <div class="head-actions">
          <el-button type="primary" :icon="DocumentChecked" :loading="saving" @click="onSave">保存</el-button>
          <el-button :icon="Back" @click="onBack">返回</el-button>
        </div>
      </div>

      <div class="page-body">
      <div v-if="activeTab === 'info'" class="pane-scroll">
        <div class="section-title">基本信息</div>
        <el-form :model="form" label-width="110px" class="patient-form">
          <el-row :gutter="24">
            <el-col :span="6"><el-form-item label="患者姓名" required><el-input v-model="form.name" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="患者卡号"><el-input v-model="form.cardNo" placeholder="请输入病人卡号" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="患者年龄"><el-input v-model="form.age" placeholder="自动计算" readonly disabled><template #append>岁</template></el-input></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="出生日期" required><el-date-picker v-model="form.birthday" type="date" style="width:100%" @change="onBirthdayChange" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="6"><el-form-item label="性别" required><el-select v-model="form.gender" style="width:100%"><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="手机号码"><el-input v-model="form.phone" placeholder="请输入手机号码" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="证件号码"><el-input v-model="form.idCard" placeholder="请输入证件号码" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="患者来源"><el-select v-model="form.source" placeholder="请选择" style="width:100%"><el-option label="自然到店" value="1" /><el-option label="转诊" value="2" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="6"><el-form-item label="会员等级"><el-select v-model="form.member_level_id" placeholder="请选择" clearable style="width:100%"><el-option v-for="lv in levelOptions" :key="lv.id" :label="lv.name" :value="lv.id" /></el-select></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="到期时间"><el-date-picker v-model="form.expireDate" type="date" style="width:100%" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="民族"><el-input v-model="form.nation" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="婚姻状况"><el-select v-model="form.marriage" placeholder="请选择" style="width:100%"><el-option label="未婚" value="single" /><el-option label="已婚" value="married" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="6"><el-form-item label="学历"><el-select v-model="form.education" placeholder="请选择" style="width:100%"><el-option label="本科" value="本科" /><el-option label="大专" value="大专" /><el-option label="高中" value="高中" /></el-select></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="地址"><el-input v-model="form.address" placeholder="请输入详细地址" /></el-form-item></el-col>
            <el-col :span="6"><el-form-item label="职业"><el-select v-model="form.job" placeholder="请选择" style="width:100%"><el-option label="教师" value="teacher" /><el-option label="医生" value="doctor" /></el-select></el-form-item></el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="6"><el-form-item label="工作单位"><el-input v-model="form.company" /></el-form-item></el-col>
            <el-col :span="18"><el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item></el-col>
          </el-row>
        </el-form>

        <div class="section-title">
          关联家庭成员
          <el-button class="fr" type="success" :icon="Plus" @click="openFamilyDialog()">添加家庭成员</el-button>
        </div>
        <el-table :data="familyList" border stripe v-loading="familyLoading" style="width: 100%">
          <el-table-column type="index" label="序号" width="55" align="center" />
          <el-table-column prop="relation" label="家庭关系" width="100" />
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="gender" label="性别" width="70" align="center">
            <template #default="{ row }">{{ formatGender(row.gender) }}</template>
          </el-table-column>
          <el-table-column prop="age" label="单位" width="80" align="center" />
          <el-table-column prop="birthday" label="出生日期" width="120" />
          <el-table-column prop="phone" label="手机号码" min-width="130" />
          <el-table-column prop="created_at" label="创建时间" min-width="160" />
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="openFamilyDialog(row)">编辑</el-button>
              <el-button type="danger" link @click="removeFamily(row)">取消关联</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else-if="activeTab === 'records'" class="pane-scroll record-layout">
        <el-row :gutter="20">
          <el-col :span="8">
            <div v-if="recordsLoading" class="empty-tip">加载中...</div>
            <div v-else-if="!records.length" class="empty-tip">暂无电子病历</div>
            <div v-else class="timeline">
              <div v-for="(item, idx) in records" :key="item.id || idx" class="timeline-item" :class="{ active: activeRecordIndex === idx }" @click="activeRecordIndex = idx">
                <div class="time">{{ item.created_at }}</div>
                <div class="card">
                  <div>门诊编号：{{ item.no || item.id || '-' }}</div>
                  <div>诊断：{{ item.diagnosis || '-' }}</div>
                  <div>接诊科室：{{ item.department_name || item.department || '-' }}</div>
                  <div>接诊医生：{{ item.doctor_name || item.doctor || '-' }}</div>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="16">
            <div v-if="activeRecord" v-loading="recordsLoading">
              <div class="record-head">
                <el-tag :type="activeRecord.visit_type === 'return' ? 'warning' : 'success'" size="large">{{ activeRecord.visit_type === 'return' ? '复诊' : '初诊' }}</el-tag>
                <div class="actions">
                  <el-button type="primary" link :icon="Edit">编辑病历</el-button>
                  <el-button type="primary" link :icon="Printer">打印病历</el-button>
                </div>
              </div>
              <div class="section-title">病历信息</div>
              <div class="record-text">
                <p><strong>发病日期：</strong>{{ activeRecord.onset_date || activeRecord.created_at?.slice(0, 10) || '-' }}</p>
                <p><strong>主诉：</strong>{{ activeRecord.chief_complaint || '-' }}</p>
                <p><strong>现病史：</strong>{{ activeRecord.present_illness || '-' }}</p>
                <p><strong>既往史：</strong>{{ activeRecord.past_history || '-' }}</p>
                <p><strong>过敏史：</strong>{{ activeRecord.allergy_history || '否认' }}</p>
                <p><strong>个人史：</strong>{{ activeRecord.personal_history || '-' }}</p>
                <p><strong>家族史：</strong>{{ activeRecord.family_history || '-' }}</p>
                <p><strong>辅助检查：</strong>{{ activeRecord.auxiliary_exam || '-' }}</p>
                <p><strong>初步诊断：</strong>{{ activeRecord.diagnosis || '-' }}</p>
                <p><strong>治疗意见：</strong>{{ activeRecord.treatment_plan || '-' }}</p>
                <p><strong>备注：</strong>{{ activeRecord.remark || '无' }}</p>
                <p><strong>医嘱：</strong><el-tag v-if="activeRecord.doctor_advice" type="primary" size="small">{{ activeRecord.doctor_advice }}</el-tag><span v-else>-</span></p>
              </div>
              <div class="section-title">处方信息</div>
              <div v-if="activeRecord.prescriptions?.length" class="rx-list">
                <div v-for="(rx, ridx) in activeRecord.prescriptions" :key="ridx" class="rx-block">
                  <div class="rx-title">{{ rx.type === 'western' ? '西药处方' : rx.type === 'chinese' ? '中药处方' : '处方' }}</div>
                  <p v-for="(item, idx) in rx.items" :key="idx">{{ idx + 1 }} {{ item.drug_name }} {{ item.specification }} {{ item.usage }}</p>
                </div>
              </div>
              <div v-else class="empty-tip">暂无处方信息</div>
            </div>
            <div v-else class="empty-tip">请选择左侧病历查看详情</div>
          </el-col>
        </el-row>
      </div>

      <div v-else-if="activeTab === 'charges'" class="pane-scroll">
        <div class="total-bar">消费总计金额：<span class="amount">{{ totalCharge.toFixed(2) }}元</span></div>
        <div class="section-title">消费明细</div>
        <el-table :data="charges" border stripe v-loading="chargesLoading" class="charge-table" header-cell-class-name="charge-header" style="width: 100%">
          <el-table-column type="index" label="序号" width="55" align="center" />
          <el-table-column prop="created_at" label="收费/退费时间" width="170" />
          <el-table-column prop="status" label="收费状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="billStatusType(row.status)">{{ billStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="bill_type" label="收费类型" min-width="120">
            <template #default="{ row }">{{ billTypeText(row.bill_type) }}</template>
          </el-table-column>
          <el-table-column prop="total_amount" label="应收金额" width="120" align="right">
            <template #default="{ row }"><span class="money">{{ Number(row.total_amount || 0).toFixed(2) }}</span></template>
          </el-table-column>
          <el-table-column prop="paid_amount" label="实收金额" width="120" align="right">
            <template #default="{ row }"><span class="money">{{ Number(row.paid_amount || 0).toFixed(2) }}</span></template>
          </el-table-column>
          <el-table-column prop="payment_method" label="支付方式" min-width="120" align="center">
            <template #default="{ row }">{{ payMethodText(row.payment_method) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button v-if="row.status === 'unpaid'" type="primary" link @click="onPay(row)">收费</el-button>
              <el-button v-else type="primary" link @click="onView(row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      </div>
    </el-card>

    <FamilyDialog v-model="showFamily" :editing="familyEditing" @confirm="onFamilyConfirm" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentChecked, Back, Plus, Edit, Printer } from '@element-plus/icons-vue'
import { getPatient, updatePatient, getMemberLevels, getFamilyMembers, createFamilyMember, updateFamilyMember, deleteFamilyMember } from '@/api/patient'
import { getMedicalRecords } from '@/api/treatment'
import { getBills } from '@/api/payment'
import FamilyDialog from './family.vue'

defineOptions({ name: 'PatientEdit' })

const route = useRoute()
const router = useRouter()
const patientId = route.params.id
const activeTab = ref('info')
const saving = ref(false)
const levelOptions = ref([])
const form = reactive({
  name: '', cardNo: '', age: '', birthday: '', gender: '男', phone: '', idCard: '',
  member_level_id: '', address: '', remark: ''
})
const familyList = ref([])
const familyLoading = ref(false)
const showFamily = ref(false)
const familyEditing = ref(null)

const records = ref([])
const recordsLoading = ref(false)
const activeRecordIndex = ref(0)
const activeRecord = computed(() => records.value[activeRecordIndex.value] || null)

const charges = ref([])
const chargesLoading = ref(false)
const totalCharge = computed(() => charges.value.reduce((sum, row) => sum + Number(row.paid_amount || 0), 0))

function formatBirthday(val) {
  if (!val) return null
  const d = val instanceof Date ? val : new Date(val)
  if (isNaN(d.getTime())) return val
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
function calcAge(birthday) {
  if (!birthday) return ''
  const d = new Date(birthday)
  if (isNaN(d.getTime())) return ''
  const now = new Date()
  let age = now.getFullYear() - d.getFullYear()
  const m = now.getMonth() - d.getMonth()
  if (m < 0 || (m === 0 && now.getDate() < d.getDate())) age--
  return String(age)
}
function onBirthdayChange(val) {
  form.age = calcAge(val)
}
function genderToBackend(v) {
  return v === '女' ? 'female' : 'male'
}
function genderToFront(v) {
  return v === 'female' ? '女' : '男'
}
function formatGender(v) {
  if (v === 'female' || v === '女') return '女'
  if (v === 'male' || v === '男') return '男'
  return v || '-'
}

async function loadDetail() {
  try {
    const data = await getPatient(patientId)
    form.name = data.name || ''
    form.cardNo = data.patient_no || ''
    form.birthday = data.birthday ? data.birthday.toString().slice(0, 10) : ''
    form.age = calcAge(form.birthday)
    form.gender = genderToFront(data.gender)
    form.phone = data.phone || ''
    form.idCard = data.id_card || ''
    form.member_level_id = data.member_level_id || ''
    form.address = data.address || ''
    form.remark = data.remark || ''
  } catch (e) {
    ElMessage.error('加载患者详情失败')
  }
}

async function onSave() {
  if (!form.name) {
    ElMessage.warning('请填写患者姓名')
    return
  }
  if (!form.idCard) {
    ElMessage.warning('请填写证件号码')
    return
  }
  if (!/^(\d{15}|\d{17}[\dXx])$/.test(form.idCard)) {
    ElMessage.warning('证件号码格式不正确（15 或 18 位）')
    return
  }
  saving.value = true
  const payload = {
    name: form.name,
    patient_no: form.cardNo || undefined,
    gender: genderToBackend(form.gender),
    birthday: formatBirthday(form.birthday),
    age: form.age !== '' ? Number(form.age) : undefined,
    phone: form.phone || undefined,
    id_card: form.idCard,
    address: form.address || undefined,
    remark: form.remark || undefined,
    member_level_id: form.member_level_id || null
  }
  try {
    await updatePatient(patientId, payload)
    ElMessage.success('保存成功')
    router.push('/patients')
  } catch (e) {
    const detail = e && e.response && e.response.data && e.response.data.detail
    ElMessage.error((Array.isArray(detail) ? detail[0].msg : detail) || '保存失败')
  } finally {
    saving.value = false
  }
}
const onBack = () => router.back()

async function loadFamilyMembers() {
  if (!patientId) return
  familyLoading.value = true
  try {
    const res = await getFamilyMembers(patientId)
    familyList.value = res.items || []
  } catch (e) {
    ElMessage.error('加载家庭成员失败')
  } finally {
    familyLoading.value = false
  }
}

function openFamilyDialog(row = null) {
  familyEditing.value = row
  showFamily.value = true
}

async function onFamilyConfirm(data) {
  if (!patientId) return
  try {
    if (data.id) {
      await updateFamilyMember(patientId, data.id, data)
      ElMessage.success('更新家庭成员成功')
    } else {
      await createFamilyMember(patientId, data)
      ElMessage.success('添加家庭成员成功')
    }
    await loadFamilyMembers()
  } catch (e) {
    ElMessage.error(e?.response?.data?.msg || '操作失败')
  }
}

async function removeFamily(row) {
  if (!row?.id) return
  try {
    await ElMessageBox.confirm('确定取消该家庭成员关联吗？', '提示', { type: 'warning' })
    await deleteFamilyMember(patientId, row.id)
    ElMessage.success('取消关联成功')
    await loadFamilyMembers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.msg || '取消关联失败')
    }
  }
}

async function loadRecords() {
  if (!patientId) return
  recordsLoading.value = true
  try {
    const res = await getMedicalRecords({ patient_id: patientId, page: 1, page_size: 100 })
    records.value = res.items || []
    activeRecordIndex.value = 0
  } catch (e) {
    ElMessage.error('加载电子病历失败')
  } finally {
    recordsLoading.value = false
  }
}

async function loadCharges() {
  if (!patientId) return
  chargesLoading.value = true
  try {
    const res = await getBills({ patient_id: patientId, page: 1, page_size: 100 })
    charges.value = res.items || []
  } catch (e) {
    ElMessage.error('加载收费记录失败')
  } finally {
    chargesLoading.value = false
  }
}

function billStatusText(status) {
  const map = { unpaid: '未收费', paid: '已收费', partial: '部分收费', refunded: '已退费', cancelled: '已取消' }
  return map[status] || status || '-'
}
function billStatusType(status) {
  const map = { unpaid: 'warning', paid: 'success', partial: '', refunded: 'danger', cancelled: 'info' }
  return map[status] || ''
}
function billTypeText(type) {
  const map = {
    registration: '挂号费',
    treatment: '诊疗费',
    prescription: '处方费',
    drug: '药品费',
    inspection: '检查费',
    test: '检验费',
    other: '其他',
    retail: '药品零售'
  }
  return map[type] || type || '-'
}
function payMethodText(method) {
  const map = {
    cash: '现金',
    wechat: '微信',
    alipay: '支付宝',
    card: '银行卡',
    insurance: '医保',
    balance: '余额',
    other: '其他'
  }
  return map[method] || method || '-'
}
const onPay = (row) => router.push(`/charge/detail/${row.id}?mode=pay`)
const onView = (row) => router.push(`/charge/detail/${row.id}`)

watch(activeTab, (tab) => {
  if (tab === 'records' && !records.value.length) loadRecords()
  if (tab === 'charges' && !charges.value.length) loadCharges()
})

onMounted(async () => {
  try {
    const res = await getMemberLevels({ page: 1, page_size: 100 })
    levelOptions.value = res.items || []
  } catch (e) { /* 等级非强依赖 */ }
  if (patientId) {
    await loadDetail()
    await loadFamilyMembers()
  }
})
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，页签/操作固定，面板内容内部滚动 */
.patient-edit-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
.page-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
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
  .patient-tabs { flex: 1; min-width: 0; }
  .head-actions { display: flex; gap: 10px; flex-shrink: 0; }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.pane-scroll {
  flex: 1;
  min-height: 0;
  overflow: auto;
}
.patient-tabs { margin-bottom: 0; }
.patient-tabs :deep(.el-tabs__header) { margin-bottom: 0; border-bottom: 1px solid #e4e7ed; }
.patient-tabs :deep(.el-tabs__nav-wrap::after) { height: 1px; background-color: #e4e7ed; }
.patient-tabs :deep(.el-tabs__item) { color: #606266; font-weight: 500; }
.patient-tabs :deep(.el-tabs__item.is-active) { color: #5b7cff; }
.patient-tabs :deep(.el-tabs__active-bar) { background-color: #5b7cff; }
.section-title { font-size: 16px; font-weight: 600; color: #5b7cff; margin: 16px 0; padding-left: 12px; border-left: 4px solid #5b7cff; display: flex; align-items: center; justify-content: space-between; }
.section-title .fr { float: none; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin: 16px 0; }
.patient-form :deep(.el-form-item__label) { color: #606266; }
.fr { float: right; }
.record-layout { min-height: 500px; }
.timeline { padding-left: 10px; }
.timeline-item { position: relative; padding-left: 16px; border-left: 2px solid #dcdfe6; margin-bottom: 16px; cursor: pointer; }
.timeline-item.active { border-left-color: #5b7cff; }
.timeline-item .time { font-size: 13px; color: #909399; margin-bottom: 6px; }
.timeline-item .card { background: #f5f7fa; padding: 10px; border-radius: 6px; font-size: 13px; color: #606266; line-height: 1.8; }
.record-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.record-text { font-size: 14px; line-height: 2; color: #303133; }
.rx-title { font-size: 14px; color: #5b7cff; margin-bottom: 8px; }
.rx-list { font-size: 13px; line-height: 2; color: #606266; }
.rx-block { margin-bottom: 12px; }
.total-bar { padding: 12px 16px; background: #f7f8ff; border-radius: 6px; font-size: 15px; margin-bottom: 16px; }
.total-bar .amount { color: #f56c6c; font-weight: 600; }
.money { font-family: 'Microsoft YaHei', sans-serif; font-weight: 500; }
.charge-table { border-radius: 6px; overflow: hidden; }
.charge-table :deep(.charge-header) { background-color: #e8eeff !important; color: #303133; font-weight: 600; }
.charge-table :deep(.el-table__header-wrapper th) { background-color: #e8eeff !important; }
.empty-tip { padding: 40px 0; text-align: center; color: #909399; font-size: 14px; }
.text-warning { color: #e6a23c; }
.text-success { color: #67c23a; }
.text-danger { color: #f56c6c; }
</style>

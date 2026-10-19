<template>
  <div class="reg-create-page">
    <div class="page-head">
      <div class="page-title"><span class="title-bar" />新增挂号</div>
      <el-button :icon="Money" type="warning" plain @click="onCharge">收费</el-button>
    </div>

    <!-- 挂号信息 -->
    <el-card class="info-card" shadow="never">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="84px" v-loading="loading">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="挂号单号">
              <el-input v-model="form.reg_no" disabled placeholder="保存后自动生成" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="科室" prop="department_id">
              <el-select v-model="form.department_id" placeholder="请选择" filterable style="width: 100%" @change="onDeptChange">
                <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="接诊类型" prop="visit_type">
              <el-select v-model="form.visit_type" placeholder="请选择" style="width: 100%">
                <el-option label="初诊" value="first" />
                <el-option label="复诊" value="followup" />
                <el-option label="转诊" value="referral" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="接诊医生" prop="doctor_id">
              <el-select v-model="form.doctor_id" placeholder="请选择" filterable :disabled="!form.department_id" style="width: 100%">
                <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="挂号费" prop="registration_fee_id">
              <el-select v-model="form.registration_fee_id" placeholder="请选择" style="width: 100%" @change="onFeeChange">
                <el-option v-for="f in registrationFeeOptions" :key="f.id" :label="`${f.name} ¥${Number(f.amount).toFixed(2)}`" :value="f.id" />
                <template #empty>
                  <div class="select-empty">请先在「设置 - 费用设置 - 挂号费」中添加费用项</div>
                </template>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="诊疗费">
              <el-select v-model="form.treatment_fee_id" placeholder="请选择" clearable style="width: 100%">
                <el-option v-for="f in treatmentFeeOptions" :key="f.id" :label="`${f.name} ¥${Number(f.amount).toFixed(2)}`" :value="f.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="挂号日期" prop="registration_date">
              <el-date-picker v-model="form.registration_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="挂号员">
              <el-input v-model="form.operator_name" disabled />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 患者信息 -->
    <div class="section-title">患者信息</div>
    <el-card class="patient-card" shadow="never">
      <el-form :model="form" label-width="84px">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="患者姓名" required>
              <el-autocomplete
                v-model="form.patient_name"
                :fetch-suggestions="searchPatients"
                placeholder="患者姓名/手机号码/证件号码/卡号"
                value-key="name"
                style="width: 100%"
                @select="onPatientPick"
              >
                <template #suffix>
                  <el-icon class="search-icon" @click="onAddPatient"><Search /></el-icon>
                </template>
                <template #default="{ item }">
                  <div class="patient-suggest">
                    <span>{{ item.name }}</span>
                    <span class="patient-suggest-no">{{ item.patient_no }}</span>
                  </div>
                </template>
              </el-autocomplete>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者卡号">
              <el-input v-model="form.patient_no" placeholder="请输入病人卡号" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者年龄">
              <el-input v-model="form.age" placeholder="请输入数字">
                <template #append>
                  <el-select v-model="form.age_unit" style="width: 90px">
                    <el-option label="岁" value="year" />
                    <el-option label="月" value="month" />
                    <el-option label="天" value="day" />
                  </el-select>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="出生日期" required>
              <el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" @change="onBirthdayChange" />
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="性别" required>
              <el-select v-model="form.gender" placeholder="请选择" style="width: 100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="手机号码">
              <el-input v-model="form.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="证件号码">
              <el-input v-model="form.id_card" placeholder="请输入证件号码" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="地址">
              <el-cascader
                v-model="region"
                :options="regionOptions"
                placeholder="广东省/深圳市"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="18">
            <el-form-item label=" " label-width="84px">
              <el-input v-model="form.address" placeholder="请输入详细地址" />
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-form-item label="备注" label-width="84px">
              <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="选填" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <div class="footer-bar">
      <el-button :icon="Back" @click="onBack">取消</el-button>
      <el-button type="primary" :loading="submitting" :icon="Check" @click="onSubmit">确认挂号</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Check, Money, Search } from '@element-plus/icons-vue'
import { createRegistration } from '@/api/registration'
import { getDepartments } from '@/api/department'
import { getDoctors } from '@/api/doctor'
// 注意：本地自动补全回调也叫 searchPatients，故此处用别名避免重名
import { searchPatients as searchPatientApi } from '@/api/patient'
import { fetchAllPages } from '@/utils/paging'
import { getFees } from '@/api/fee'
import { useUserStore } from '@/store/modules/user'

defineOptions({ name: 'RegistrationCreate' })

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const departments = ref([])
const doctors = ref([])
// 挂号费 / 诊疗费均取自「设置 - 费用设置」
const registrationFeeOptions = ref([])
const treatmentFeeOptions = ref([])

const regionOptions = [
  { value: 'gd', label: '广东省', children: [{ value: 'sz', label: '深圳市' }] },
]
const region = ref([])

const today = new Date().toISOString().slice(0, 10)

const form = reactive({
  reg_no: generateRegNo(),
  patient_id: '',
  patient_name: '',
  patient_no: '',
  gender: '',
  birthday: '',
  age: '',
  age_unit: 'year',
  phone: '',
  id_card: '',
  address: '',
  department_id: '',
  doctor_id: '',
  visit_type: 'first',
  registration_fee_id: '',
  registration_fee: 0,
  treatment_fee_id: '',
  registration_date: today,
  operator_name: userStore.userName || '',
  price: 0,
  payment_status: 'unpaid',
  notes: '',
})

const rules = {
  department_id: [{ required: true, message: '请选择科室', trigger: 'change' }],
  doctor_id: [{ required: true, message: '请选择医生', trigger: 'change' }],
  visit_type: [{ required: true, message: '请选择接诊类型', trigger: 'change' }],
  registration_fee_id: [{ required: true, message: '请选择挂号费', trigger: 'change' }],
  registration_date: [{ required: true, message: '请选择挂号日期', trigger: 'change' }],
  patient_name: [{ required: true, message: '请选择或输入患者姓名', trigger: 'change' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  birthday: [{ required: true, message: '请选择出生日期', trigger: 'change' }],
}

// 挂号单号（前端生成；保存成功后由后端返回真实单号覆盖）
function generateRegNo() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  const stamp = `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`
  const rand = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  return `${stamp}${rand}`
}

// 远程搜索患者（el-autocomplete fetch-suggestions）
const searchPatients = async (keyword, cb) => {
  if (!keyword) { cb([]); return }
  try {
    const res = await searchPatientApi(keyword, 20)
    cb(res.items || [])
  } catch {
    cb([])
  }
}

// 选中自动补全项：填充患者信息
const onPatientPick = (item) => {
  form.patient_id = item.id
  form.patient_name = item.name
  form.patient_no = item.patient_no || ''
  form.gender = item.gender || ''
  form.birthday = item.birthday || ''
  form.age = computeAge(item.birthday)
  form.phone = item.phone || ''
  form.id_card = item.id_card || ''
  form.address = item.address || ''
}

// 根据生日计算年龄（周岁）
function computeAge(birthday) {
  if (!birthday) return ''
  const b = new Date(birthday)
  const now = new Date()
  let age = now.getFullYear() - b.getFullYear()
  const m = now.getMonth() - b.getMonth()
  if (m < 0 || (m === 0 && now.getDate() < b.getDate())) age--
  return age >= 0 ? age : ''
}

// 出生日期变化时自动计算年龄
const onBirthdayChange = (val) => {
  if (val) form.age = computeAge(val)
}

// 跳到新增患者页
const onAddPatient = () => router.push('/patients/create')

const onDeptChange = () => { form.doctor_id = '' }

// 选中挂号费项后，带出金额作为应收金额
const onFeeChange = (id) => {
  const fee = registrationFeeOptions.value.find(f => f.id === id)
  const amount = Number(fee?.amount) || 0
  form.registration_fee = amount
  form.price = amount
}

const onCharge = () => ElMessage.info('请先保存挂号后再进行收费')

async function fetchOptions() {
  loading.value = true
  try {
    const [d, doc, rf, tf] = await Promise.all([
      getDepartments({ page_size: 100 }),
      getDoctors({ page_size: 100 }),
      fetchAllPages(p => getFees({ fee_type: 'registration', ...p })),
      fetchAllPages(p => getFees({ fee_type: 'treatment', ...p })),
    ])
    departments.value = d.items || []
    doctors.value = doc.items || []
    // 仅展示启用中的费用项
    registrationFeeOptions.value = (rf || []).filter(f => f.status !== false)
    treatmentFeeOptions.value = (tf || []).filter(f => f.status !== false)
  } catch { /* ignore */ }
  finally { loading.value = false }
}

const onSubmit = async () => {
  try { await formRef.value.validate() }
  catch { return }
  if (!form.patient_id) {
    ElMessage.warning('请先从搜索中选择已有患者；如为新患者请先到「患者管理」创建')
    return
  }
  submitting.value = true
  try {
    await createRegistration({
      patient_id: form.patient_id,
      patient_name: form.patient_name,
      patient_no: form.patient_no,
      department_id: form.department_id,
      doctor_id: form.doctor_id,
      registration_type: 'normal',
      registration_fee: form.registration_fee,
      registration_date: form.registration_date,
      time_period: 'morning',
      price: form.price,
      status: 'pending',
      payment_status: 'unpaid',
      notes: form.notes,
    })
    ElMessage.success('挂号成功')
    router.push('/registration')
  } catch (e) {
    ElMessage.error(e?.message || '挂号失败')
  } finally {
    submitting.value = false
  }
}

const onBack = () => router.back()

onMounted(fetchOptions)
</script>

<style lang="scss" scoped>
.reg-create-page { background: #f5f7fa; padding: 12px 16px 80px; min-height: 100vh; box-sizing: border-box; }
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-bar {
  display: inline-block;
  width: 4px;
  height: 16px;
  background: #5b7cff;
  border-radius: 2px;
}
.info-card {
  border-radius: 8px;
  background: #f4f0ff;
  border: none;
  margin-bottom: 16px;
  :deep(.el-card__body) { padding: 20px 20px 4px; }
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #5b7cff;
  margin: 4px 0 12px;
}
.patient-card {
  border-radius: 8px;
  :deep(.el-card__body) { padding: 20px 20px 4px; }
}
.footer-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: #fff;
  padding: 12px 16px;
  text-align: center;
  border-top: 1px solid #ebeef5;
  z-index: 10;
}
.search-icon {
  cursor: pointer;
  color: #909399;
  &:hover { color: #5b7cff; }
}
.patient-suggest {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.patient-suggest-no {
  color: #909399;
  font-size: 12px;
}
.select-empty {
  padding: 8px 12px;
  color: #909399;
  font-size: 12px;
  text-align: center;
}
</style>
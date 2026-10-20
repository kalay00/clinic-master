<template>
  <div class="record-page">
    <!-- 顶部：病历 / 处方（先填病历，保存后切换到处方） -->
    <el-tabs v-model="topTab" class="consult-top-tabs" @tab-change="onTopTabChange">
      <el-tab-pane label="病历" name="record" />
      <el-tab-pane label="处方" name="western" />
    </el-tabs>

    <!-- 患者信息 -->
    <el-card class="patient-card" shadow="never">
      <el-form :model="patient" label-width="80px" class="patient-form">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="患者姓名" required>
              <el-input v-model="patient.name" placeholder="患者姓名/手机号/证件号/卡号">
                <template #append>
                  <el-button :icon="Search" @click="onSearchPatient" />
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者卡号">
              <el-input v-model="patient.cardNo" placeholder="请输入病人卡号" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者年龄" required>
              <el-input v-model="patient.age" placeholder="请输入数字">
                <template #append>岁</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="出生日期" required>
              <el-date-picker v-model="patient.birthday" type="date" placeholder="请选择" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="性别" required>
              <el-select v-model="patient.gender" placeholder="请选择" style="width: 100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="手机号码">
              <el-input v-model="patient.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="证件号码">
              <el-input v-model="patient.idCard" placeholder="请输入证件号码" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="接诊类型" required>
              <el-select v-model="patient.visitType" placeholder="请选择" style="width: 100%">
                <el-option label="初诊" value="first" />
                <el-option label="复诊" value="return" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="地址">
              <el-cascader v-model="patient.region" :options="regionOptions" placeholder="请选择" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="18">
            <el-form-item label="详细地址">
              <el-input v-model="patient.address" placeholder="请输入详细地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="诊断" required>
              <el-input v-model="patient.diagnosis">
                <template #append>
                  <el-button :icon="Search" @click="onPickDiagnosis" />
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="医嘱">
              <el-input v-model="patient.advice">
                <template #append>
                  <el-button :icon="Search" @click="onPickAdvice" />
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 体格信息 -->
    <el-card class="physical-card" shadow="never">
      <div class="section-title">体格信息</div>
      <el-form :model="physical" label-width="56px" class="physical-form">
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="体温">
              <el-input v-model="physical.temperature" class="inline-input">
                <template #append>℃</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="呼吸">
              <el-input v-model="physical.breath" class="inline-input">
                <template #append>次/分</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="脉搏">
              <el-input v-model="physical.pulse" class="inline-input">
                <template #append>次/分</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="血压">
              <div class="blood-pressure">
                <el-input v-model="physical.bpSystolic" class="inline-input" />
                <span class="bp-split">/</span>
                <el-input v-model="physical.bpDiastolic" class="inline-input" />
                <span class="bp-unit">mmHg</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="身高">
              <el-input v-model="physical.height" class="inline-input">
                <template #append>cm</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="体重">
              <el-input v-model="physical.weight" class="inline-input">
                <template #append>Kg</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="血糖">
              <el-input v-model="physical.bloodSugar" class="inline-input">
                <template #append>mmol/l</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="血脂">
              <el-input v-model="physical.bloodFat" class="inline-input">
                <template #append>mmol/l</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 病历信息 -->
    <el-card class="record-info-card" shadow="never">
      <div class="section-title">病历信息<span class="section-tip">（病历信息可在系统设置-基础设置中的自定义设置）</span></div>
      <el-form :model="record" label-width="80px" class="record-form">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="发病日期">
              <el-date-picker v-model="record.onsetDate" type="date" placeholder="请选择" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="主诉" required>
              <el-input v-model="record.chiefComplaint">
                <template #append>
                  <el-button :icon="Search" @click="onPickComplaint" />
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="现病史">
              <el-input v-model="record.presentIllness" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="既往史">
              <el-input v-model="record.pastHistory" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="过敏史">
              <el-input v-model="record.allergyHistory" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="个人史">
              <el-input v-model="record.personalHistory" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="家族史">
              <el-input v-model="record.familyHistory" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="辅助检查">
              <el-input v-model="record.auxiliaryExam" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="治疗意见">
              <el-input v-model="record.treatmentOpinion" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注">
              <el-input v-model="record.remark" type="textarea" :rows="3" placeholder="请输入" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 底部操作栏 -->
    <div class="bottom-bar">
      <div class="bottom-bar-left">
        <span class="footer-label">接诊医生：</span>
        <el-select v-model="doctorId" placeholder="请选择接诊医生" size="small" style="width: 160px">
          <el-option
            v-for="d in doctors"
            :key="d.id"
            :label="d.name + (d.title ? `（${d.title}）` : '')"
            :value="d.id"
          />
        </el-select>
      </div>
      <div class="bottom-bar-actions">
        <el-button :icon="Document" @click="goTemplateCall">病历调</el-button>
        <el-button :icon="Printer" @click="printRecord">打印病历</el-button>
        <el-button :icon="Files" @click="goTemplateCreate">存为模板</el-button>
        <el-button type="primary" :icon="Check" @click="onSave">保存</el-button>
        <el-button type="warning" :icon="SwitchButton" @click="goEnd">结束就诊</el-button>
      </div>
    </div>

    <!-- 弹窗 -->
    <RecordTemplateCall v-model="showRecordTemplateCall" @confirm="onRecordTemplateConfirm" />
    <RecordTemplateCreate v-model="showRecordTemplateCreate" />
    <RecordInfoCall v-model="showRecordInfo" @confirm="onRecordInfoConfirm" />
    <ChargeConfirm v-model="showChargeConfirm" @confirm="onChargeConfirm" />

    <!-- 患者查询弹窗：直接就诊（无挂号单）时查询并回填患者信息 -->
    <el-dialog v-model="showPatientSearch" title="查询患者" width="760px" append-to-body>
      <div class="patient-search-bar">
        <el-input
          v-model="patientKeyword"
          placeholder="姓名 / 手机号 / 证件号 / 档案号"
          clearable
          style="width: 280px"
          @keyup.enter="onPatientSearch"
        />
        <el-button type="primary" :icon="Search" @click="onPatientSearch">查询</el-button>
        <span class="patient-search-tip">点击表格行即选中并回填患者信息</span>
      </div>
      <el-table :data="patientResults" border height="380" v-loading="patientSearching" @row-click="onPickPatient">
        <el-table-column prop="patient_no" label="档案号" width="130" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="性别" width="70">
          <template #default="{ row }">{{ row.gender === 'male' || row.gender === 'M' || row.gender === '男' ? '男' : row.gender === 'female' || row.gender === 'F' || row.gender === '女' ? '女' : '-' }}</template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="id_card" label="证件号" min-width="170" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search, Document, Printer, Files, Check, SwitchButton,
} from '@element-plus/icons-vue'
import RecordTemplateCall from '@/views/consultation/record-template-call.vue'
import RecordTemplateCreate from '@/views/consultation/record-template-create.vue'
import RecordInfoCall from '@/views/consultation/record-info-call.vue'
import ChargeConfirm from '@/views/consultation/charge-confirm.vue'
import { getRegistration } from '@/api/registration'
import { getPatient, getPatients, getPatientVisits } from '@/api/patient'
import { getDoctors } from '@/api/doctor'
import { createMedicalRecord } from '@/api/treatment'

defineOptions({ name: 'ConsultationRecord' })

const router = useRouter()
const route = useRoute()

const regId = computed(() => route.query.regId || '')
const patientId = ref('')
const registrationId = ref('')
// 接诊医生（保存病历必填）
const doctorId = ref('')
const doctors = ref([])

const loadDoctors = async () => {
  try {
    const res = await getDoctors({ page: 1, page_size: 100 })
    doctors.value = res.items || []
  } catch (e) { /* 医生列表加载失败不影响表单填写 */ }
}

// 根据出生日期计算年龄
const calcAge = (birthday) => {
  if (!birthday) return ''
  const b = new Date(birthday)
  if (Number.isNaN(b.getTime())) return ''
  const now = new Date()
  let age = now.getFullYear() - b.getFullYear()
  const m = now.getMonth() - b.getMonth()
  if (m < 0 || (m === 0 && now.getDate() < b.getDate())) age -= 1
  return age >= 0 && age < 150 ? String(age) : ''
}

// 性别归一化：兼容 male/female、M/F、男/女
const normalizeGender = (g) => {
  if (!g) return ''
  if (g === 'male' || g === '男' || g === 'M') return 'male'
  if (g === 'female' || g === '女' || g === 'F') return 'female'
  return g
}

// 患者信息回填（挂号带入 / 弹窗查询共用）
const applyPatientToForm = (p) => {
  if (!p) return
  patient.name = p.name || patient.name
  patient.cardNo = p.patient_no || patient.cardNo
  patient.phone = p.phone || patient.phone
  patient.gender = normalizeGender(p.gender) || patient.gender
  const birthday = p.birth_date || (p.birthday ? String(p.birthday).slice(0, 10) : '')
  patient.birthday = birthday || patient.birthday
  patient.idCard = p.id_card || patient.idCard
  patient.address = p.address || patient.address
  if (p.age != null && p.age !== '') patient.age = String(p.age)
  else if (!patient.age && patient.birthday) patient.age = calcAge(patient.birthday)
}

// 按患者ID补全详情，并按就诊历史推断初/复诊
const fillPatientById = async (id, fallback = {}) => {
  if (!id) return
  try {
    const detail = await getPatient(id)
    applyPatientToForm({ ...fallback, ...(detail || {}) })
  } catch (e) { applyPatientToForm(fallback) }
  try {
    const visits = await getPatientVisits(id)
    const list = Array.isArray(visits) ? visits : (visits?.items || [])
    patient.visitType = list.length > 0 ? 'return' : 'first'
  } catch (e) { /* 就诊历史不可得时不改接诊类型 */ }
}

// 跨页保留就诊上下文（挂号单 / 患者），病历 ↔ 处方互跳不丢信息
const consultationQuery = () => {
  const q = {}
  if (regId.value) q.regId = regId.value
  if (patientId.value) q.patientId = patientId.value
  return q
}

onMounted(async () => {
  await loadDoctors()
  if (regId.value) {
    try {
      const reg = await getRegistration(regId.value)
      registrationId.value = reg.id || regId.value
      patientId.value = reg.patient_id || ''
      // 挂号单上的医生作为默认接诊医生
      if (reg.doctor_id) doctorId.value = reg.doctor_id
      await fillPatientById(patientId.value, {
        name: reg.patient_name,
        patient_no: reg.patient_no,
        phone: reg.patient_phone,
      })
    } catch (e) { /* 忽略：直接就诊时走患者查询 */ }
  } else if (route.query.patientId) {
    // 从处方页切回时按患者ID恢复
    patientId.value = route.query.patientId
    await fillPatientById(patientId.value)
  }
})

// 患者查询弹窗（直接就诊时选择患者）
const showPatientSearch = ref(false)
const patientKeyword = ref('')
const patientResults = ref([])
const patientSearching = ref(false)

const onPatientSearch = async () => {
  patientSearching.value = true
  try {
    const res = await getPatients({ keyword: patientKeyword.value.trim() || undefined, page: 1, page_size: 20 })
    patientResults.value = res.items || []
  } catch (e) {
    ElMessage.error('患者查询失败')
  } finally {
    patientSearching.value = false
  }
}

const onPickPatient = async (row) => {
  patientId.value = row.id
  await fillPatientById(row.id, row)
  showPatientSearch.value = false
  ElMessage.success(`已选择患者：${row.name || ''}`)
}

const onSearchPatient = () => {
  showPatientSearch.value = true
  if (!patientResults.value.length) onPatientSearch()
}

// 弹窗显隐
const showRecordTemplateCall = ref(false)
const showRecordTemplateCreate = ref(false)
const showRecordInfo = ref(false)
const showChargeConfirm = ref(false)

// 顶部 Tab
const topTab = ref('record')
const onTopTabChange = (name) => {
  // 病历保存后（或手动切换到处方）携带挂号/患者上下文
  if (name === 'western') router.push({ path: '/consultation/western', query: consultationQuery() })
}

// 患者信息
const patient = reactive({
  name: '', cardNo: '', age: '', birthday: '', gender: '', phone: '',
  idCard: '', visitType: '', region: [], address: '', diagnosis: '', advice: '',
})
const regionOptions = [
  { value: 'gd', label: '广东省', children: [{ value: 'sz', label: '深圳市' }] },
]

// 体格信息
const physical = reactive({
  temperature: '', breath: '', pulse: '', bpSystolic: '', bpDiastolic: '',
  height: '', weight: '', bloodSugar: '', bloodFat: '',
})

// 病历信息
const record = reactive({
  onsetDate: '', chiefComplaint: '', presentIllness: '', pastHistory: '',
  allergyHistory: '', personalHistory: '', familyHistory: '', auxiliaryExam: '',
  treatmentOpinion: '', remark: '',
})

// 底部按钮
const goTemplateCall = () => { showRecordTemplateCall.value = true }
const goTemplateCreate = () => { showRecordTemplateCreate.value = true }
const goEnd = () => { showChargeConfirm.value = true }

const onPickDiagnosis = () => ElMessage.info('打开诊断选择')
const onPickAdvice = () => ElMessage.info('打开医嘱选择')
const onPickComplaint = () => ElMessage.info('打开主诉选择')

const printRecord = () => {
  ElMessage.info('调用浏览器打印')
  window.print()
}
const onSave = async () => {
  if (!patientId.value) {
    ElMessage.warning('请先选择就诊患者')
    return
  }
  if (!doctorId.value) {
    ElMessage.warning('请先选择接诊医生')
    return
  }
  if (!registrationId.value) {
    ElMessage.warning('该患者未挂号，请先在挂号记录中挂号后再保存病历')
    return
  }
  // 过敏史/个人史/家族史/辅助检查/治疗意见暂无独立字段，合并到备注避免丢失
  const extraParts = [
    record.allergyHistory && `过敏史：${record.allergyHistory}`,
    record.personalHistory && `个人史：${record.personalHistory}`,
    record.familyHistory && `家族史：${record.familyHistory}`,
    record.auxiliaryExam && `辅助检查：${record.auxiliaryExam}`,
    record.treatmentOpinion && `治疗意见：${record.treatmentOpinion}`,
  ].filter(Boolean)
  try {
    await createMedicalRecord({
      registration_id: registrationId.value,
      patient_id: patientId.value,
      doctor_id: doctorId.value,
      chief_complaint: record.chiefComplaint,
      present_illness: record.presentIllness,
      past_history: record.pastHistory,
      physical_examination: `体温${physical.temperature || ''} 呼吸${physical.breath || ''} 脉搏${physical.pulse || ''} 血压${physical.bpSystolic || ''}/${physical.bpDiastolic || ''} 身高${physical.height || ''} 体重${physical.weight || ''}`,
      diagnosis: patient.diagnosis,
      treatment_plan: patient.advice || record.treatmentOpinion || '',
      remark: [record.remark, ...extraParts].filter(Boolean).join('；'),
    })
    ElMessage.success('病历保存成功，请继续开处方')
    // 保存后切换到处方页，携带挂号/患者上下文
    router.push({ path: '/consultation/western', query: consultationQuery() })
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const onRecordTemplateConfirm = (tpl) => {
  record.diagnosis = tpl.diagnosis || record.diagnosis
  record.chiefComplaint = tpl.chiefComplaint || record.chiefComplaint
  record.presentIllness = tpl.presentIllness || record.presentIllness
  record.pastHistory = tpl.pastHistory || record.pastHistory
  record.allergyHistory = tpl.allergyHistory || record.allergyHistory
  record.personalHistory = tpl.personalHistory || record.personalHistory
  record.familyHistory = tpl.familyHistory || record.familyHistory
  record.auxiliaryExam = tpl.auxiliaryExam || record.auxiliaryExam
  record.treatmentOpinion = tpl.treatmentOpinion || record.treatmentOpinion
  record.advice = tpl.advice || record.advice
}
const onRecordInfoConfirm = (info) => {
  // 简单回填备注，便于演示
  record.remark = info.name
}
const onChargeConfirm = () => {}
</script>

<style lang="scss" scoped>
.record-page {
  background: #f5f7fa;
  padding: 12px 16px 80px;
}

.patient-card,
.physical-card,
.record-info-card {
  border-radius: 8px;
  margin-bottom: 12px;
}

.patient-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}

/* 患者查询弹窗 */
.patient-search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;

  .patient-search-tip {
    color: #909399;
    font-size: 12px;
  }
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #5b7cff;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #5b7cff;
}
.section-tip {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
  margin-left: 8px;
}

.physical-card {
  border: 1px solid #b0c2ff;
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.physical-form {
  :deep(.el-form-item) {
    margin-bottom: 12px;
  }
  :deep(.el-form-item__label) {
    padding-right: 8px;
  }
}

.inline-input {
  :deep(.el-input__wrapper) {
    padding-right: 0;
  }
}

.blood-pressure {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  .inline-input {
    flex: 1;
  }
  .bp-split {
    color: #606266;
  }
  .bp-unit {
    font-size: 13px;
    color: #909399;
    white-space: nowrap;
  }
}

.record-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}

.bottom-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12px 24px;
  background: #fff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
  z-index: 100;

  .bottom-bar-actions {
    display: flex;
    gap: 10px;
  }

  .footer-label {
    color: #606266;
    font-size: 13px;
  }
}
</style>

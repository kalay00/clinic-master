<template>
  <div class="record-page">
    <!-- 顶部：处方 / 病历 -->
    <el-tabs v-model="topTab" class="consult-top-tabs" @tab-change="onTopTabChange">
      <el-tab-pane label="处方" name="western" />
      <el-tab-pane label="病历" name="record" />
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
      <el-button :icon="Document" @click="goTemplateCall">病历调</el-button>
      <el-button :icon="Printer" @click="printRecord">打印病历</el-button>
      <el-button :icon="Files" @click="goTemplateCreate">存为模板</el-button>
      <el-button type="primary" :icon="Check" @click="onSave">保存</el-button>
      <el-button type="warning" :icon="SwitchButton" @click="goEnd">结束就诊</el-button>
    </div>

    <!-- 弹窗 -->
    <RecordTemplateCall v-model="showRecordTemplateCall" @confirm="onRecordTemplateConfirm" />
    <RecordTemplateCreate v-model="showRecordTemplateCreate" />
    <RecordInfoCall v-model="showRecordInfo" @confirm="onRecordInfoConfirm" />
    <ChargeConfirm v-model="showChargeConfirm" @confirm="onChargeConfirm" />
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
import { createMedicalRecord } from '@/api/treatment'

defineOptions({ name: 'ConsultationRecord' })

const router = useRouter()
const route = useRoute()

const regId = computed(() => route.query.regId || '')
const patientId = ref('')
const registrationId = ref('')

onMounted(async () => {
  if (regId.value) {
    try {
      const reg = await getRegistration(regId.value)
      registrationId.value = reg.id || regId.value
      patientId.value = reg.patient_id || ''
      patient.name = reg.patient_name || patient.name
      patient.cardNo = reg.patient_no || patient.cardNo
    } catch (e) { /* 忽略 */ }
  }
})

// 弹窗显隐
const showRecordTemplateCall = ref(false)
const showRecordTemplateCreate = ref(false)
const showRecordInfo = ref(false)
const showChargeConfirm = ref(false)

// 顶部 Tab
const topTab = ref('record')
const onTopTabChange = (name) => {
  if (name === 'western') router.push('/consultation/western')
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

const onSearchPatient = () => ElMessage.info('按条件查询患者')
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
  try {
    await createMedicalRecord({
      registration_id: registrationId.value,
      patient_id: patientId.value,
      chief_complaint: record.chiefComplaint,
      present_illness: record.presentIllness,
      past_history: record.pastHistory,
      allergy_history: record.allergyHistory,
      physical_exam: `体温${physical.temperature || ''} 呼吸${physical.breath || ''} 脉搏${physical.pulse || ''} 血压${physical.bpSystolic || ''}/${physical.bpDiastolic || ''} 身高${physical.height || ''} 体重${physical.weight || ''}`,
      diagnosis: patient.diagnosis,
      advice: patient.advice,
    })
    ElMessage.success('保存成功')
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
  justify-content: flex-end;
  gap: 10px;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12px 24px;
  background: #fff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
  z-index: 100;
}
</style>

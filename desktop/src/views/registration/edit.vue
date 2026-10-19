<template>
  <div class="reg-edit-page">
    <div class="page-head">
      <div class="page-title">编辑挂号</div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>

    <el-card class="page-card" shadow="never">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" v-loading="loading">
        <el-divider content-position="left">患者信息</el-divider>
        <el-form-item label="患者">
          <el-input :model-value="`${form.patient_name}（${form.patient_no}）`" disabled />
        </el-form-item>

        <el-divider content-position="left">挂号信息</el-divider>
        <el-form-item label="挂号科室" prop="department_id">
          <el-select v-model="form.department_id" filterable style="width: 320px" @change="onDeptChange">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="接诊医生" prop="doctor_id">
          <el-select v-model="form.doctor_id" filterable :disabled="!form.department_id" style="width: 320px">
            <el-option v-for="doc in doctors" :key="doc.id" :label="doc.name" :value="doc.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="挂号类型" prop="registration_type">
          <el-radio-group v-model="form.registration_type">
            <el-radio-button label="normal">普通号</el-radio-button>
            <el-radio-button label="expert">专家号</el-radio-button>
            <el-radio-button label="emergency">急诊号</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="号别" prop="registration_fee">
          <el-select v-model="form.registration_fee" style="width: 220px" @change="onFeeChange">
            <el-option v-for="fee in feeOptions" :key="fee.value" :label="fee.label" :value="fee.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="就诊日期" prop="registration_date">
          <el-date-picker v-model="form.registration_date" type="date" value-format="YYYY-MM-DD" style="width: 220px" />
        </el-form-item>
        <el-form-item label="时段" prop="time_period">
          <el-select v-model="form.time_period" style="width: 220px">
            <el-option label="上午" value="morning" />
            <el-option label="下午" value="afternoon" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" style="width: 460px" />
        </el-form-item>
      </el-form>
    </el-card>

    <div class="footer-bar">
      <el-button @click="onBack">取消</el-button>
      <el-button type="primary" :loading="submitting" :icon="Check" :disabled="form.status === 'completed' || form.status === 'cancelled'" @click="onSubmit">保存</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Check } from '@element-plus/icons-vue'
import { getRegistration, updateRegistration } from '@/api/registration'
import { getDepartments } from '@/api/department'
import { getDoctors } from '@/api/doctor'

defineOptions({ name: 'RegistrationEdit' })

const route = useRoute()
const router = useRouter()
const id = route.params.id
const loading = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const departments = ref([])
const doctors = ref([])
const feeOptions = [
  { value: 10, label: '普通号 ¥10' },
  { value: 20, label: '专家号 ¥20' },
  { value: 30, label: '急诊号 ¥30' }
]

const form = reactive({
  patient_name: '', patient_no: '',
  department_id: '', doctor_id: '',
  registration_type: 'normal', registration_fee: 10,
  registration_date: '', time_period: 'morning',
  price: 0, status: 'pending', notes: ''
})

const rules = {
  department_id: [{ required: true, message: '请选择科室', trigger: 'change' }],
  doctor_id: [{ required: true, message: '请选择医生', trigger: 'change' }],
  registration_fee: [{ required: true, message: '请选择号别', trigger: 'change' }],
  registration_date: [{ required: true, message: '请选择就诊日期', trigger: 'change' }],
  time_period: [{ required: true, message: '请选择时段', trigger: 'change' }],
}

async function fetchOptions() {
  try {
    const [d, doc] = await Promise.all([getDepartments({ page_size: 100 }), getDoctors({ page_size: 100 })])
    departments.value = d.items || []
    doctors.value = doc.items || []
  } catch (e) { /* ignore */ }
}

async function fetchDetail() {
  loading.value = true
  try {
    const data = await getRegistration(id)
    Object.assign(form, {
      patient_name: data.patient_name, patient_no: data.patient_no,
      department_id: data.department_id, doctor_id: data.doctor_id,
      registration_type: data.registration_type, registration_fee: data.registration_fee || data.price,
      registration_date: data.registration_date, time_period: data.time_period,
      price: data.price, status: data.status, notes: data.notes
    })
  } catch (e) {
    ElMessage.error('加载挂号信息失败')
  } finally {
    loading.value = false
  }
}

const onDeptChange = () => { form.doctor_id = '' }
const onFeeChange = (v) => { form.price = v }

const onSubmit = async () => {
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    await updateRegistration(id, {
      department_id: form.department_id, doctor_id: form.doctor_id,
      registration_type: form.registration_type, registration_fee: form.registration_fee,
      registration_date: form.registration_date, time_period: form.time_period,
      price: form.price, notes: form.notes
    })
    ElMessage.success('保存成功')
    router.push('/registration')
  } catch (e) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

const onBack = () => router.back()

onMounted(() => { fetchOptions(); fetchDetail() })
</script>

<style lang="scss" scoped>
.reg-edit-page { background: #f5f7fa; padding: 12px 16px 16px; }
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.page-title { font-size: 16px; font-weight: 600; color: #303133; }
.page-card { border-radius: 8px; }
.footer-bar { text-align: center; margin-top: 16px; }
</style>

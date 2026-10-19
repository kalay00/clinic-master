<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">新增患者信息</div>
      <div class="head-actions">
        <el-button type="primary" :icon="DocumentChecked" :loading="saving" @click="onSave">保存</el-button>
        <el-button :icon="Back" @click="onBack">返回</el-button>
      </div>
    </div>

    <el-card class="page-card" shadow="never">
      <div class="section-title">基本信息</div>
      <el-form :model="form" label-width="110px" class="patient-form">
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="患者姓名" required>
              <el-input v-model="form.name" placeholder="请输入患者姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者卡号">
              <el-input v-model="form.cardNo" placeholder="请输入病人卡号" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者年龄">
              <el-input v-model="form.age" placeholder="自动计算" readonly disabled><template #append>岁</template></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="出生日期" required>
              <el-date-picker v-model="form.birthday" type="date" style="width: 100%" @change="onBirthdayChange" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="性别" required>
              <el-select v-model="form.gender" placeholder="请选择" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
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
              <el-input v-model="form.idCard" placeholder="请输入证件号码" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者来源">
              <el-select v-model="form.source" placeholder="请选择" style="width: 100%">
                <el-option label="自然到店" value="1" />
                <el-option label="转诊" value="2" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="会员等级">
              <el-select v-model="form.member_level_id" placeholder="请选择" clearable style="width: 100%">
                <el-option v-for="lv in levelOptions" :key="lv.id" :label="lv.name" :value="lv.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="到期时间">
              <el-date-picker v-model="form.expireDate" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="民族">
              <el-input v-model="form.nation" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="婚姻状况">
              <el-select v-model="form.marriage" placeholder="请选择" style="width: 100%">
                <el-option label="未婚" value="single" />
                <el-option label="已婚" value="married" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="学历">
              <el-select v-model="form.education" placeholder="请选择" style="width: 100%">
                <el-option label="本科" value="本科" />
                <el-option label="大专" value="大专" />
                <el-option label="高中" value="高中" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地址">
              <el-input v-model="form.address" placeholder="请输入详细地址" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="职业">
              <el-select v-model="form.job" placeholder="请选择" style="width: 100%">
                <el-option label="教师" value="teacher" />
                <el-option label="医生" value="doctor" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="6">
            <el-form-item label="工作单位">
              <el-input v-model="form.company" />
            </el-form-item>
          </el-col>
          <el-col :span="18">
            <el-form-item label="备注">
              <el-input v-model="form.remark" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="section-header">
        关联家庭成员
        <el-button class="fr" type="success" :icon="Plus" @click="openFamilyDialog()">添加家庭成员</el-button>
      </div>
      <el-table :data="familyList" border stripe style="width: 100%">
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
            <el-button type="danger" link @click="removeFamily(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <FamilyDialog v-model="showFamily" :editing="familyEditing" @confirm="onFamilyConfirm" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentChecked, Back, Plus } from '@element-plus/icons-vue'
import { createPatient, getMemberLevels, createFamilyMember, updateFamilyMember, deleteFamilyMember } from '@/api/patient'
import FamilyDialog from './family.vue'

defineOptions({ name: 'PatientCreate' })

const router = useRouter()
const levelOptions = ref([])
const saving = ref(false)
const form = reactive({
  name: '', cardNo: '', age: '', birthday: '', gender: '男', phone: '', idCard: '',
  member_level_id: '', address: '', remark: ''
})
const familyList = ref([])
const showFamily = ref(false)
const familyEditing = ref(null)

function genderToBackend(v) {
  return v === '女' ? 'female' : 'male'
}
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
function formatGender(v) {
  if (v === 'female' || v === '女') return '女'
  if (v === 'male' || v === '男') return '男'
  return v || '-'
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
    const created = await createPatient(payload)
    const patientId = created?.id || created?.data?.id
    if (patientId && familyList.value.length) {
      for (const m of familyList.value) {
        if (m.id && !m._new) {
          continue
        }
        const { id, _new, created_at, ...rest } = m
        const data = { ...rest, gender: rest.gender === '女' ? 'female' : 'male' }
        await createFamilyMember(patientId, data)
      }
    }
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

function openFamilyDialog(row = null) {
  familyEditing.value = row
  showFamily.value = true
}

async function onFamilyConfirm(data) {
  if (data.id) {
    const idx = familyList.value.findIndex((m) => m.id === data.id)
    if (idx > -1) familyList.value[idx] = { ...data, _new: false }
  } else {
    familyList.value.push({
      relation: data.relation,
      name: data.name,
      gender: data.gender,
      age: data.age ?? null,
      birthday: data.birthday || '',
      phone: data.phone || '',
      _new: true
    })
  }
  showFamily.value = false
}

async function removeFamily(row) {
  try {
    await ElMessageBox.confirm('确定删除该家庭成员吗？', '提示', { type: 'warning' })
    if (row.id && !row._new) {
      await deleteFamilyMember(row._patientId, row.id).catch(() => {})
    }
    familyList.value = familyList.value.filter((m) => m !== row)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  try {
    const res = await getMemberLevels({ page: 1, page_size: 100 })
    levelOptions.value = res.items || []
    // 默认选中普通会员（默认等级），与后端 create_patient 兜底逻辑一致
    const def = levelOptions.value.find(lv => lv.is_default) || levelOptions.value[0]
    if (def) form.member_level_id = def.id
  } catch (e) { /* 等级非强依赖 */ }
})
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; }
.head-actions { display: flex; gap: 10px; }
.section-title { font-size: 16px; font-weight: 600; color: #5b7cff; margin: 8px 0 16px; padding-left: 12px; border-left: 4px solid #5b7cff; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin: 16px 0; }
.patient-form :deep(.el-form-item__label) { color: #606266; }
.fr { float: right; }
</style>

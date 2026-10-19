<template>
  <el-dialog
    v-model="visible"
    title="新增病历模板"
    width="720px"
    append-to-body
    @open="reset"
  >
    <el-form :model="form" label-width="90px" class="tpl-form">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="模板名称" required>
            <el-input v-model="form.name" placeholder="请输入模板名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="模板分类" required>
            <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
              <el-option label="门诊病历" value="outpatient" />
              <el-option label="住院病历" value="inpatient" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="诊断"><el-input v-model="form.diagnosis" placeholder="请输入诊断" /></el-form-item>
      <el-form-item label="主诉"><el-input v-model="form.chiefComplaint" type="textarea" :rows="2" placeholder="请输入主诉" /></el-form-item>
      <el-form-item label="现病史"><el-input v-model="form.presentIllness" type="textarea" :rows="2" placeholder="请输入现病史" /></el-form-item>
      <el-form-item label="既往史"><el-input v-model="form.pastHistory" type="textarea" :rows="2" placeholder="请输入既往史" /></el-form-item>
      <el-form-item label="过敏史"><el-input v-model="form.allergyHistory" type="textarea" :rows="2" placeholder="请输入过敏史" /></el-form-item>
      <el-form-item label="个人史"><el-input v-model="form.personalHistory" type="textarea" :rows="2" placeholder="请输入个人史" /></el-form-item>
      <el-form-item label="家族史"><el-input v-model="form.familyHistory" type="textarea" :rows="2" placeholder="请输入家族史" /></el-form-item>
      <el-form-item label="辅助检查"><el-input v-model="form.auxiliaryExam" type="textarea" :rows="2" placeholder="请输入辅助检查" /></el-form-item>
      <el-form-item label="治疗意见"><el-input v-model="form.treatmentOpinion" type="textarea" :rows="2" placeholder="请输入治疗意见" /></el-form-item>
      <el-form-item label="医嘱"><el-input v-model="form.advice" type="textarea" :rows="2" placeholder="请输入医嘱" /></el-form-item>
      <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" /></el-form-item>
    </el-form>

    <template #footer>
      <el-button :icon="Close" @click="visible = false">取消</el-button>
      <el-button type="primary" :icon="Check" @click="onSubmit">保存模板</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])

const emptyForm = () => ({
  name: '', category: '', diagnosis: '', chiefComplaint: '', presentIllness: '',
  pastHistory: '', allergyHistory: '', personalHistory: '', familyHistory: '',
  auxiliaryExam: '', treatmentOpinion: '', advice: '', remark: '',
})
const form = reactive(emptyForm())
const reset = () => Object.assign(form, emptyForm())

const onSubmit = () => {
  if (!form.name || !form.category) {
    ElMessage.warning('请填写模板名称和分类')
    return
  }
  emit('confirm', { ...form })
  ElMessage.success('模板保存成功')
  visible.value = false
}
</script>

<style lang="scss" scoped>
.tpl-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}
</style>

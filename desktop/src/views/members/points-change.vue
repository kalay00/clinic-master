<template>
  <el-dialog v-model="visible" title="积分变动" width="460px" :close-on-click-modal="false" @close="onCancel">
    <div class="member-head">
      <span>会员卡号：{{ member.patient_no || member.card || '-' }}</span>
      <span>会员姓名：{{ member.name || '-' }}</span>
    </div>
    <div class="balance-line">当前积分：{{ Number(member.points || 0) }}</div>
    <el-form :model="form" label-width="100px" class="member-form">
      <el-form-item label="变动方式">
        <el-radio-group v-model="form.action">
          <el-radio label="add">赠送积分</el-radio>
          <el-radio label="deduct">扣减积分</el-radio>
          <el-radio label="clear">清空积分</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="变动数量" v-if="form.action !== 'clear'">
        <el-input v-model="form.qty"><template #append>分</template></el-input>
      </el-form-item>
      <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { adjustMemberPoints } from '@/api/member'

const props = defineProps({ modelValue: Boolean, member: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:modelValue', 'confirmed'])

const visible = computed({ get: () => props.modelValue, set: (val) => emit('update:modelValue', val) })
const loading = ref(false)
const form = reactive({ action: 'add', qty: '', remark: '' })

const onCancel = () => { visible.value = false }
const onConfirm = async () => {
  if (!props.member.id) { ElMessage.warning('会员信息缺失'); return }
  let points = 0
  if (form.action === 'add') points = Number(form.qty)
  else if (form.action === 'deduct') points = -Number(form.qty)
  else if (form.action === 'clear') points = -Number(props.member.points || 0)
  if (!points) { ElMessage.warning('请输入正确的变动数量'); return }
  loading.value = true
  try {
    await adjustMemberPoints(props.member.id, { points, remark: form.remark })
    ElMessage.success('积分变动成功')
    visible.value = false
    emit('confirmed')
  } catch (e) {
    const d = e?.response?.data?.detail
    ElMessage.error((Array.isArray(d) ? d[0].msg : d) || '积分变动失败')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.member-head { font-size: 14px; color: #606266; margin-bottom: 12px; display: flex; gap: 40px; }
.balance-line { font-size: 14px; color: #606266; margin-bottom: 16px; }
.member-form :deep(.el-form-item__label) { color: #606266; }
</style>

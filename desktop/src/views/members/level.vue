<template>
  <el-dialog v-model="visible" title="会员等级设置" width="520px" :close-on-click-modal="false" @close="onCancel">
    <div class="member-head">
      <span>会员卡号：{{ member.patient_no || member.card || '-' }}</span>
      <span>会员姓名：{{ member.name || '-' }}</span>
    </div>
    <div class="balance-line">当前等级：{{ member.member_level_name || '非会员' }}</div>
    <el-form label-width="100px" class="member-form">
      <el-form-item label="选择等级">
        <el-select v-model="targetLevel" placeholder="请选择等级" style="width: 100%">
          <el-option v-for="lv in levels" :key="lv.id" :label="lv.name" :value="lv.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="到期时间">
        <el-date-picker v-model="expireDate" type="date" placeholder="不填则永久" value-format="YYYY-MM-DD" style="width: 100%" />
      </el-form-item>
      <el-form-item label="备注"><el-input v-model="remark" type="textarea" :rows="2" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { setMemberLevel } from '@/api/member'
import { getMemberLevels } from '@/api/patient'

const props = defineProps({ modelValue: Boolean, member: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:modelValue', 'confirmed'])

const visible = computed({ get: () => props.modelValue, set: (val) => emit('update:modelValue', val) })
const loading = ref(false)
const levels = ref([])
const targetLevel = ref('')
const expireDate = ref('')
const remark = ref('')

async function loadLevels() {
  try {
    const res = await getMemberLevels({ page: 1, page_size: 100 })
    levels.value = res.items || []
  } catch (e) { /* 等级非强依赖 */ }
}
const onCancel = () => { visible.value = false }
const onConfirm = async () => {
  if (!props.member.id) { ElMessage.warning('会员信息缺失'); return }
  if (!targetLevel.value) { ElMessage.warning('请选择会员等级'); return }
  loading.value = true
  try {
    await setMemberLevel(props.member.id, { member_level_id: targetLevel.value, remark: remark.value })
    ElMessage.success('设置成功')
    visible.value = false
    emit('confirmed')
  } catch (e) {
    const d = e?.response?.data?.detail
    ElMessage.error((Array.isArray(d) ? d[0].msg : d) || '设置失败')
  } finally {
    loading.value = false
  }
}

watch(visible, (open) => { if (open) loadLevels() })
</script>

<style lang="scss" scoped>
.member-head { font-size: 14px; color: #606266; margin-bottom: 12px; display: flex; gap: 40px; }
.balance-line { font-size: 14px; color: #606266; margin-bottom: 16px; }
.member-form :deep(.el-form-item__label) { color: #606266; }
</style>

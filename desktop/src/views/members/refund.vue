<template>
  <el-dialog v-model="visible" title="余额退款" width="460px" :close-on-click-modal="false" @close="onCancel">
    <div class="member-head">
      <span>会员卡号：{{ member.patient_no || member.card || '-' }}</span>
      <span>会员姓名：{{ member.name || '-' }}</span>
    </div>
    <div class="balance-line">当前余额：{{ Number(member.balance || 0).toFixed(2) }} 元</div>
    <el-form :model="form" label-width="100px" class="member-form">
      <el-form-item label="退款金额" required><el-input v-model="form.amount"><template #append>元</template></el-input></el-form-item>
      <el-form-item label="退款方式">
        <el-radio-group v-model="form.payWay">
          <el-radio label="cash">现金</el-radio>
          <el-radio label="alipay">支付宝</el-radio>
          <el-radio label="wechat">微信</el-radio>
          <el-radio label="card">银行卡</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onConfirm">确定退款</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { refundMember } from '@/api/member'

const props = defineProps({ modelValue: Boolean, member: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:modelValue', 'confirmed'])

const visible = computed({ get: () => props.modelValue, set: (val) => emit('update:modelValue', val) })
const loading = ref(false)
const form = reactive({ amount: '', payWay: 'cash', remark: '' })

const onCancel = () => { visible.value = false }
const onConfirm = async () => {
  if (!props.member.id) { ElMessage.warning('会员信息缺失'); return }
  const amount = Number(form.amount)
  if (!amount || amount <= 0) { ElMessage.warning('请输入正确的退款金额'); return }
  loading.value = true
  try {
    await refundMember(props.member.id, { amount, payWay: form.payWay, remark: form.remark })
    ElMessage.success('退款成功')
    visible.value = false
    emit('confirmed')
  } catch (e) {
    const d = e?.response?.data?.detail
    ElMessage.error((Array.isArray(d) ? d[0].msg : d) || '退款失败')
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

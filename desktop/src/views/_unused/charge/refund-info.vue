<template>
  <el-dialog v-model="visible" title="退费信息确认" width="680px" :close-on-click-modal="false" @close="onCancel">
    <el-card shadow="never" class="fee-card">
      <div class="fee-title">收费信息</div>
      <div class="fee-line">
        <span>应收金额：150.00 元</span>
        <span>实收金额：150.00 元</span>
        <span>可退金额：150.00 元</span>
        <span>支付方式：支付宝</span>
      </div>
    </el-card>

    <div class="section-title">退费明细</div>
    <el-table :data="rows" border stripe size="small">
      <el-table-column type="index" label="序号" width="50" />
      <el-table-column prop="code" label="编码" width="90" />
      <el-table-column prop="name" label="收费名称" min-width="130" />
      <el-table-column prop="price" label="单价（元）" width="90" />
      <el-table-column prop="qty" label="退费数量" width="90" />
      <el-table-column prop="unit" label="单位" width="60" />
      <el-table-column prop="amount" label="退费金额（元）" width="110" />
    </el-table>
    <div class="extra-fee">
      <span>附加费用</span>
      <span class="ml-lg">注射费：20.00元</span>
      <span class="ml-lg">处理费：15.00元</span>
    </div>

    <el-form :model="form" label-width="100px" class="refund-form">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="实退金额">
            <el-input v-model="form.refundAmount" style="width: 140px"><template #append>元</template></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="退费方式">
            <el-radio-group v-model="form.refundMethod">
              <el-radio label="cash">现金</el-radio>
              <el-radio label="alipay">支付宝</el-radio>
              <el-radio label="wechat">微信</el-radio>
              <el-radio label="card">银行卡</el-radio>
              <el-radio label="member">会员卡</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="退费说明">
        <el-input v-model="form.remark" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="onCancel">取消</el-button>
      <el-button type="primary" @click="onConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const rows = reactive([
  { code: '100010', name: '阿卡波糖片', price: '15.00', qty: '1', unit: '瓶', amount: '15.00' },
  { code: '100234', name: '胃镜检查', price: '25.00', qty: '1', unit: '次', amount: '25.00' }
])

const form = reactive({ refundAmount: '75.00', refundMethod: 'cash', remark: '' })

const onCancel = () => { visible.value = false }
const onConfirm = () => {
  emit('confirm', { ...form })
  visible.value = false
  ElMessage.success('退费确认成功')
}
</script>

<style lang="scss" scoped>
.fee-card { margin-bottom: 16px; background: #f7f8ff; }
.fee-title { font-weight: 600; color: #5b7cff; margin-bottom: 8px; }
.fee-line { display: flex; gap: 40px; font-size: 14px; color: #606266; }
.section-title { font-size: 15px; font-weight: 600; color: #5b7cff; margin: 16px 0 12px; padding-left: 10px; border-left: 3px solid #5b7cff; }
.extra-fee { margin-top: 10px; font-size: 14px; color: #606266; }
.refund-form { margin-top: 16px; }
</style>

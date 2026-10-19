<template>
  <el-dialog
    v-model="visible"
    title="收费确认"
    width="820px"
    append-to-body
  >
    <!-- 项目明细 -->
    <div class="section-title">项目明细</div>
    <el-table :data="items" border class="confirm-table">
      <el-table-column type="index" label="序号" width="50" />
      <el-table-column prop="name" label="项目名称" min-width="160" />
      <el-table-column prop="type" label="项目类型" width="110" />
      <el-table-column prop="spec" label="规格" width="100" />
      <el-table-column prop="num" label="数量" width="70" />
      <el-table-column prop="price" label="单价" width="90" />
      <el-table-column prop="amount" label="金额" width="90" />
    </el-table>

    <!-- 人员信息 -->
    <div class="section-title">人员信息</div>
    <el-descriptions :column="3" border class="confirm-desc">
      <el-descriptions-item label="患者姓名">{{ staff.patientName }}</el-descriptions-item>
      <el-descriptions-item label="卡号">{{ staff.cardNo }}</el-descriptions-item>
      <el-descriptions-item label="性别">{{ staff.gender }}</el-descriptions-item>
      <el-descriptions-item label="接诊医生">{{ staff.doctor }}</el-descriptions-item>
      <el-descriptions-item label="科室">{{ staff.dept }}</el-descriptions-item>
      <el-descriptions-item label="接诊类型">{{ staff.visitType }}</el-descriptions-item>
    </el-descriptions>

    <!-- 接诊信息 -->
    <div class="section-title">接诊信息</div>
    <el-descriptions :column="3" border class="confirm-desc">
      <el-descriptions-item label="接诊时间">{{ info.time }}</el-descriptions-item>
      <el-descriptions-item label="接诊类型">{{ info.type }}</el-descriptions-item>
      <el-descriptions-item label="处方数量">{{ info.rxCount }}</el-descriptions-item>
      <el-descriptions-item label="诊断">{{ info.diagnosis }}</el-descriptions-item>
      <el-descriptions-item label="主诉">{{ info.chiefComplaint }}</el-descriptions-item>
      <el-descriptions-item label="备注">{{ info.remark }}</el-descriptions-item>
    </el-descriptions>

    <div class="confirm-total">
      应收合计：<span class="amount">{{ totalAmount.toFixed(2) }}</span> 元
    </div>

    <template #footer>
      <el-button :icon="Printer" @click="onPrint">打印确认单</el-button>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :icon="Check" @click="onConfirm">确认收费</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Printer, Check } from '@element-plus/icons-vue'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])

const items = ref([
  { name: '阿莫西林胶囊', type: '药品', spec: '0.25g*20', num: 2, price: '15.00', amount: '30.00' },
  { name: '血常规', type: '检查', spec: '-', num: 1, price: '20.00', amount: '20.00' },
  { name: '挂号费', type: '服务', spec: '-', num: 1, price: '10.00', amount: '10.00' },
])

const totalAmount = computed(() => items.value.reduce((s, i) => s + Number(i.amount || 0), 0))

const staff = ref({
  patientName: '张伟', cardNo: 'KH20260803001', gender: '男',
  doctor: '王阳明', dept: '全科', visitType: '初诊',
})
const info = ref({
  time: '2026-08-03 10:30', type: '初诊', rxCount: '1',
  diagnosis: '急性上呼吸道感染', chiefComplaint: '发热咳嗽2天', remark: '无',
})

const onPrint = () => { ElMessage.info('调用浏览器打印'); window.print() }
const onConfirm = () => {
  emit('confirm', { amount: totalAmount.value })
  ElMessage.success('收费确认成功')
  visible.value = false
}
</script>

<style lang="scss" scoped>
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #5b7cff;
  margin: 16px 0 10px;
  padding-left: 10px;
  border-left: 3px solid #5b7cff;
  &:first-child {
    margin-top: 0;
  }
}
.confirm-table {
  margin-bottom: 4px;
}
.confirm-desc {
  margin-bottom: 4px;
}
.confirm-total {
  text-align: right;
  margin: 14px 0 4px;
  font-size: 15px;
  .amount {
    color: #f56c6c;
    font-size: 20px;
    font-weight: 600;
    margin: 0 4px;
  }
}
</style>

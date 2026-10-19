<template>
  <el-dialog
    v-model="visible"
    title="附加费用"
    width="520px"
    append-to-body
  >
    <div class="extra-tip">名称与金额可在【系统设置-处方费用设置】进行设置</div>
    <el-table :data="extraList" border class="extra-table">
      <el-table-column width="50">
        <template #default="{ row }"><el-checkbox v-model="row.selected" /></template>
      </el-table-column>
      <el-table-column label="序号" width="60">
        <template #default="{ $index }">{{ String($index + 1).padStart(2, '0') }}</template>
      </el-table-column>
      <el-table-column prop="name" label="费用名称" />
      <el-table-column label="数量" width="90">
        <template #default="{ row }"><el-input v-model="row.quantity" size="small" /></template>
      </el-table-column>
      <el-table-column label="价格" width="90">
        <template #default="{ row }"><el-input v-model="row.price" size="small" /></template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="onConfirm">添加</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])

const extraList = reactive([
  { id: 1, name: '注射费', quantity: 1, price: '3.0', selected: true },
  { id: 2, name: '材料费', quantity: 1, price: '4.0', selected: true },
  { id: 3, name: '处理费', quantity: 1, price: '6.0', selected: true },
  { id: 4, name: '诊疗费', quantity: 1, price: '8.0', selected: true },
])

const onConfirm = () => {
  const chosen = extraList.filter((i) => i.selected)
  emit('confirm', chosen)
  ElMessage.success('附加费用已添加')
  visible.value = false
}
</script>

<style lang="scss" scoped>
.extra-tip {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}
</style>

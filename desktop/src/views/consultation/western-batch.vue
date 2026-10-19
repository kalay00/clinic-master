<template>
  <el-dialog
    v-model="visible"
    title="批量设置药品信息"
    width="680px"
    append-to-body
  >
    <el-table :data="rows" border class="batch-table">
      <el-table-column width="50">
        <template #default="{ row }">
          <el-checkbox v-model="row.checked" />
        </template>
      </el-table-column>
      <el-table-column label="组号" width="70">
        <template #default="{ row }"><el-input v-model="row.group" size="small" /></template>
      </el-table-column>
      <el-table-column label="单次用量" width="100">
        <template #default="{ row }"><el-input v-model="row.dosage" size="small" /></template>
      </el-table-column>
      <el-table-column label="用法" width="110">
        <template #default="{ row }">
          <el-select v-model="row.usage" size="small">
            <el-option label="口服" value="口服" />
            <el-option label="外用" value="外用" />
            <el-option label="注射" value="注射" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="频度" width="120">
        <template #default="{ row }">
          <el-select v-model="row.frequency" size="small">
            <el-option label="一天1次" value="一天1次" />
            <el-option label="一天2次" value="一天2次" />
            <el-option label="一天3次" value="一天3次" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="天数" width="80">
        <template #default="{ row }"><el-input v-model="row.days" size="small" /></template>
      </el-table-column>
      <el-table-column label="总量" width="90">
        <template #default="{ row }"><el-input v-model="row.total" size="small" /></template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="onConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])

const rows = reactive([
  { checked: true, group: '1', dosage: '1', usage: '口服', frequency: '一天1次', days: '1', total: '' },
])

const onConfirm = () => {
  emit('confirm', rows.filter((r) => r.checked))
  ElMessage.success('批量设置已应用')
  visible.value = false
}
</script>

<style lang="scss" scoped>
.batch-table {
  :deep(.el-table__row) {
    cursor: default;
  }
}
</style>

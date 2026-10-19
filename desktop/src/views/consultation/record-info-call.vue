<template>
  <el-dialog
    v-model="visible"
    title="调用病历信息"
    width="640px"
    append-to-body
  >
    <el-table :data="records" border max-height="360">
      <el-table-column prop="name" label="病历内容" min-width="200" />
      <el-table-column prop="createTime" label="创建时间" width="180" />
      <el-table-column prop="creator" label="创建人员" width="120" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="onUse(row)">调用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])

const records = ref([
  { id: 1, name: '张伟 门诊病历 2026-07-20', createTime: '2026-07-20 09:15', creator: '王阳明' },
  { id: 2, name: '李娜 门诊病历 2026-07-18', createTime: '2026-07-18 11:02', creator: '张仲景' },
  { id: 3, name: '王强 门诊病历 2026-07-15', createTime: '2026-07-15 14:30', creator: '王阳明' },
])

const onUse = (row) => {
  emit('confirm', row)
  ElMessage.success(`已调用病历「${row.name}」`)
  visible.value = false
}
</script>

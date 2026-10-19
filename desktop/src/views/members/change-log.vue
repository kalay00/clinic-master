<template>
  <el-dialog v-model="visible" title="会员等级变更记录" width="640px" :close-on-click-modal="false" @close="onCancel">
    <div class="member-head">
      <span>会员卡号：{{ member.patient_no || member.card || '-' }}</span>
      <span>会员姓名：{{ member.name || '-' }}</span>
    </div>
    <el-table :data="logs" border stripe v-loading="loading" max-height="360">
      <el-table-column prop="created_at" label="变更时间" width="160" />
      <el-table-column prop="type" label="变更类型" width="110">
        <template #default>等级变更</template>
      </el-table-column>
      <el-table-column prop="remark" label="变更内容" />
      <el-table-column prop="after_points" label="操作人" width="120">
        <template #default="{ row }">{{ row.operator_id || '-' }}</template>
      </el-table-column>
    </el-table>
    <el-pagination class="list-pagination" v-model:current-page="page" :current-page="page" v-model:page-size="pageSize" layout="total, prev, pager, next" :total="total" @current-change="(p) => { page = p; fetchLogs() }" />
    <template #footer>
      <el-button @click="onCancel">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { getMemberTransactions } from '@/api/member'

const props = defineProps({ modelValue: Boolean, member: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:modelValue'])

const visible = computed({ get: () => props.modelValue, set: (val) => emit('update:modelValue', val) })
const loading = ref(false)
const logs = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

async function fetchLogs() {
  if (!props.member.id) return
  loading.value = true
  try {
    const res = await getMemberTransactions(props.member.id, { page: page.value, pageSize: pageSize.value, type: 'level_change' })
    logs.value = res.items || []
    total.value = (res.pagination && res.pagination.total) || 0
  } finally {
    loading.value = false
  }
}
const onCancel = () => { visible.value = false }
watch(visible, (val) => { if (val) { page.value = 1; fetchLogs() } })
</script>

<style lang="scss" scoped>
.member-head { font-size: 14px; color: #606266; margin-bottom: 12px; display: flex; gap: 40px; }
.list-pagination { justify-content: flex-end; margin-top: 10px; }
</style>

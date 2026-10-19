<template>
  <el-dialog v-model="visible" title="积分变动记录" width="640px" :close-on-click-modal="false" @close="onCancel">
    <div class="member-head">
      <span>会员卡号：{{ member.patient_no || member.card || '-' }}</span>
      <span>会员姓名：{{ member.name || '-' }}</span>
    </div>
    <el-table :data="logs" border stripe v-loading="loading" max-height="360">
      <el-table-column prop="created_at" label="变动时间" width="160" />
      <el-table-column label="变动类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.type === 'points_add' ? 'success' : 'danger'" size="small">
            {{ row.type === 'points_add' ? '增加' : '扣减' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="变动数量" width="100">
        <template #default="{ row }">{{ row.points > 0 ? '+' : '' }}{{ row.points }}</template>
      </el-table-column>
      <el-table-column prop="after_points" label="变动后积分" width="120" />
      <el-table-column prop="remark" label="备注" />
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
    const res = await getMemberTransactions(props.member.id, { page: page.value, pageSize: pageSize.value })
    logs.value = (res.items || []).filter(it => it.type === 'points_add' || it.type === 'points_deduct')
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

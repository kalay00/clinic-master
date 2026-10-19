<template>
  <el-dialog v-model="visible" title="会员条件设置" width="680px" :close-on-click-modal="false" @close="onCancel">
    <el-alert type="info" :closable="false" show-icon title="会员等级依据「累计消费阈值」自动升级，阈值在会员类型中维护。" style="margin-bottom: 12px" />
    <el-table :data="rows" border stripe v-loading="loading">
      <el-table-column type="index" label="序号" width="55" />
      <el-table-column prop="name" label="会员等级" width="120" />
      <el-table-column prop="upgrade_threshold" label="升级阈值（累计消费/元）" width="200">
        <template #default="{ row }">{{ row.upgrade_threshold || 0 }}</template>
      </el-table-column>
      <el-table-column prop="discount_rate" label="享受折扣率" width="120">
        <template #default="{ row }">{{ row.discount_rate || 1 }}</template>
      </el-table-column>
    </el-table>
    <template #footer>
      <el-button @click="onCancel">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { getLevels } from '@/api/member'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])

const visible = computed({ get: () => props.modelValue, set: (val) => emit('update:modelValue', val) })
const loading = ref(false)
const rows = ref([])

async function load() {
  loading.value = true
  try {
    const res = await getLevels({ page: 1, page_size: 100 })
    rows.value = res.items || []
  } catch (e) { /* 忽略 */ }
  finally { loading.value = false }
}
const onCancel = () => { visible.value = false }
watch(visible, (open) => { if (open) load() })
</script>

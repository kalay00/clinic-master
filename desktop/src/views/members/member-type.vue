<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑会员类型' : '新增会员类型'" width="760px" :close-on-click-modal="false" @close="onCancel">
    <el-table v-if="!isEdit" :data="rows" border stripe v-loading="loading" style="margin-bottom: 16px">
      <el-table-column type="index" label="序号" width="55" />
      <el-table-column prop="name" label="会员等级" min-width="140" />
      <el-table-column prop="discount_rate" label="折扣率" width="90" />
      <el-table-column prop="upgrade_threshold" label="升级阈值" min-width="120" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'inactive' ? 'info' : 'success'" size="small">
            {{ row.status === 'inactive' ? '停用' : '启用' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
    <el-form :inline="true" class="filter-form">
      <el-form-item label="会员等级"><el-input v-model="form.name" placeholder="如 普通会员" /></el-form-item>
      <el-form-item label="折扣率"><el-input v-model="form.discount_rate" placeholder="如 0.95" style="width: 90px" /></el-form-item>
      <el-form-item label="升级阈值"><el-input v-model="form.upgrade_threshold" placeholder="累计消费" style="width: 110px" /></el-form-item>
      <el-form-item label="状态">
        <el-select v-model="form.status" style="width: 110px">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onCancel">关闭</el-button>
      <el-button type="primary" :loading="loading" @click="onConfirm">{{ isEdit ? '保存' : '新增' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getLevels, createLevel, updateLevel } from '@/api/member'

const props = defineProps({
  modelValue: Boolean,
  editData: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const visible = computed({ get: () => props.modelValue, set: (val) => emit('update:modelValue', val) })
const isEdit = computed(() => !!props.editData && !!props.editData.id)
const loading = ref(false)
const rows = ref([])
const form = ref({ name: '', discount_rate: '', upgrade_threshold: '', status: 'active' })

// 打开时回显编辑数据
watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      if (isEdit.value) {
        const d = props.editData
        form.value = {
          name: d.name || '',
          discount_rate: d.discount_rate ?? '',
          upgrade_threshold: d.upgrade_threshold ?? '',
          status: d.status || 'active'
        }
      } else {
        form.value = { name: '', discount_rate: '', upgrade_threshold: '', status: 'active' }
      }
    }
  },
  { immediate: true }
)

async function load() {
  loading.value = true
  try {
    const res = await getLevels({ page: 1, page_size: 100 })
    rows.value = res.items || []
  } catch (e) { /* 忽略 */ }
  finally { loading.value = false }
}
const onCancel = () => { visible.value = false }
const onConfirm = async () => {
  if (!form.value.name) { ElMessage.warning('请填写会员名称'); return }
  loading.value = true
  try {
    const payload = {
      name: form.value.name,
      discount_rate: form.value.discount_rate ? Number(form.value.discount_rate) : 1,
      upgrade_threshold: form.value.upgrade_threshold ? Number(form.value.upgrade_threshold) : 0,
      status: form.value.status
    }
    if (isEdit.value) {
      await updateLevel(props.editData.id, payload)
      ElMessage.success('保存成功')
    } else {
      await createLevel(payload)
      ElMessage.success('新增成功')
    }
    form.value = { name: '', discount_rate: '', upgrade_threshold: '', status: 'active' }
    await load()
    emit('saved')
  } catch (e) {
    const d = e?.response?.data?.detail
    ElMessage.error((Array.isArray(d) ? d[0].msg : d) || (isEdit.value ? '保存失败' : '新增失败'))
  } finally { loading.value = false }
}
</script>

<style lang="scss" scoped>
.filter-form :deep(.el-form-item) { margin-bottom: 10px; }
</style>

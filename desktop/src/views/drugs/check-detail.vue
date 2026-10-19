<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">盘点详情</div>
        <div class="his-page-subtitle">{{ info.check_no }}</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="盘点单号">{{ info.check_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(info.status)" size="small">{{ statusMap[info.status] || info.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ info.created_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="his-section-title" style="margin-top:20px">盘点明细</div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="drug_name" label="药品名称" min-width="200" />
        <el-table-column prop="book_quantity" label="账面数量" width="110" />
        <el-table-column prop="actual_quantity" label="实盘数量" width="110" />
        <el-table-column label="差异" width="100">
          <template #default="{ row }">{{ (row.actual_quantity || 0) - (row.book_quantity || 0) }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="差异原因" min-width="140" />
      </el-table>
    </div>
    <div class="his-footer-bar" v-if="info.status && info.status !== 'completed'">
      <el-button @click="onBack">关闭</el-button>
      <el-button type="success" :loading="acting" @click="onComplete">完成盘点</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { getInventoryCheck, completeInventoryCheck } from '@/api/inventory'

defineOptions({ name: 'CheckDetail' })

const route = useRoute()
const router = useRouter()
const id = route.params.id
const loading = ref(false)
const acting = ref(false)
const info = reactive({})
const items = ref([])
const statusMap = { draft: '草稿', counted: '已盘点', completed: '已完成' }
const statusType = (s) => ({ draft: 'info', counted: 'warning', completed: 'success' }[s] || 'info')

async function load() {
  loading.value = true
  try {
    const d = await getInventoryCheck(id)
    Object.assign(info, d)
    items.value = d.items || []
  } catch (e) { ElMessage.error('加载详情失败') }
  finally { loading.value = false }
}
const onComplete = async () => { acting.value = true; try { await completeInventoryCheck(id); ElMessage.success('盘点完成'); await load() } catch (e) { ElMessage.error(e?.message || '操作失败') } finally { acting.value = false } }
const onBack = () => router.back()
onMounted(load)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
</style>

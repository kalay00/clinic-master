<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">调价详情</div>
        <div class="his-page-subtitle">{{ info.adjustment_no }}</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="调价单号">{{ info.adjustment_no }}</el-descriptions-item>
        <el-descriptions-item label="调价日期">{{ info.adjust_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="info.status === 'approved' ? 'success' : 'info'" size="small">{{ info.status === 'approved' ? '已审批' : '草稿' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ info.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="his-section-title" style="margin-top:20px">调价明细</div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="drug_name" label="药品名称" min-width="200" />
        <el-table-column prop="old_price" label="原价（元）" width="120">
          <template #default="{ row }">{{ fmt(row.old_price) }}</template>
        </el-table-column>
        <el-table-column prop="new_price" label="新价（元）" width="120">
          <template #default="{ row }">{{ fmt(row.new_price) }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="调价原因" min-width="140" />
      </el-table>
    </div>
    <div class="his-footer-bar" v-if="info.status && info.status !== 'approved'">
      <el-button @click="onBack">关闭</el-button>
      <el-button type="success" :loading="acting" @click="onApprove">审批生效</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { getPriceAdjustment, approvePriceAdjustment } from '@/api/pharmacy'

defineOptions({ name: 'PriceDetail' })

const route = useRoute()
const router = useRouter()
const id = route.params.id
const loading = ref(false)
const acting = ref(false)
const info = reactive({})
const items = ref([])
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function load() {
  loading.value = true
  try {
    const d = await getPriceAdjustment(id)
    Object.assign(info, d)
    items.value = d.items || []
  } catch (e) { ElMessage.error('加载详情失败') }
  finally { loading.value = false }
}
const onApprove = async () => { acting.value = true; try { await approvePriceAdjustment(id); ElMessage.success('审批成功，售价已更新'); await load() } catch (e) { ElMessage.error(e?.message || '审批失败') } finally { acting.value = false } }
const onBack = () => router.back()
onMounted(load)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
</style>

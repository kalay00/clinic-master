<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">入库详情</div>
        <div class="his-page-subtitle">{{ info.order_no }}</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <div class="his-section-title">入库信息</div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="入库单号">{{ info.order_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ info.supplier_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="入库类型">{{ info.order_type === 'return' ? '退货入库' : '采购入库' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(info.status)" size="small">{{ statusMap[info.status] || info.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总金额（元）">{{ fmt(info.total_amount) }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ info.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="his-section-title" style="margin-top:20px">药品明细</div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="drug_name" label="药品名称" min-width="200" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="unit_price" label="单价（元）" width="120">
          <template #default="{ row }">{{ fmt(row.unit_price) }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额（元）" width="120">
          <template #default="{ row }">{{ fmt(row.amount) }}</template>
        </el-table-column>
      </el-table>
    </div>
    <div class="his-footer-bar" v-if="info.status && info.status !== 'cancelled'">
      <el-button @click="onBack">关闭</el-button>
      <el-button v-if="info.status === 'submitted'" type="primary" :loading="acting" @click="onApprove">审核</el-button>
      <el-button v-if="info.status === 'approved'" type="success" :loading="acting" @click="onReceive">入库</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { getPurchaseOrder, approvePurchaseOrder, receivePurchaseOrder } from '@/api/inventory'

defineOptions({ name: 'InboundDetail' })

const route = useRoute()
const router = useRouter()
const id = route.params.id
const loading = ref(false)
const acting = ref(false)
const info = reactive({})
const items = ref([])
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)
const statusMap = { draft: '草稿', submitted: '待审核', approved: '已审核', received: '已入库', cancelled: '已取消' }
const statusType = (s) => ({ draft: 'info', submitted: 'warning', approved: 'primary', received: 'success', cancelled: 'danger' }[s] || 'info')

async function load() {
  loading.value = true
  try {
    const d = await getPurchaseOrder(id)
    Object.assign(info, d)
    items.value = d.items || []
  } catch (e) { ElMessage.error('加载详情失败') }
  finally { loading.value = false }
}
const onApprove = async () => { acting.value = true; try { await approvePurchaseOrder(id); ElMessage.success('审核成功'); await load() } catch (e) { ElMessage.error(e?.message || '审核失败') } finally { acting.value = false } }
const onReceive = async () => { acting.value = true; try { await receivePurchaseOrder(id); ElMessage.success('入库成功'); await load() } catch (e) { ElMessage.error(e?.message || '入库失败') } finally { acting.value = false } }
const onBack = () => router.back()
onMounted(load)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
</style>

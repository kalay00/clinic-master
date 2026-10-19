<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">库存明细</div>
        <div class="his-page-subtitle">药品库存与流水</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>

    <div class="his-card" v-loading="loading">
      <div class="his-section-title">库存信息</div>
      <el-descriptions :column="2" border class="info-list" v-if="stock">
        <el-descriptions-item label="药品编码">{{ stock.drug_code }}</el-descriptions-item>
        <el-descriptions-item label="药品名称">{{ stock.drug_name }}</el-descriptions-item>
        <el-descriptions-item label="规格">{{ stock.specification || '-' }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ stock.supplier_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="批号">{{ stock.batch_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="有效期">{{ stock.expiry_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="当前库存">{{ stock.quantity }}</el-descriptions-item>
        <el-descriptions-item label="库存下限">{{ stock.min_quantity }}</el-descriptions-item>
      </el-descriptions>
      <el-empty v-else description="未找到该药品库存记录" />

      <div class="his-section-title" style="margin-top:20px">库存流水</div>
      <el-empty description="后端暂未提供库存流水查询接口（inventory transactions），待补齐后接入。" />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { getInventory } from '@/api/pharmacy'

defineOptions({ name: 'DrugStockDetail' })

const route = useRoute()
const router = useRouter()
const id = route.query.id
const loading = ref(false)
const stock = ref(null)

async function fetchStock() {
  if (!id) return
  loading.value = true
  try {
    const res = await getInventory({ drug_id: id, page_size: 1 })
    stock.value = (res.items && res.items[0]) || null
  } catch (e) {
    ElMessage.error('加载库存失败')
  } finally {
    loading.value = false
  }
}

const onBack = () => router.back()

onMounted(fetchStock)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.info-list { margin-bottom: 8px; }
</style>

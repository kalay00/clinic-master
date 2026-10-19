<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">编辑调价</div>
        <div class="his-page-subtitle">调整未审批调价单</div>
      </div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <div class="his-card" v-loading="loading">
      <el-form label-width="100px">
        <el-form-item label="调价日期">
          <el-date-picker v-model="adjustDate" type="date" value-format="YYYY-MM-DD" style="width: 220px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="remark" type="textarea" :rows="2" style="width: 460px" />
        </el-form-item>
      </el-form>
      <div class="his-section-title">调价明细</div>
      <el-table :data="items" border stripe>
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="drug_name" label="药品名称" min-width="200" />
        <el-table-column label="原价（元）" width="120"><template #default="{ row }">{{ fmt(row.old_price) }}</template></el-table-column>
        <el-table-column label="新价（元）" width="140"><template #default="{ row }"><el-input-number v-model="row.new_price" :min="0" :precision="2" size="small" /></template></el-table-column>
        <el-table-column label="调价原因" min-width="140"><template #default="{ row }"><el-input v-model="row.reason" /></template></el-table-column>
      </el-table>
    </div>
    <div class="his-footer-bar">
      <el-button @click="onBack">取消</el-button>
      <el-button type="primary" :loading="submitting" :icon="Check" @click="onSubmit">保存</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Check } from '@element-plus/icons-vue'
import { getPriceAdjustment, createPriceAdjustment } from '@/api/pharmacy'

defineOptions({ name: 'PriceEdit' })

const route = useRoute()
const router = useRouter()
const id = route.params.id
const loading = ref(false)
const submitting = ref(false)
const items = ref([])
const adjustDate = ref('')
const remark = ref('')
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function load() {
  loading.value = true
  try {
    const d = await getPriceAdjustment(id)
    adjustDate.value = d.adjust_date || new Date().toISOString().slice(0, 10)
    remark.value = d.remark || ''
    items.value = (d.items || []).map(x => ({ drug_id: x.drug_id, drug_name: x.drug_name, old_price: x.old_price, new_price: x.new_price, reason: x.reason }))
  } catch (e) { ElMessage.error('加载调价单失败') }
  finally { loading.value = false }
}
const onSubmit = async () => {
  if (!items.value.length) { ElMessage.warning('无调价明细'); return }
  submitting.value = true
  try {
    await createPriceAdjustment({ adjust_date: adjustDate.value, remark: remark.value, items: items.value.map(x => ({ drug_id: x.drug_id, new_price: x.new_price, reason: x.reason })) })
    ElMessage.success('已保存为新调价单')
    router.push('/drugs/price')
  } catch (e) { ElMessage.error(e?.message || '保存失败') }
  finally { submitting.value = false }
}
const onBack = () => router.back()
onMounted(load)
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
</style>

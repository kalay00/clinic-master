<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">发药详情</div>
      <div class="head-actions">
        <el-button :icon="Back" @click="onBack">返回</el-button>
      </div>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="16">
        <!-- 处方项目明细 -->
        <el-card class="page-card" shadow="never">
          <div class="section-title">项目明细</div>
          <el-table :data="items" border stripe>
            <el-table-column type="index" label="序号" width="55" />
            <el-table-column prop="name" label="药品名称" min-width="150" />
            <el-table-column prop="specification" label="规格" width="110" />
            <el-table-column prop="quantity" label="数量" width="70" />
            <el-table-column prop="unit" label="单位" width="60" />
            <el-table-column prop="price" label="单价（元）" width="100">
              <template #default="{ row }">{{ formatMoney(row.price) }}</template>
            </el-table-column>
            <el-table-column label="金额（元）" width="100">
              <template #default="{ row }">{{ formatMoney(Number(row.price || 0) * Number(row.quantity || 0)) }}</template>
            </el-table-column>
            <el-table-column prop="usage" label="用法" width="90" />
            <el-table-column prop="frequency" label="频度" width="100" />
            <el-table-column prop="days" label="天数" width="60" />
          </el-table>
          <div class="summary-bar">
            <span>处方金额：{{ formatMoney(rx.total_amount) }} 元</span>
            <span class="ml-lg">药品数量：{{ items.length }} 种</span>
          </div>
        </el-card>

        <!-- 发药记录 -->
        <el-card class="page-card" shadow="never">
          <div class="section-title">发药记录</div>
          <el-table :data="dispenseRows" border stripe>
            <el-table-column type="index" label="序号" width="55" />
            <el-table-column prop="drug_name" label="药品名称" min-width="150" />
            <el-table-column prop="quantity" label="发药数量" width="90" />
            <el-table-column prop="unit_price" label="单价（元）" width="100">
              <template #default="{ row }">{{ formatMoney(row.unit_price) }}</template>
            </el-table-column>
            <el-table-column prop="total_amount" label="金额（元）" width="100">
              <template #default="{ row }">{{ formatMoney(row.total_amount) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="dispenseStatusTag(row.status)" size="small">
                  {{ dispenseStatusMap[row.status] || row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="发药时间" min-width="160" />
          </el-table>
          <el-empty v-if="!loading && !dispenseRows.length" description="暂无发药记录（尚未发药）" />
        </el-card>
      </el-col>

      <el-col :span="8">
        <!-- 处方信息 -->
        <el-card class="page-card" shadow="never">
          <div class="section-title">处方信息</div>
          <el-descriptions :column="1" border class="info-list">
            <el-descriptions-item label="处方单号">{{ rx.prescription_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="处方类型">{{ rxTypeMap[rx.prescription_type] || rx.prescription_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="开方医生">{{ rx.doctor_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="处方金额（元）">{{ formatMoney(rx.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="处方状态">
              <el-tag :type="rxStatusTag(rx.status)" size="small">
                {{ rxStatusMap[rx.status] || rx.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="开方时间">{{ rx.created_at || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 患者信息 -->
        <el-card class="page-card" shadow="never">
          <div class="section-title">患者信息</div>
          <el-descriptions :column="1" border class="info-list">
            <el-descriptions-item label="患者姓名">{{ rx.patient_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="档案编号">{{ rx.patient_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ formatGender(patient.gender) }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ patient.age || '-' }}</el-descriptions-item>
            <el-descriptions-item label="手机号码">{{ patient.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="证件号码">{{ patient.id_card || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back } from '@element-plus/icons-vue'
import { getPrescription } from '@/api/treatment'
import { getDispenses } from '@/api/pharmacy'
import { getPatient } from '@/api/patient'

defineOptions({ name: 'DispenseDetail' })

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const rx = ref({})
const patient = reactive({ gender: '', age: '', phone: '', id_card: '' })
const dispenseRows = ref([])

const rxTypeMap = { western: '西药处方', traditional: '中药处方', chinese: '中药处方', inspection: '检查项目' }
const rxStatusMap = { pending: '待收费', paid: '待发药', dispensed: '已发药', cancelled: '已取消' }
const dispenseStatusMap = { pending: '待审核', dispensed: '已发药', cancelled: '已取消' }

const items = computed(() => {
  const list = rx.value.items
  return Array.isArray(list) ? list : []
})

const formatMoney = (v) => v == null ? '0.00' : Number(v).toFixed(2)
const formatGender = (g) => (g === 'male' || g === 'M' || g === '男' ? '男' : g === 'female' || g === 'F' || g === '女' ? '女' : '-')
const rxStatusTag = (s) => ({ pending: 'info', paid: 'warning', dispensed: 'success', cancelled: 'danger' }[s] || 'info')
const dispenseStatusTag = (s) => ({ pending: 'warning', dispensed: 'success', cancelled: 'danger' }[s] || 'info')

const onBack = () => router.back()

const loadDetail = async () => {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    // 处方（含富化明细：药品名称/规格/单位 + 患者/医生）
    rx.value = await getPrescription(id)
    // 患者详情补全性别/年龄/手机/证件
    if (rx.value.patient_id) {
      try {
        const p = await getPatient(rx.value.patient_id)
        patient.gender = p.gender || ''
        patient.age = p.age ?? ''
        patient.phone = p.phone || ''
        patient.id_card = p.id_card || ''
      } catch (e) { /* 患者详情获取失败不影响主流程 */ }
    }
    // 发药记录
    try {
      const res = await getDispenses({ prescription_id: id, page: 1, page_size: 100 })
      const list = res.items || []
      // 发药记录只有 drug_id，用处方明细补药品名称
      const nameMap = {}
      items.value.forEach(it => { if (it.drug_id) nameMap[it.drug_id] = it })
      dispenseRows.value = list.map(d => ({
        ...d,
        drug_name: nameMap[d.drug_id]?.name || d.drug_id || '-',
      }))
    } catch (e) {
      dispenseRows.value = []
    }
  } catch (e) {
    rx.value = {}
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
</script>

<style lang="scss" scoped>
.page-card { margin-bottom: 20px; }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: 12px; }
.info-list { margin-bottom: 8px; }
.summary-bar { margin-top: 12px; color: #606266; font-size: 13px; }
.ml-lg { margin-left: 16px; }
</style>

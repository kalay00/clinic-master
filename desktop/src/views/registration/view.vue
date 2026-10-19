<template>
  <div class="reg-view-page">
    <div class="page-head">
      <div class="page-title">挂号详情</div>
      <el-button :icon="Back" @click="onBack">返回</el-button>
    </div>
    <el-card class="page-card" shadow="never" v-loading="loading">
      <el-descriptions :column="2" border class="info-list">
        <el-descriptions-item label="挂号单号">{{ info.registration_no }}</el-descriptions-item>
        <el-descriptions-item label="患者姓名">{{ info.patient_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="档案号">{{ info.patient_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="挂号科室">{{ info.department_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="接诊医生">{{ info.doctor_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="挂号类型">{{ regTypeMap[info.registration_type] || info.registration_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="挂号费（元）">{{ fmt(info.registration_fee) }}</el-descriptions-item>
        <el-descriptions-item label="应收总额（元）">{{ fmt(info.price) }}</el-descriptions-item>
        <el-descriptions-item label="就诊日期">{{ info.registration_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="时段">{{ timeMap[info.time_period] || info.time_period || '-' }}</el-descriptions-item>
        <el-descriptions-item label="就诊状态">
          <el-tag :type="statusType(info.status)" size="small">{{ statusMap[info.status] || info.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="支付状态">
          <el-tag :type="payType(info.payment_status)" size="small">{{ payMap[info.payment_status] || info.payment_status || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ info.notes || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="footer-bar" v-if="info.status === 'pending'">
        <el-button type="primary" :icon="VideoPlay" @click="onVisit">进入就诊</el-button>
        <el-button type="warning" :icon="RefreshLeft" @click="onRefund">退号</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back, VideoPlay, RefreshLeft } from '@element-plus/icons-vue'
import { getRegistration, updateRegistration } from '@/api/registration'

defineOptions({ name: 'RegistrationView' })

const route = useRoute()
const router = useRouter()
const id = route.params.id
const loading = ref(false)
const info = reactive({})
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)
const regTypeMap = { normal: '普通号', expert: '专家号', emergency: '急诊号' }
const timeMap = { morning: '上午', afternoon: '下午' }
const statusMap = { pending: '未就诊', completed: '已就诊', cancelled: '已退号' }
const statusType = (s) => s === 'pending' ? 'warning' : (s === 'completed' ? 'success' : 'info')
const payMap = { unpaid: '未支付', paid: '已支付', refunded: '已退费', cancelled: '已取消' }
const payType = (s) => s === 'paid' ? 'success' : (s === 'unpaid' ? 'warning' : 'info')

async function load() {
  loading.value = true
  try {
    const d = await getRegistration(id)
    Object.assign(info, d)
  } catch (e) { ElMessage.error('加载挂号详情失败') }
  finally { loading.value = false }
}
const onVisit = () => router.push(`/consultation/western?regId=${id}`)
const onRefund = async () => {
  try { await ElMessageBox.confirm('确定退号？', '提示', { type: 'warning' }) } catch { return }
  try { await updateRegistration(id, { status: 'cancelled' }); ElMessage.success('退号成功'); load() } catch (e) { ElMessage.error('退号失败') }
}
const onBack = () => router.back()
onMounted(load)
</script>

<style lang="scss" scoped>
.reg-view-page { background: #f5f7fa; padding: 12px 16px 16px; }
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.page-title { font-size: 16px; font-weight: 600; color: #303133; }
.info-list { margin-bottom: 20px; }
.footer-bar { text-align: center; margin-top: 16px; display: flex; gap: 12px; justify-content: center; }
</style>

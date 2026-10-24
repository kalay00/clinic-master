<template>
  <div class="settings-form-page">
    <el-card class="page-card" shadow="never" v-loading="loading">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="挂号设置" name="registration">
        <el-form :model="cfg.registration" label-width="140px" style="max-width: 620px">
          <el-form-item label="最大提前预约天数">
            <el-input-number v-model="cfg.registration.max_advance_days" :min="0" :max="365" />
            <span class="tip">0 表示仅当天</span>
          </el-form-item>
          <el-form-item label="默认挂号费">
            <el-input-number v-model="cfg.registration.default_fee" :min="0" :precision="2" :step="1" />
            <span class="tip">元</span>
          </el-form-item>
          <el-form-item label="允许当天挂号">
            <el-switch v-model="cfg.registration.allow_same_day" />
          </el-form-item>
          <el-form-item label="就诊后自动完成">
            <el-switch v-model="cfg.registration.auto_complete_visit" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="处方设置" name="prescription">
        <el-form :model="cfg.prescription" label-width="140px" style="max-width: 620px">
          <el-form-item label="处方有效天数">
            <el-input-number v-model="cfg.prescription.validity_days" :min="1" :max="90" />
            <span class="tip">天</span>
          </el-form-item>
          <el-form-item label="默认处方类型">
            <el-select v-model="cfg.prescription.default_type" style="width: 200px">
              <el-option label="西药" value="western" />
              <el-option label="中药" value="chinese" />
            </el-select>
          </el-form-item>
          <el-form-item label="需要医生签名">
            <el-switch v-model="cfg.prescription.require_doctor_signature" />
          </el-form-item>
          <el-form-item label="保存后允许修改">
            <el-switch v-model="cfg.prescription.allow_edit_after_save" />
          </el-form-item>
          <el-form-item label="启用药师审核">
            <el-switch v-model="cfg.pharmacist_review_enabled" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="药品设置" name="drug">
        <el-form :model="cfg.drug_category" label-width="160px" style="max-width: 620px">
          <el-form-item label="启用西药/成药">
            <el-switch v-model="cfg.drug_category.western_enabled" />
            <span class="tip">关闭后，添加药品不显示「西/成药」，新开就诊不显示西药处方</span>
          </el-form-item>
          <el-form-item label="启用中药">
            <el-switch v-model="cfg.drug_category.chinese_enabled" />
            <span class="tip">关闭后，添加药品不显示「中药」，新开就诊不显示中药处方</span>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="打印设置" name="print">
        <el-form :model="cfg.print" label-width="160px" style="max-width: 620px">
          <el-form-item label="默认收费单模板">
            <el-select v-model="cfg.print.default_bill_template" clearable placeholder="请选择" style="width: 260px">
              <el-option v-for="t in templates.bill" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="默认处方单模板">
            <el-select v-model="cfg.print.default_prescription_template" clearable placeholder="请选择" style="width: 260px">
              <el-option v-for="t in templates.prescription" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="默认病历模板">
            <el-select v-model="cfg.print.default_medical_record_template" clearable placeholder="请选择" style="width: 260px">
              <el-option v-for="t in templates.medical_record" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="收费后自动打印">
            <el-switch v-model="cfg.print.auto_print_after_payment" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="系统安全" name="system">
        <el-form :model="cfg.system" label-width="140px" style="max-width: 620px">
          <el-form-item label="会话超时时间">
            <el-input-number v-model="cfg.system.session_timeout" :min="300" :step="300" />
            <span class="tip">秒</span>
          </el-form-item>
          <el-form-item label="密码最小长度">
            <el-input-number v-model="cfg.system.password_min_length" :min="6" :max="32" />
          </el-form-item>
          <el-form-item label="强制修改初始密码">
            <el-switch v-model="cfg.system.require_password_change" />
          </el-form-item>
          <el-form-item label="启用操作日志">
            <el-switch v-model="cfg.system.enable_audit_log" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="会员积分" name="loyalty">
        <el-form :model="cfg.loyalty" label-width="160px" style="max-width: 620px">
          <el-form-item label="消费1元赠送积分">
            <el-input-number v-model="cfg.loyalty.points_per_yuan" :min="0" :precision="2" :step="1" />
          </el-form-item>
          <el-form-item label="积分抵扣比例">
            <el-input-number v-model="cfg.loyalty.points_to_yuan" :min="0" :precision="4" :step="0.01" />
            <span class="tip">1 积分抵扣多少元</span>
          </el-form-item>
          <el-form-item label="充值赠送比例">
            <el-input-number v-model="cfg.loyalty.recharge_bonus_ratio" :min="0" :precision="4" :step="0.01" />
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <div class="form-actions">
      <el-button type="primary" :loading="submitting" @click="submit">保存设置</el-button>
      <el-button @click="fetchConfig">重置</el-button>
    </div>
  </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTenantConfig, updateTenantConfig } from '@/api/tenant'
import { getPrintTemplates } from '@/api/printTemplate'
import { fetchAllPages } from '@/utils/paging'
import { useDrugCategoryConfig } from '@/composables/useDrugCategoryConfig'

const { refresh: refreshDrugCategoryConfig } = useDrugCategoryConfig()

const activeTab = ref('registration')
const loading = ref(false)
const submitting = ref(false)

const defaultCfg = () => ({
  pharmacist_review_enabled: true,
  registration: { max_advance_days: 30, default_fee: 10, allow_same_day: true, auto_complete_visit: false },
  prescription: { validity_days: 7, default_type: 'western', require_doctor_signature: true, allow_edit_after_save: false },
  drug_category: { western_enabled: true, chinese_enabled: true },
  print: {
    default_bill_template: null,
    default_prescription_template: null,
    default_medical_record_template: null,
    auto_print_after_payment: false,
  },
  system: { session_timeout: 3600, password_min_length: 6, require_password_change: false, enable_audit_log: true },
  loyalty: { points_per_yuan: 1, points_to_yuan: 0.01, recharge_bonus_ratio: 0 },
})

const cfg = reactive(defaultCfg())
const templates = reactive({ bill: [], prescription: [], medical_record: [] })

function mergeConfig(data) {
  const base = defaultCfg()
  Object.keys(base).forEach(key => {
    const incoming = data?.[key]
    if (incoming && typeof incoming === 'object' && !Array.isArray(incoming)) {
      cfg[key] = { ...base[key], ...incoming }
    } else if (incoming !== undefined && incoming !== null) {
      cfg[key] = incoming
    } else {
      cfg[key] = base[key]
    }
  })
}

async function fetchConfig() {
  loading.value = true
  try {
    const data = await getTenantConfig()
    mergeConfig(data || {})
  } finally {
    loading.value = false
  }
}

async function fetchTemplates() {
  try {
    const items = await fetchAllPages(p => getPrintTemplates(p))
    templates.bill = items.filter(t => t.type === 'bill')
    templates.prescription = items.filter(t => t.type === 'prescription')
    templates.medical_record = items.filter(t => t.type === 'medical_record')
  } catch {
    // 模板接口异常不阻塞基础设置
  }
}

async function submit() {
  submitting.value = true
  try {
    await updateTenantConfig({
      pharmacist_review_enabled: cfg.pharmacist_review_enabled,
      registration: cfg.registration,
      prescription: cfg.prescription,
      drug_category: cfg.drug_category,
      print: cfg.print,
      system: cfg.system,
      loyalty: cfg.loyalty,
    })
    // 药品分类开关已变更，刷新共享缓存，让其他页面立即生效
    refreshDrugCategoryConfig()
    ElMessage.success('保存成功')
    fetchConfig()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchConfig()
  fetchTemplates()
})
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动 */
.settings-form-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
.page-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  :deep(.el-card__body) { flex: 1; overflow: auto; min-height: 0; padding: 16px 20px; }
}
</style>

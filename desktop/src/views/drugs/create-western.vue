<template>
  <div class="drug-form-page">
    <div class="page-header">
      <el-radio-group v-model="activeTab" size="large" class="tab-group">
        <el-radio-button v-if="westernEnabled" label="western">西/成药信息</el-radio-button>
        <el-radio-button v-if="chineseEnabled" label="herb">中药信息</el-radio-button>
      </el-radio-group>
      <div class="actions">
        <el-button type="primary" size="large" :icon="DocumentChecked" :loading="saving" @click="onSave">保存</el-button>
        <el-button size="large" :icon="Back" @click="onBack">返回</el-button>
      </div>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="drug-form">
      <h3 class="section-title">基本信息</h3>
      <div class="form-grid four-col">
        <el-form-item label="药品编码" prop="drug_code">
          <el-input v-model="form.drug_code" placeholder="自动生成/手动输入" />
        </el-form-item>
        <el-form-item label="药品条形码">
          <el-input v-model="form.barcode" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="药品通用名" prop="name">
          <el-input v-model="form.name" placeholder="必填" />
        </el-form-item>
        <el-form-item label="拼音码">
          <el-input v-model="form.pinyin_code" placeholder="请输入" />
        </el-form-item>

        <el-form-item label="药品分类" prop="category_id">
          <div class="select-plus">
            <el-select v-model="form.category_id" placeholder="请选择" filterable clearable style="flex:1">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <el-button :icon="Plus" circle class="plus-btn" @click="goDict('drug-category')" />
          </div>
        </el-form-item>
        <el-form-item label="药品规格" prop="specification">
          <el-input v-model="form.specification" placeholder="必填" />
        </el-form-item>
        <el-form-item label="药品剂型">
          <div class="select-plus">
            <el-select v-model="form.form" placeholder="请选择" filterable allow-create clearable style="flex:1">
              <el-option v-for="f in dosageForms" :key="f" :label="f" :value="f" />
            </el-select>
            <el-button :icon="Plus" circle class="plus-btn" @click="goDict('dosage-form')" />
          </div>
        </el-form-item>
        <el-form-item label="OTC药品">
          <el-radio-group v-model="form.is_otc">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="发票项目" prop="fee_item_id">
          <div class="select-plus">
            <el-select v-model="form.fee_item_id" placeholder="请选择" filterable allow-create clearable style="flex:1">
              <el-option v-for="f in feeItems" :key="f.id" :label="f.name" :value="f.id" />
            </el-select>
            <el-button :icon="Plus" circle class="plus-btn" @click="goDict('fee-item')" />
          </div>
        </el-form-item>
        <el-form-item label="批准文号">
          <el-input v-model="form.approval_no" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="生产厂家">
          <el-select v-model="form.manufacturer" placeholder="请选择/输入" filterable allow-create clearable>
            <el-option v-for="m in manufacturers" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="药品状态">
          <el-radio-group v-model="form.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </div>

      <h3 class="section-title">包装信息</h3>
      <div class="form-grid four-col">
        <el-form-item label="包装单位" prop="unit">
          <div class="select-plus">
            <el-select v-model="form.unit" placeholder="请选择" filterable allow-create clearable style="flex:1">
              <el-option v-for="u in units" :key="u" :label="u" :value="u" />
            </el-select>
            <el-button :icon="Plus" circle class="plus-btn" @click="goDict('unit')" />
          </div>
        </el-form-item>
        <template v-if="activeTab !== 'herb'">
          <el-form-item label="基本系数">
            <el-input-number v-model="form.base_coefficient" :min="0" :precision="4" controls-position="right" style="width: 100%" />
          </el-form-item>
          <el-form-item label="基本单位">
            <el-select v-model="form.base_unit" placeholder="请选择" filterable allow-create clearable>
              <el-option v-for="u in units" :key="u" :label="u" :value="u" />
            </el-select>
          </el-form-item>
          <el-form-item label="剂量系数">
            <el-input-number v-model="form.dose_coefficient" :min="0" :precision="4" controls-position="right" style="width: 100%" />
          </el-form-item>
          <el-form-item label="剂量单位">
            <el-select v-model="form.dose_unit" placeholder="请选择" filterable allow-create clearable>
              <el-option v-for="u in units" :key="u" :label="u" :value="u" />
            </el-select>
          </el-form-item>
        </template>
        <el-form-item label="采购价（元）">
          <el-input-number v-model="form.purchase_price" :min="0" :precision="2" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="零售价（元）" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item v-if="activeTab !== 'herb'" label="允许拆零">
          <el-radio-group v-model="form.allow_split">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="允许会员折扣">
          <el-radio-group v-model="form.allow_discount">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>
      </div>

      <h3 class="section-title">功效说明</h3>
      <div class="form-grid four-col">
        <el-form-item label="用法" prop="usage_id">
          <div class="select-plus">
            <el-select v-model="form.usage_id" placeholder="请选择" filterable allow-create clearable style="flex:1">
              <el-option v-for="u in usages" :key="u.id" :label="u.name" :value="u.id" />
            </el-select>
            <el-button :icon="Plus" circle class="plus-btn" @click="goDict('usage')" />
          </div>
        </el-form-item>
        <el-form-item label="单次用量" prop="single_dose">
          <div class="input-unit">
            <el-input-number v-model="form.single_dose" :min="0" :precision="2" controls-position="right" style="flex:1" />
            <el-select v-model="form.single_dose_unit" placeholder="单位" filterable allow-create style="width: 90px">
              <el-option v-for="u in doseUnits" :key="u" :label="u" :value="u" />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="频度">
          <div class="select-plus">
            <el-select v-model="form.frequency_id" placeholder="请选择" filterable allow-create clearable style="flex:1">
              <el-option v-for="f in frequencies" :key="f.id" :label="f.name" :value="f.id" />
            </el-select>
            <el-button :icon="Plus" circle class="plus-btn" @click="goDict('frequency')" />
          </div>
        </el-form-item>
        <template v-if="activeTab !== 'herb'">
          <el-form-item label="天数">
            <el-input-number v-model="form.days" :min="1" controls-position="right" style="width: 100%" />
          </el-form-item>
          <el-form-item label="总量">
            <div class="input-unit">
              <el-input-number v-model="form.total_qty" :min="0" :precision="2" controls-position="right" style="flex:1" />
              <el-select v-model="form.total_unit" placeholder="单位" filterable allow-create style="width: 90px">
                <el-option v-for="u in units" :key="u" :label="u" :value="u" />
              </el-select>
            </div>
          </el-form-item>
        </template>
      </div>

      <h3 class="section-title">其他信息</h3>
      <div class="form-grid four-col">
        <el-form-item label="库存下限">
          <el-input-number v-model="form.stock_min" :min="0" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存上限">
          <el-input-number v-model="form.stock_max" :min="0" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="货位号">
          <el-input v-model="form.location_no" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="有效期预警">
          <div class="input-suffix">
            <el-input-number v-model="form.expiry_warning_days" :min="0" controls-position="right" style="flex:1" />
            <span class="suffix">天</span>
          </div>
        </el-form-item>
        <el-form-item label="药品说明" class="full-width">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="备注" class="full-width">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入" />
        </el-form-item>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DocumentChecked, Back, Plus } from '@element-plus/icons-vue'
import { createDrug, updateDrug, getDrugCategories, getDrug } from '@/api/pharmacy'
import { fetchAllPages } from '@/utils/paging'
import { useDrugCategoryConfig } from '@/composables/useDrugCategoryConfig'

const { westernEnabled, chineseEnabled, load: loadDrugCategoryConfig } = useDrugCategoryConfig()

defineOptions({ name: 'DrugCreateWestern' })

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const activeTab = ref(route.name === 'DrugCreateHerb' || route.query.type === 'herb' ? 'herb' : 'western')
const isEdit = ref(false)
const categories = ref([])
const manufacturers = ref([])

const dosageForms = ref(['片剂', '胶囊', '颗粒', '注射剂', '口服液', '丸剂', '散剂', '软膏', '贴剂', '滴剂', '喷雾剂', '混悬剂'])
const units = ref(['盒', '瓶', '支', '袋', '板', '粒', '片', '瓶', 'g', 'mg', 'ml', '包'])
const doseUnits = ref(['片', '粒', 'mg', 'g', 'ml', '支', '袋', '包'])
const feeItems = ref([
  { id: '1', name: '西药费' },
  { id: '2', name: '中成药费' },
  { id: '3', name: '中草药费' },
  { id: '4', name: '检查费' },
  { id: '5', name: '治疗费' }
])
const usages = ref([
  { id: '1', name: '口服' },
  { id: '2', name: '外用' },
  { id: '3', name: '注射' },
  { id: '4', name: '含服' },
  { id: '5', name: '滴眼' },
  { id: '6', name: '煎服' }
])
const frequencies = ref([
  { id: '1', name: '一天1次' },
  { id: '2', name: '一天2次' },
  { id: '3', name: '一天3次' },
  { id: '4', name: '睡前' },
  { id: '5', name: '必要时' },
  { id: '6', name: '饭前' },
  { id: '7', name: '饭后' }
])

const form = reactive({
  drug_code: '',
  name: '',
  generic_name: '',
  barcode: '',
  pinyin_code: '',
  category_id: '',
  specification: '',
  form: '',
  is_otc: false,
  fee_item_id: '',
  approval_no: '',
  manufacturer: '',
  status: 'active',
  unit: '',
  base_coefficient: 1,
  base_unit: '',
  dose_coefficient: 1,
  dose_unit: '',
  purchase_price: 0,
  price: 0,
  allow_split: false,
  allow_discount: true,
  usage_id: '',
  single_dose: 1,
  single_dose_unit: activeTab.value === 'herb' ? 'g' : '片',
  frequency_id: '',
  days: 1,
  total_qty: 1,
  total_unit: '',
  stock_min: 0,
  stock_max: 0,
  location_no: '',
  expiry_warning_days: 30,
  description: '',
  remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入药品通用名', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择药品分类', trigger: 'change' }],
  specification: [{ required: true, message: '请输入药品规格', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择包装单位', trigger: 'change' }],
  price: [{ required: true, message: '请输入零售价', trigger: 'change' }],
  usage_id: [{ required: true, message: '请选择用法', trigger: 'change' }]
}

async function loadCategories() {
  try {
    categories.value = await fetchAllPages(p => getDrugCategories(p))
  } catch (e) { ElMessage.warning('加载药品分类失败') }
}

async function loadDetail() {
  const id = route.query.id || route.params.id
  if (!id) return
  isEdit.value = true
  try {
    const d = await getDrug(id)
    if (!d) return
    activeTab.value = d.drug_type === 'herb' ? 'herb' : 'western'
    Object.assign(form, {
      ...d,
      is_otc: !!d.is_otc,
      allow_split: !!d.allow_split,
      allow_discount: d.allow_discount !== false,
      single_dose_unit: d.single_dose_unit || (d.drug_type === 'herb' ? 'g' : '片')
    })
    // 分类回显：后端详情只返回旧分类名 category，需反查分类列表得到 category_id
    if (d.category_id) {
      form.category_id = d.category_id
    } else if (d.category) {
      const c = categories.value.find(c => c.name === d.category)
      form.category_id = c ? c.id : ''
    } else {
      form.category_id = ''
    }
  } catch (e) { ElMessage.error('加载药品详情失败') }
}

function goDict(type) {
  ElMessage.info(`请前往系统设置维护${type}字典`)
}

function onBack() {
  router.back()
}

async function onSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = {
      ...form,
      drug_type: activeTab.value === 'herb' ? 'herb' : 'western',
      category: categories.value.find(c => c.id === form.category_id)?.name || form.category || '',
      purchase_price: form.purchase_price || 0,
      price: form.price || 0,
      days: activeTab.value === 'herb' ? undefined : (form.days || 1),
      total_qty: activeTab.value === 'herb' ? undefined : (form.total_qty || 1)
    }
    if (isEdit.value && route.query.id) {
      await updateDrug(route.query.id, payload)
      ElMessage.success('保存成功')
    } else {
      await createDrug(payload)
      ElMessage.success('新增成功')
    }
    router.push('/drugs/maintain')
  } catch (e) {
    const d = e?.response?.data?.detail
    ElMessage.error((Array.isArray(d) ? d[0].msg : d) || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadDrugCategoryConfig()
  // 当前药品类型被关闭时，自动切到仍启用的类型
  if (activeTab.value === 'western' && !westernEnabled.value && chineseEnabled.value) {
    activeTab.value = 'herb'
  } else if (activeTab.value === 'herb' && !chineseEnabled.value && westernEnabled.value) {
    activeTab.value = 'western'
  }
  await loadCategories()
  await loadDetail()
})
</script>

<style lang="scss" scoped>
.drug-form-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.tab-group :deep(.el-radio-button__inner) {
  min-width: 120px;
}
.drug-form {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.section-title {
  color: #5b7cff;
  font-size: 16px;
  font-weight: 600;
  margin: 24px 0 16px;
  padding-left: 10px;
  border-left: 4px solid #5b7cff;
}
.section-title:first-child { margin-top: 0; }
.form-grid {
  display: grid;
  gap: 16px;
}
.form-grid.four-col {
  grid-template-columns: repeat(4, 1fr);
}
.form-grid .full-width {
  grid-column: span 2;
}
.select-plus {
  display: flex;
  gap: 8px;
  align-items: center;
}
.plus-btn {
  flex-shrink: 0;
}
.input-unit {
  display: flex;
  gap: 8px;
  align-items: center;
}
.input-suffix {
  display: flex;
  gap: 8px;
  align-items: center;
}
.suffix {
  color: #666;
  white-space: nowrap;
}
@media (max-width: 1400px) {
  .form-grid.four-col { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 1100px) {
  .form-grid.four-col { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .form-grid.four-col { grid-template-columns: 1fr; }
  .form-grid .full-width { grid-column: span 1; }
}
</style>

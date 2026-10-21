<template>
  <div class="consultation-page">
    <!-- 顶部：病历 / 处方（先填病历，保存后切换到处方） -->
    <el-tabs v-model="topTab" class="consult-top-tabs" @tab-change="onTopTabChange">
      <el-tab-pane label="病历" name="record" />
      <el-tab-pane label="处方" name="western" />
    </el-tabs>

    <!-- 患者信息 -->
    <el-card class="patient-card" shadow="never">
      <el-form :model="patient" label-width="80px" class="patient-form">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="患者姓名" required>
              <el-input v-model="patient.name" placeholder="患者姓名/手机号/证件号/卡号">
                <template #append>
                  <el-button :icon="Search" @click="onSearchPatient" />
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者卡号">
              <el-input v-model="patient.cardNo" placeholder="请输入病人卡号" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="患者年龄" required>
              <el-input v-model="patient.age" placeholder="请输入数字">
                <template #append>岁</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="出生日期" required>
              <el-date-picker v-model="patient.birthday" type="date" placeholder="请选择" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="性别" required>
              <el-select v-model="patient.gender" placeholder="请选择" style="width: 100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="手机号码">
              <el-input v-model="patient.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="证件号码">
              <el-input v-model="patient.idCard" placeholder="请输入证件号码" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="接诊类型" required>
              <el-select v-model="patient.visitType" placeholder="请选择" style="width: 100%">
                <el-option label="初诊" value="first" />
                <el-option label="复诊" value="return" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="地址">
              <el-cascader v-model="patient.region" :options="regionOptions" placeholder="请选择" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="18">
            <el-form-item label="详细地址">
              <el-input v-model="patient.address" placeholder="请输入详细地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="诊断" required>
              <el-input v-model="patient.diagnosis">
                <template #append>
                  <el-button :icon="Search" @click="onPickDiagnosis" />
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="医嘱">
              <el-input v-model="patient.advice">
                <template #append>
                  <el-button :icon="Search" @click="onPickAdvice" />
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 处方标签 -->
    <el-card class="prescription-card" shadow="never">
      <div class="prescription-tabs">
        <el-dropdown trigger="click" @command="addPrescription" class="add-prescription">
          <el-button type="primary" plain size="small">
            添加处方<el-icon class="el-icon--right"><i class="el-icon-arrow-down" /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="westernEnabled" command="western">西药处方</el-dropdown-item>
              <el-dropdown-item v-if="chineseEnabled" command="chinese">中药处方</el-dropdown-item>
              <el-dropdown-item command="inspection">检查项目</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-tabs v-model="activePrescription" type="card" class="rx-tabs" @tab-change="onRxTabChange">
          <el-tab-pane
            v-for="tab in prescriptionTabs"
            :key="tab.key"
            :name="tab.key"
            :closable="prescriptionTabs.length > 1"
            @tab-remove="removePrescription"
          >
            <template #label>{{ tab.name }}</template>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 主体：处方表格 + 药品选择（按当前 tab 类型切换内容，不切页） -->
      <div class="prescription-main">
        <div class="prescription-left">
          <div class="rx-header">
            <span class="rx-title">Rp</span>
            <el-button size="small" :icon="SetUp" @click="goBatch">批量设置</el-button>
          </div>

          <!-- 西药 / 中药 共用药品明细（列略不同） -->
          <template v-if="activeTabType !== 'inspection'">
            <el-table :data="prescriptionList" border class="rx-table" empty-text="请从右侧选择药品">
              <el-table-column type="selection" width="40" />
              <el-table-column type="index" label="序号" width="55" />
              <el-table-column label="组号" width="70">
                <template #default="{ row }">
                  <el-input v-model="row.group" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="name" label="名称" min-width="120" />
              <el-table-column v-if="activeTabType === 'chinese'" label="脚注" width="90">
                <template #default="{ row }">
                  <el-input v-model="row.footnote" size="small" placeholder="脚注" />
                </template>
              </el-table-column>
              <el-table-column label="单次用量" width="100">
                <template #default="{ row }">
                  <div class="input-unit">
                    <el-input v-model="row.dosage" size="small" />
                    <span>{{ row.dosageUnit }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="用法" width="100">
                <template #default="{ row }">
                  <el-select v-model="row.usage" size="small">
                    <el-option label="口服" value="口服" />
                    <el-option label="外用" value="外用" />
                    <el-option label="注射" value="注射" />
                    <el-option label="冲服" value="冲服" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="频度" width="110">
                <template #default="{ row }">
                  <el-select v-model="row.frequency" size="small">
                    <el-option label="一天1次" value="一天1次" />
                    <el-option label="一天2次" value="一天2次" />
                    <el-option label="一天3次" value="一天3次" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="天数" width="70">
                <template #default="{ row }">
                  <el-input v-model="row.days" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="总量" width="110">
                <template #default="{ row }">
                  <div class="input-unit">
                    <el-input v-model="row.total" size="small" />
                    <el-select v-model="row.totalUnit" size="small" class="unit-select">
                      <el-option label="瓶" value="瓶" />
                      <el-option label="片" value="片" />
                      <el-option label="支" value="支" />
                      <el-option label="剂" value="剂" />
                    </el-select>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="单价" width="70" />
              <el-table-column label="编辑" width="60" align="center">
                <template #default="{ $index }">
                  <el-button link type="danger" :icon="Delete" @click="removeDrug($index)" />
                </template>
              </el-table-column>
            </el-table>
          </template>

          <!-- 检查项目明细 -->
          <template v-else>
            <el-table :data="prescriptionList" border class="rx-table" empty-text="请从右侧选择检查项目">
              <el-table-column type="index" label="序号" width="55" />
              <el-table-column prop="name" label="项目名称" min-width="140" />
              <el-table-column label="部位" width="110">
                <template #default="{ row }">
                  <el-input v-model="row.position" size="small" placeholder="部位" />
                </template>
              </el-table-column>
              <el-table-column label="单价" width="90">
                <template #default="{ row }">
                  <el-input v-model="row.price" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="数量" width="70">
                <template #default="{ row }">
                  <el-input v-model="row.qty" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="金额" width="80">
                <template #default="{ row }">
                  {{ ((Number(row.price) || 0) * (Number(row.qty) || 1)).toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column label="编辑" width="60" align="center">
                <template #default="{ $index }">
                  <el-button link type="danger" :icon="Delete" @click="removeDrug($index)" />
                </template>
              </el-table-column>
            </el-table>
          </template>
        </div>

        <div class="prescription-right">
          <div class="drug-toolbar">
            <el-select v-model="drugCategory" placeholder="药品分类" style="width: 120px">
              <el-option label="全部分类" value="all" />
              <el-option
                v-for="c in drugCategories"
                :key="c.id"
                :label="c.name"
                :value="c.id"
              />
            </el-select>
            <el-input
              v-model="drugKeyword"
              :placeholder="activeTabType === 'inspection' ? '输入检查项目名称' : '输入药品中文或拼音名称'"
              :prefix-icon="Search"
              class="drug-search"
            />
          </div>

          <!-- 药品库（西药/中药） -->
          <el-table
            v-if="activeTabType !== 'inspection'"
            ref="drugTableRef"
            :data="filteredDrugs"
            border
            class="drug-table"
            height="360"
            v-loading="drugLoading"
            @row-click="toggleDrug"
            @scroll="onDrugScroll"
          >
            <el-table-column prop="name" label="名称" min-width="110" />
            <el-table-column prop="spec" label="规格" width="70" />
            <el-table-column prop="stock" label="库存" width="60" />
            <el-table-column prop="price" label="价格" width="60" />
            <template #append>
              <div v-if="drugLoadingMore" class="drug-load-more">加载中…</div>
              <div v-else-if="drugFinished" class="drug-load-more">没有更多了</div>
            </template>
          </el-table>

          <!-- 检查项目库 -->
          <el-table
            v-else
            ref="inspectionTableRef"
            :data="filteredDrugs"
            border
            class="drug-table"
            height="360"
            empty-text="暂无检查项目"
            @row-click="toggleDrug"
            @scroll="onDrugScroll"
          >
            <el-table-column prop="name" label="项目名称" min-width="140" />
            <el-table-column prop="position" label="部位" width="100" />
            <el-table-column prop="price" label="价格" width="70" />
            <template #append>
              <div v-if="drugLoadingMore" class="drug-load-more">加载中…</div>
              <div v-else-if="drugFinished" class="drug-load-more">没有更多了</div>
            </template>
          </el-table>
        </div>
      </div>

      <!-- 处方合计 -->
      <div class="prescription-footer">
        <div class="footer-left">
          <el-button type="success" size="small" @click="goExtraFee">+ 附加费用</el-button>
          <span class="footer-label">科室：</span>
          <el-select v-model="dept" placeholder="科室" size="small" style="width: 110px">
            <el-option label="全科" value="general" />
          </el-select>
          <span class="footer-label">接诊医生：</span>
          <el-select v-model="doctorId" placeholder="请选择接诊医生" size="small" style="width: 150px">
            <el-option
              v-for="d in doctors"
              :key="d.id"
              :label="d.name + (d.title ? `（${d.title}）` : '')"
              :value="d.id"
            />
          </el-select>
        </div>
        <div class="footer-right">
          此方合计：<span class="total-amount">{{ prescriptionTotal.toFixed(2) }}</span> 元； 共
          {{ prescriptionTabs.length }} 个处方，共计：<span class="total-amount">{{ allTotal.toFixed(2) }}</span> 元
        </div>
      </div>
    </el-card>

    <!-- 底部操作栏 -->
    <div class="bottom-bar">
      <el-button :icon="Document" @click="goTemplateCall">处方调用</el-button>
      <el-button :icon="Printer" @click="printRx">打印处方</el-button>
      <el-button :icon="Files" @click="goTemplateCreate">存为模板</el-button>
      <el-button type="primary" :icon="Check" @click="onSave">保存</el-button>
      <el-button type="warning" :icon="Money" @click="goCharge">收费</el-button>
      <el-button type="danger" :icon="SwitchButton" @click="goEnd">结束就诊</el-button>
    </div>

    <!-- 弹窗 -->
    <PrescriptionTemplateCall v-model="showRxTemplateCall" @confirm="onRxTemplateConfirm" />
    <PrescriptionTemplateCreate v-model="showRxTemplateCreate" />
    <WesternBatch v-model="showBatch" @confirm="onBatchConfirm" />
    <WesternExtra v-model="showExtra" @confirm="onExtraConfirm" />
    <ChargeConfirm v-model="showChargeConfirm" @confirm="onChargeConfirm" />

    <!-- 患者查询弹窗：直接就诊（无挂号单）时查询并回填患者信息 -->
    <el-dialog v-model="showPatientSearch" title="查询患者" width="760px" append-to-body>
      <div class="patient-search-bar">
        <el-input
          v-model="patientKeyword"
          placeholder="姓名 / 手机号 / 证件号 / 档案号"
          clearable
          style="width: 280px"
          @keyup.enter="onPatientSearch"
        />
        <el-button type="primary" :icon="Search" @click="onPatientSearch">查询</el-button>
        <span class="patient-search-tip">点击表格行即选中并回填患者信息</span>
      </div>
      <el-table
        :data="patientResults"
        border
        height="380"
        v-loading="patientSearching"
        @row-click="onPickPatient"
      >
        <el-table-column prop="patient_no" label="档案号" width="130" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="性别" width="70">
          <template #default="{ row }">{{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '-' }}</template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="id_card" label="证件号" min-width="170" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search, SetUp, Delete,
  Document, Printer, Files, Check, Money, SwitchButton,
} from '@element-plus/icons-vue'
import PrescriptionTemplateCall from '@/views/consultation/prescription-template-call.vue'
import PrescriptionTemplateCreate from '@/views/consultation/prescription-template-create.vue'
import WesternBatch from '@/views/consultation/western-batch.vue'
import WesternExtra from '@/views/consultation/western-extra.vue'
import ChargeConfirm from '@/views/consultation/charge-confirm.vue'
import { getRegistration } from '@/api/registration'
import { getPatient, getPatients, getPatientVisits } from '@/api/patient'
import { getDoctors } from '@/api/doctor'
import { getDrugs, getDrugCategories } from '@/api/pharmacy'
import { getDictionaryList } from '@/api/dictionary'
import { fetchAllPages } from '@/utils/paging'
import { createPrescription } from '@/api/treatment'
import { useDrugCategoryConfig } from '@/composables/useDrugCategoryConfig'

const { westernEnabled, chineseEnabled, load: loadDrugCategoryConfig } = useDrugCategoryConfig()

const router = useRouter()
const route = useRoute()

// 患者信息（提前声明，确保模板渲染时已初始化）
const patient = reactive({
  name: '', cardNo: '', age: '', birthday: '', gender: '', phone: '',
  idCard: '', visitType: '', region: [], address: '', diagnosis: '', advice: '',
})

// 当前就诊上下文（来自挂号）
const regId = computed(() => route.query.regId || '')
const patientId = ref('')
const registrationId = ref('')
// 接诊医生（保存处方必填）
const doctorId = ref('')
const doctors = ref([])

const loadDoctors = async () => {
  try {
    const res = await getDoctors({ page: 1, page_size: 100 })
    doctors.value = res.items || []
  } catch (e) { /* 医生列表加载失败不影响开方 */ }
}

// 根据出生日期计算年龄
const calcAge = (birthday) => {
  if (!birthday) return ''
  const b = new Date(birthday)
  if (Number.isNaN(b.getTime())) return ''
  const now = new Date()
  let age = now.getFullYear() - b.getFullYear()
  const m = now.getMonth() - b.getMonth()
  if (m < 0 || (m === 0 && now.getDate() < b.getDate())) age -= 1
  return age >= 0 && age < 150 ? String(age) : ''
}

// 性别归一化：兼容 male/female、M/F、男/女 等历史写法，统一为表单选项值
const normalizeGender = (g) => {
  if (!g) return ''
  if (g === 'male' || g === '男' || g === 'M') return 'male'
  if (g === 'female' || g === '女' || g === 'F') return 'female'
  return g
}

// 患者信息回填（挂号带入 / 弹窗查询共用）；仅覆盖有值的字段，避免空值冲掉已有数据
const applyPatientToForm = (p) => {
  if (!p) return
  patient.name = p.name || patient.name
  patient.cardNo = p.patient_no || patient.cardNo
  patient.phone = p.phone || patient.phone
  patient.gender = normalizeGender(p.gender) || patient.gender
  const birthday = p.birth_date || (p.birthday ? String(p.birthday).slice(0, 10) : '')
  patient.birthday = birthday || patient.birthday
  patient.idCard = p.id_card || patient.idCard
  patient.address = p.address || patient.address
  if (p.age != null && p.age !== '') patient.age = String(p.age)
  else if (!patient.age && patient.birthday) patient.age = calcAge(patient.birthday)
}

// 按患者ID补全患者信息（详情接口失败时保留调用方传入的兜底数据）
const fillPatientById = async (id, fallback = {}) => {
  if (!id) return
  try {
    const detail = await getPatient(id)
    applyPatientToForm({ ...fallback, ...(detail || {}) })
  } catch (e) { /* 详情失败：保留兜底 */ applyPatientToForm(fallback) }
  // 有历史就诊记录则默认复诊，否则初诊
  try {
    const visits = await getPatientVisits(id)
    const list = Array.isArray(visits) ? visits : (visits?.items || [])
    patient.visitType = list.length > 0 ? 'return' : 'first'
  } catch (e) { /* 就诊历史不可得时不改接诊类型 */ }
}

onMounted(async () => {
  // 先读取药品分类开关，确保处方 tab 在渲染药品前已按开关过滤
  await loadDrugCategoryConfig()
  applyDrugCategoryTabs()
  await loadDoctors()
  if (regId.value) {
    // 场景一：从挂号记录点「就诊」进入，按挂号单自动填充患者信息
    try {
      const reg = await getRegistration(regId.value)
      registrationId.value = reg.id || regId.value
      patientId.value = reg.patient_id || ''
      // 挂号单上的医生作为默认接诊医生
      if (reg.doctor_id) doctorId.value = reg.doctor_id
      // 挂号返回的富化字段先兜底，再拉患者详情补全年龄/性别/证件/地址等
      await fillPatientById(patientId.value, {
        name: reg.patient_name,
        patient_no: reg.patient_no,
        phone: reg.patient_phone,
      })
    } catch (e) { /* 忽略：未带挂号参数时保持空白，走直接就诊流程 */ }
  } else if (route.query.patientId) {
    // 从病历页保存后切换过来：按患者ID恢复患者信息
    patientId.value = route.query.patientId
    await fillPatientById(patientId.value)
  }
  await loadDrugCategories()
  reloadDrugs()
})

// 药品库（真实接口，默认20条，滚动加载更多）
const mapDrug = (d) => ({
  id: d.id,
  name: d.name,
  spec: d.spec || d.specification || '',
  stock: d.stock ?? 0,
  price: d.price ?? 0,
})

// 重置并加载第一页
const reloadDrugs = async () => {
  if (activeTabType.value === 'inspection') return reloadInspections()
  drugPage.value = 1
  drugTotal.value = 0
  drugList.value = []
  drugLoading.value = true
  try {
    const res = await getDrugs({
      page: drugPage.value,
      pageSize: drugPageSize,
      category: currentDrugCategory.value,
      search: drugKeyword.value.trim() || undefined,
    })
    drugList.value = (res.items || []).map(mapDrug)
    drugTotal.value = res.total ?? drugList.value.length
    drugPage.value += 1
  } catch (e) {
    ElMessage.error('药品库加载失败')
    drugList.value = []
  } finally {
    drugLoading.value = false
  }
}

// 滚动加载更多
const loadMoreDrugs = async () => {
  if (drugLoading.value || drugLoadingMore.value || drugFinished.value) return
  drugLoadingMore.value = true
  try {
    const res = await getDrugs({
      page: drugPage.value,
      pageSize: drugPageSize,
      category: currentDrugCategory.value,
      search: drugKeyword.value.trim() || undefined,
    })
    const items = (res.items || []).map(mapDrug)
    if (!items.length) { drugTotal.value = drugList.value.length; return }
    drugList.value = [...drugList.value, ...items]
    drugTotal.value = res.total ?? drugList.value.length
    drugPage.value += 1
  } catch (e) {
    ElMessage.error('药品库加载失败')
  } finally {
    drugLoadingMore.value = false
  }
}

// 检查项目（字典接口，按 inspection 分类分页）
const mapInspection = (d) => ({
  id: d.id,
  name: d.content,
  position: d.sub_type || '',
  price: d.code || '0',
})
const inspectionPage = ref(1)
const inspectionTotal = ref(0)
const inspectionLoadingMore = ref(false)
const inspectionFinished = computed(() => inspectionList.value.length >= inspectionTotal.value && inspectionTotal.value > 0)

const reloadInspections = async () => {
  inspectionPage.value = 1
  inspectionTotal.value = 0
  inspectionList.value = []
  drugLoading.value = true
  try {
    const res = await getDictionaryList({ page: inspectionPage.value, pageSize: drugPageSize, category: 'inspection' })
    inspectionList.value = (res.items || []).map(mapInspection)
    inspectionTotal.value = res.total ?? inspectionList.value.length
    inspectionPage.value += 1
  } catch (e) {
    ElMessage.error('检查项目加载失败')
    inspectionList.value = []
  } finally {
    drugLoading.value = false
  }
}
const loadMoreInspections = async () => {
  if (drugLoading.value || inspectionLoadingMore.value || inspectionFinished.value) return
  inspectionLoadingMore.value = true
  try {
    const res = await getDictionaryList({ page: inspectionPage.value, pageSize: drugPageSize, category: 'inspection' })
    const items = (res.items || []).map(mapInspection)
    if (!items.length) { inspectionTotal.value = inspectionList.value.length; return }
    inspectionList.value = [...inspectionList.value, ...items]
    inspectionTotal.value = res.total ?? inspectionList.value.length
    inspectionPage.value += 1
  } catch (e) {
    ElMessage.error('检查项目加载失败')
  } finally {
    inspectionLoadingMore.value = false
  }
}

// 弹窗显隐
const showRxTemplateCall = ref(false)
const showRxTemplateCreate = ref(false)
const showBatch = ref(false)
const showExtra = ref(false)
const showChargeConfirm = ref(false)


// 顶部 Tab
const topTab = ref('western')
const onTopTabChange = (name) => {
  // 返回病历时携带挂号/患者上下文，避免患者信息丢失
  if (name === 'record') {
    const q = {}
    if (regId.value) q.regId = regId.value
    if (patientId.value) q.patientId = patientId.value
    router.push({ path: '/consultation/record', query: q })
  }
}

// 跨页保留就诊上下文（供病历页互跳使用）
const consultationQuery = () => {
  const q = {}
  if (regId.value) q.regId = regId.value
  if (patientId.value) q.patientId = patientId.value
  return q
}

const regionOptions = [
  { value: 'gd', label: '广东省', children: [{ value: 'sz', label: '深圳市' }] },
]

// 处方标签（全部在本页内切换，不跳页）
const prescriptionTabs = ref([
  { key: 'western-1', name: '西药处方1', type: 'western' },
  { key: 'chinese-1', name: '中药处方1', type: 'chinese' },
  { key: 'inspection-1', name: '检查项目1', type: 'inspection' },
])
const activePrescription = ref('western-1')
const activeTab = computed(() => prescriptionTabs.value.find(t => t.key === activePrescription.value) || prescriptionTabs.value[0])
const activeTabType = computed(() => activeTab.value.type)

// 按「基础设置 - 药品设置」的开关过滤可用的处方类型
function applyDrugCategoryTabs() {
  const kept = prescriptionTabs.value.filter(t => {
    if (t.type === 'western') return westernEnabled.value
    if (t.type === 'chinese') return chineseEnabled.value
    return true
  })
  prescriptionTabs.value = kept.length ? kept : [{ key: 'inspection-1', name: '检查项目1', type: 'inspection' }]
  if (!prescriptionTabs.value.some(t => t.key === activePrescription.value)) {
    activePrescription.value = prescriptionTabs.value[0].key
  }
}

const onRxTabChange = (key) => {
  // 仅切换当前页内容，不做路由跳转
  activePrescription.value = key
}

const addPrescription = (type) => {
  if (type === 'western') {
    const idx = prescriptionTabs.value.filter(t => t.type === 'western').length + 1
    const key = `western-${idx}`
    prescriptionTabs.value.push({ key, name: `西药处方${idx}`, type: 'western' })
    if (!prescriptionData[key]) prescriptionData[key] = []
    activePrescription.value = key
  } else if (type === 'chinese') {
    const idx = prescriptionTabs.value.filter(t => t.type === 'chinese').length + 1
    const key = `chinese-${idx}`
    prescriptionTabs.value.push({ key, name: `中药处方${idx}`, type: 'chinese' })
    if (!prescriptionData[key]) prescriptionData[key] = []
    activePrescription.value = key
  } else if (type === 'inspection') {
    const idx = prescriptionTabs.value.filter(t => t.type === 'inspection').length + 1
    const key = `inspection-${idx}`
    prescriptionTabs.value.push({ key, name: `检查项目${idx}`, type: 'inspection' })
    if (!prescriptionData[key]) prescriptionData[key] = []
    activePrescription.value = key
  }
}

const removePrescription = (key) => {
  if (prescriptionTabs.value.length <= 1) return
  const idx = prescriptionTabs.value.findIndex(t => t.key === key)
  prescriptionTabs.value.splice(idx, 1)
  // 同时清理该处方的明细
  delete prescriptionData[key]
  if (activePrescription.value === key) {
    activePrescription.value = prescriptionTabs.value[0].key
  }
}

// 每个处方 tab 独立维护明细
const prescriptionData = reactive({})
const defaultDrugRow = () => ({
  id: Date.now() + Math.random(),
  name: '', group: '1', dosage: '1', dosageUnit: '片', usage: '口服',
  frequency: '一天1次', days: '1', total: '1', totalUnit: '瓶', price: '0',
})
// 左侧默认空白，由右侧点击选择后追加
prescriptionTabs.value.forEach(t => {
  prescriptionData[t.key] = []
})

// 当前 tab 的明细
const prescriptionList = computed({
  get: () => prescriptionData[activePrescription.value] || [],
  set: (val) => { prescriptionData[activePrescription.value] = val },
})

// 确保每个处方 tab 都有明细容器：新建 tab / 切换 tab 时按需创建，
// 否则 getter 返回临时空数组，右侧选药 push 进去会丢失（页面无反应）
watch(activePrescription, (key) => {
  if (key && !prescriptionData[key]) prescriptionData[key] = []
}, { immediate: true })

const prescriptionTotal = computed(() =>
  prescriptionList.value.reduce((sum, item) => sum + (Number(item.price) * (Number(item.qty) || 1) || 0), 0)
)
const allTotal = computed(() =>
  Object.values(prescriptionData).reduce(
    (sum, list) => sum + (list || []).reduce((s, item) => s + (Number(item.price) * (Number(item.qty) || 1) || 0), 0),
    0
  )
)

const removeDrug = (idx) => {
  prescriptionList.value.splice(idx, 1)
}

// 药品 / 检查项目选择（全部接入真实接口）
const drugCategory = ref('')
const drugKeyword = ref('')
const drugCategories = ref([])   // 药品分类（字典维护-药品分类，DrugCategory 表）

async function loadDrugCategories() {
  try {
    const list = await fetchAllPages(p => getDrugCategories(p))
    drugCategories.value = list.filter(c => c.status !== 'inactive')
  } catch (e) { /* 分类加载失败时保持空下拉，不影响选药 */ }
}
const drugList = ref([])          // 当前分类已加载的药品（分页追加）
const inspectionList = ref([])    // 检查项目（字典接口分页追加）
const drugTableRef = ref(null)
const inspectionTableRef = ref(null)

// 分页状态
const drugPage = ref(1)
const drugPageSize = 20
const drugTotal = ref(0)
const drugLoading = ref(false)      // 首次 / 重置加载
const drugLoadingMore = ref(false)  // 滚动追加加载
const drugFinished = computed(() => drugList.value.length >= drugTotal.value && drugTotal.value > 0)

const currentDrugCategory = computed(() => {
  if (activeTabType.value === 'inspection') return ''
  if (drugCategory.value && drugCategory.value !== 'all') return drugCategory.value
  return '' // 全部分类：不加过滤；此前回退 activeTabType('western'/'chinese') 会命中旧分类名匹配而查不到数据
})

const filteredDrugs = computed(() => {
  if (activeTabType.value === 'inspection') return inspectionList.value
  return drugList.value
})

// 滚动到底加载更多
const onDrugScroll = ({ scrollTop, scrollHeight, clientHeight }) => {
  if (activeTabType.value === 'inspection') {
    if (scrollTop + clientHeight >= scrollHeight - 30) loadMoreInspections()
  } else {
    if (scrollTop + clientHeight >= scrollHeight - 30) loadMoreDrugs()
  }
}

const isSelected = (id) => prescriptionList.value.some(item => item.id === id)

const toggleDrug = (item) => {
  if (isSelected(item.id)) {
    prescriptionList.value = prescriptionList.value.filter(row => row.id !== item.id)
    return
  }
  if (activeTabType.value === 'inspection') {
    prescriptionList.value.push({
      id: item.id,
      name: item.name,
      position: item.position || '',
      price: String(item.price),
      qty: '1',
    })
  } else {
    prescriptionList.value.push({
      id: item.id,
      name: item.name,
      group: '1',
      dosage: '1',
      dosageUnit: '片',
      usage: '口服',
      frequency: '一天1次',
      days: '1',
      total: '1',
      totalUnit: '瓶',
      price: String(item.price),
    })
  }
}


// 底部按钮跳转
const dept = ref('general')
const goBatch = () => { showBatch.value = true }
const goExtraFee = () => { showExtra.value = true }
const goTemplateCall = () => { showRxTemplateCall.value = true }
const goTemplateCreate = () => { showRxTemplateCreate.value = true }
const goCharge = () => router.push('/consultation/charge')
const goEnd = () => { showChargeConfirm.value = true }

// 直接就诊：查询患者并回填
const showPatientSearch = ref(false)
const patientKeyword = ref('')
const patientResults = ref([])
const patientSearching = ref(false)

const onPatientSearch = async () => {
  patientSearching.value = true
  try {
    const res = await getPatients({ keyword: patientKeyword.value.trim() || undefined, page: 1, page_size: 20 })
    patientResults.value = res.items || []
  } catch (e) {
    ElMessage.error('患者查询失败')
  } finally {
    patientSearching.value = false
  }
}

const onPickPatient = async (row) => {
  patientId.value = row.id
  // 与挂号带入一致：拉详情补全 + 按就诊历史推断初/复诊
  await fillPatientById(row.id, row)
  showPatientSearch.value = false
  ElMessage.success(`已选择患者：${row.name || ''}`)
}

const onSearchPatient = () => {
  showPatientSearch.value = true
  if (!patientResults.value.length) onPatientSearch()
}
const onPickDiagnosis = () => ElMessage.info('打开诊断选择')
const onPickAdvice = () => ElMessage.info('打开医嘱选择')

const printRx = () => {
  ElMessage.info('调用浏览器打印')
  window.print()
}
const onSave = async () => {
  if (!patientId.value) {
    ElMessage.warning('请先选择就诊患者')
    return
  }
  if (!doctorId.value) {
    ElMessage.warning('请先选择接诊医生')
    return
  }
  if (!prescriptionTabs.value.some(t => (prescriptionData[t.key] || []).length)) {
    ElMessage.warning('请先从右侧选择药品')
    return
  }
  try {
    // 病历已在病历页保存，此处仅按处方 tab 保存处方
    for (const tab of prescriptionTabs.value) {
      const list = prescriptionData[tab.key] || []
      if (!list.length) continue
      if (tab.type === 'inspection') {
        const total = list.reduce((s, it) => s + Number(it.price || 0) * (Number(it.qty) || 1), 0)
        await createPrescription({
          patient_id: patientId.value,
          doctor_id: doctorId.value,
          prescription_type: 'inspection',
          total_amount: Number(total.toFixed(2)),
          items: list.map(it => ({
            name: it.name,
            position: it.position,
            price: it.price,
            qty: it.qty,
          })),
        })
      } else {
        const total = list.reduce((s, it) => s + Number(it.price || 0) * (Number(it.total) || 1), 0)
        await createPrescription({
          patient_id: patientId.value,
          doctor_id: doctorId.value,
          prescription_type: tab.type,
          total_amount: Number(total.toFixed(2)),
          items: list.map(it => ({
            drug_id: it.id,
            name: it.name,
            spec: it.spec,
            group: it.group,
            dosage: it.dosage,
            dosage_unit: it.dosageUnit,
            usage: it.usage,
            frequency: it.frequency,
            days: it.days,
            total: it.total,
            total_unit: it.totalUnit,
            quantity: Number(it.total) || 1,
            price: it.price,
          })),
        })
      }
    }
    ElMessage.success('处方保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const onRxTemplateConfirm = (tpl) => {
  tpl.items.forEach((it) => {
    prescriptionList.value.push({
      id: Date.now() + Math.random(),
      name: it.name,
      group: '1',
      dosage: '1',
      dosageUnit: '片',
      usage: it.usage || '口服',
      frequency: it.frequency || '一天1次',
      days: it.days || '1',
      total: '1',
      totalUnit: '瓶',
      price: it.price || '0',
    })
  })
}
const onBatchConfirm = (rows) => {
  if (rows.length) {
    const r = rows[0]
    prescriptionList.value.forEach((it) => {
      it.dosage = r.dosage
      it.usage = r.usage
      it.frequency = r.frequency
      it.days = r.days
      it.total = r.total
    })
  }
}
const onExtraConfirm = () => {}
const onChargeConfirm = () => {}

// 切换处方分类 / 药品分类 / 关键词时重置并重新加载
// 注意：必须在被观察变量（activeTabType/drugCategory/drugKeyword）定义之后注册，
// 否则 watch 创建时立即求值源会触发 const TDZ，导致整个组件 setup 中断崩溃。
watch(activeTabType, () => reloadDrugs())
watch(drugCategory, () => reloadDrugs())
let kwTimer = null
watch(drugKeyword, () => {
  clearTimeout(kwTimer)
  kwTimer = setTimeout(() => reloadDrugs(), 400)
})
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';

.consultation-page {
  background: #f5f7fa;
  padding: 12px 16px 80px;
}

/* 覆盖 Element Plus 卡片圆角 */
.patient-card,
.prescription-card {
  border-radius: 8px;
  margin-bottom: 12px;
}

.patient-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}

/* 处方标签 */
.prescription-tabs {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.rx-tabs {
  flex: 1;
  :deep(.el-tabs__header) {
    margin: 0;
    border-bottom: none;
  }
  :deep(.el-tabs__nav) {
    border: none;
  }
  :deep(.el-tabs__item) {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    margin-right: 8px;
    height: 32px;
    line-height: 30px;
    font-size: 13px;
  }
  :deep(.el-tabs__item.is-active) {
    background: #5b7cff;
    border-color: #5b7cff;
    color: #fff;
  }
}

/* 处方主体 */
.prescription-main {
  display: flex;
  min-height: 420px;
}
.prescription-left {
  flex: 1;
  min-width: 0;
  padding-right: 16px;
  border-right: 1px solid #eef0f4;
}
.rx-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.rx-title {
  font-size: 28px;
  color: #5b7cff;
  font-weight: 600;
  font-family: 'Times New Roman', serif;
}
.input-unit {
  display: flex;
  align-items: center;
  gap: 4px;
  .el-select.unit-select {
    width: 56px;
  }
  span {
    font-size: 12px;
    color: #909399;
    white-space: nowrap;
  }
}

/* 右侧药品选择 */
.prescription-right {
  width: 340px;
  min-width: 340px;
  padding-left: 16px;
}
.drug-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.drug-search {
  flex: 1;
}
.drug-load-more {
  text-align: center;
  font-size: 12px;
  color: #909399;
  padding: 8px 0;
}

/* 处方底部 */
.prescription-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #eef0f4;
}
.footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.footer-label {
  font-size: 13px;
  color: #909399;
}
.footer-right {
  font-size: 14px;
  color: #606266;
}
.total-amount {
  color: #f56c6c;
  font-weight: 700;
  font-size: 16px;
}

/* 底部操作栏 */
.bottom-bar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12px 24px;
  background: #fff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
  z-index: 100;
}

/* 患者查询弹窗 */
.patient-search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;

  .patient-search-tip {
    color: #909399;
    font-size: 12px;
  }
}
</style>

<template>
  <div class="his-page consultation-page" style="padding-bottom: 80px">
    <div class="consultation-top-tabs">
      <div class="top-tab" @click="goTab('western')">处方</div>
      <div class="top-tab active" @click="goTab('record')">病历</div>
    </div>

    <div class="his-card patient-card">
      <PatientForm />
    </div>

    <div class="his-card prescription-card">
      <div class="prescription-tabs">
        <div class="prescription-tab active">检查项目1</div>
      </div>
      <div class="prescription-main">
        <div class="prescription-left">
          <div class="rx-header">
            <span class="rx-title">检查</span>
          </div>
          <div class="inspection-content">
            <table class="drug-table" v-if="inspectionList.length">
              <thead>
                <tr>
                  <th>名称</th>
                  <th style="width: 70px">规格</th>
                  <th style="width: 60px">价格</th>
                  <th style="width: 60px">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="it in inspectionList" :key="it.id">
                  <td>{{ it.name }}</td>
                  <td>{{ it.spec }}</td>
                  <td>{{ it.price }}</td>
                  <td><button class="link-btn" @click="removeProject(it.id)">移除</button></td>
                </tr>
              </tbody>
            </table>
            <p class="placeholder-text" v-else>检查项目内容区，可从右侧项目库选择检查项目。</p>
          </div>
        </div>
        <div class="prescription-right">
          <div class="drug-toolbar">
            <select class="his-select" style="width: 110px">
              <option value="">项目分类</option>
              <option value="all">全部分类</option>
            </select>
            <div class="drug-search">
              <input class="his-input" placeholder="输入项目名称" />
              <button class="search-btn">
                <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                  <path d="M11.7422 10.3439C12.5329 9.2673 13 7.9382 13 6.5C13 2.91015 10.0899 0 6.5 0C2.91015 0 0 2.91015 0 6.5C0 10.0899 2.91015 13 6.5 13C7.9382 13 9.2673 12.5329 10.3439 11.7422L14.1464 15.5456L15 14.6921L11.7422 10.3439ZM6.5 11.5C3.73858 11.5 1.5 9.26142 1.5 6.5C1.5 3.73858 3.73858 1.5 6.5 1.5C9.26142 1.5 11.5 3.73858 11.5 6.5C11.5 9.26142 9.26142 11.5 6.5 11.5Z" />
                </svg>
              </button>
            </div>
          </div>
          <div class="drug-table-wrap">
            <table class="drug-table">
              <thead>
                <tr>
                  <th style="width: 32px">选择</th>
                  <th>名称</th>
                  <th style="width: 70px">规格</th>
                  <th style="width: 60px">价格</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in projectList" :key="p.id" @click="addProject(p)">
                  <td><input type="checkbox" :checked="inspectionList.some(it => it.id === p.id)" /></td>
                  <td>{{ p.name }}</td>
                  <td>{{ p.spec }}</td>
                  <td>{{ p.price }}</td>
                </tr>
                <tr v-if="!projectList.length">
                  <td colspan="4" style="text-align: center; color: #9ca3af; padding: 40px 0">暂无检查项目数据</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div class="his-bottom-bar consultation-bottom-bar">
      <button class="bottom-btn" @click="goTemplateCall">处方调用</button>
      <button class="bottom-btn" @click="printRx">打印处方</button>
      <button class="bottom-btn" @click="goTemplateCreate">存为模板</button>
      <button class="bottom-btn primary" @click="onSave">保存</button>
      <button class="bottom-btn warning" @click="goCharge">收费</button>
      <button class="bottom-btn danger" @click="goEnd">结束就诊</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PatientForm from './components/PatientForm.vue'
import { getRegistration } from '@/api/registration'
import { createMedicalRecord } from '@/api/treatment'
import { get } from '@/utils/request'
import { fetchAllPages } from '@/utils/paging'

const router = useRouter()
const route = useRoute()

const regId = computed(() => route.query.regId || '')
const patientId = ref('')
const registrationId = ref('')

onMounted(async () => {
  if (regId.value) {
    try {
      const reg = await getRegistration(regId.value)
      registrationId.value = reg.id || regId.value
      patientId.value = reg.patient_id || ''
      patient.name = reg.patient_name || patient.name
    } catch (e) { /* 忽略 */ }
  }
  loadProjects()
})

const patient = reactive({ name: '' })

// 检查项目库（真实接口）
const loadingProjects = ref(false)
const projectList = ref([])
const inspectionList = ref([])

const loadProjects = async () => {
  loadingProjects.value = true
  try {
    const items = await fetchAllPages(async p => (await get('/projects', p))?.data || {})
    projectList.value = items.map(p => ({
      id: p.id,
      name: p.name,
      spec: p.spec || '',
      category: p.category || '',
      price: p.price ?? 0,
    }))
  } catch (e) {
    ElMessage.error('检查项目加载失败')
  } finally {
    loadingProjects.value = false
  }
}

const addProject = (p) => {
  if (inspectionList.value.some(it => it.id === p.id)) return
  inspectionList.value.push({ ...p })
}
const removeProject = (id) => {
  inspectionList.value = inspectionList.value.filter(it => it.id !== id)
}

const goTab = (name) => {
  if (name === 'western') router.push('/consultation/western')
}

const goTemplateCall = () => router.push('/consultation/prescription/template-call')
const goTemplateCreate = () => router.push('/consultation/prescription/template-create')
const goCharge = () => router.push('/consultation/charge')
const goEnd = () => router.push('/consultation/charge/confirm')
const printRx = () => {
  ElMessage.info('调用浏览器打印')
  window.print()
}
const onSave = async () => {
  if (!patientId.value) {
    ElMessage.warning('请先选择就诊患者')
    return
  }
  try {
    await createMedicalRecord({
      registration_id: registrationId.value,
      patient_id: patientId.value,
      advice: '检查项目：' + inspectionList.value.map(it => it.name).join('、'),
    })
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';

.consultation-page {
  background: #f5f7fa;
}
.consultation-top-tabs {
  display: inline-flex;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 12px;
  background: #fff;
}
.top-tab {
  padding: 9px 28px;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
  border-right: 1px solid #d1d5db;
  transition: color 0.2s, background 0.2s;
  user-select: none;
}
.top-tab:last-child {
  border-right: none;
}
.top-tab.active {
  color: #fff;
  background: #7b8dfd;
  font-weight: 500;
}
.patient-card {
  margin-bottom: 12px;
  padding: 16px 20px;
}
.prescription-card {
  padding: 0;
  overflow: hidden;
}
.prescription-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}
.prescription-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  font-size: 13px;
  color: #4b5563;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
}
.prescription-tab.active {
  color: #fff;
  background: #7b8dfd;
  border-color: #7b8dfd;
}
.prescription-main {
  display: flex;
  min-height: 420px;
}
.prescription-left {
  flex: 1;
  min-width: 0;
  padding: 16px;
  border-right: 1px solid #e5e7eb;
}
.rx-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.rx-title {
  font-size: 28px;
  color: #7b8dfd;
  font-weight: 600;
}
.inspection-content {
  padding: 40px 20px;
  text-align: center;
}
.placeholder-text {
  color: #9ca3af;
  font-size: 14px;
}
.prescription-right {
  width: 320px;
  min-width: 320px;
  padding: 16px;
  background: #fff;
}
.drug-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.drug-search {
  flex: 1;
  display: flex;
  align-items: stretch;
}
.drug-search .his-input {
  flex: 1;
  font-size: 13px;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.search-btn {
  width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #7b8dfd;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}
.drug-table-wrap {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}
.drug-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.drug-table th {
  padding: 10px 8px;
  background: #f9fafb;
  color: #374151;
  font-weight: 500;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}
.drug-table td {
  padding: 9px 8px;
  color: #4b5563;
  border-bottom: 1px solid #f3f4f6;
}
.consultation-bottom-bar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 20px;
}
.bottom-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  font-size: 14px;
  color: #4b5563;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  transition: color 0.2s, background 0.2s, border-color 0.2s;
}
.bottom-btn:hover {
  color: #7b8dfd;
  border-color: #7b8dfd;
}
.bottom-btn.primary {
  color: #fff;
  background: #7b8dfd;
  border-color: #7b8dfd;
}
.bottom-btn.primary:hover {
  background: #6876e8;
}
.bottom-btn.warning {
  color: #fff;
  background: #f59e0b;
  border-color: #f59e0b;
}
.bottom-btn.warning:hover {
  background: #d97706;
}
.bottom-btn.danger {
  color: #fff;
  background: #ef4444;
  border-color: #ef4444;
}
.bottom-btn.danger:hover {
  background: #dc2626;
}
</style>

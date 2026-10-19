<template>
  <div class="his-page">
    <div class="clinic-header">
      <div class="clinic-title">诊所信息维护</div>
      <button class="his-btn his-btn-primary" :disabled="saving" @click="onSave">
        <span v-if="saving" class="btn-spinner"></span>
        <span>保存</span>
      </button>
    </div>

    <div class="clinic-card">
      <div class="clinic-form">
        <div class="form-row">
          <div class="form-item">
            <label>诊所编号</label>
            <input v-model="form.code" class="his-input" disabled />
          </div>
          <div class="form-item required">
            <label>诊所名称</label>
            <input v-model="form.name" class="his-input" placeholder="请输入诊所名称" />
          </div>
          <div class="form-item">
            <label>诊所Logo</label>
            <HisUpload v-model="form.logo" :width="80" :height="80" placeholder="上传" action-text="修改" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-item">
            <label>诊所所有人</label>
            <input v-model="form.contact_name" class="his-input" placeholder="请输入诊所所有人" />
          </div>
          <div class="form-item">
            <label>诊所所有人电话</label>
            <input v-model="form.contact_phone" class="his-input" placeholder="请输入电话" />
          </div>
          <div class="form-item">
            <label>诊所所有人邮箱</label>
            <input v-model="form.contact_email" class="his-input" placeholder="请输入邮箱" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-item">
            <label>地址</label>
            <select v-model="form.region" class="his-input his-select">
              <option value="">请选择省/市</option>
              <option value="广东省/深圳市">广东省/深圳市</option>
              <option value="广东省/广州市">广东省/广州市</option>
              <option value="北京市/北京市">北京市/北京市</option>
              <option value="上海市/上海市">上海市/上海市</option>
              <option value="浙江省/杭州市">浙江省/杭州市</option>
            </select>
          </div>
          <div class="form-item col-2">
            <label>详细地址</label>
            <input v-model="form.detail_address" class="his-input" placeholder="请输入详细地址" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-item col-3">
            <label>诊所介绍</label>
            <textarea v-model="form.introduction" class="his-input his-textarea" rows="4" placeholder="请输入诊所介绍"></textarea>
          </div>
        </div>
      </div>

      <div class="clinic-footer">
        <div class="footer-item">
          <span class="footer-label">诊所状态</span>
          <label class="his-switch">
            <input v-model="isActive" type="checkbox" @change="onStatusChange">
            <span class="his-switch-slider"></span>
          </label>
        </div>
        <div class="footer-item">
          <span class="footer-label">到期时间：</span>
          <span class="footer-value">{{ form.expires_at || '-' }}</span>
        </div>
        <div class="footer-item">
          <span class="footer-label">总用户数：</span>
          <span class="footer-value">{{ form.user_count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import HisUpload from '@/components/HisUpload/index.vue'
import { getCurrentTenant, updateCurrentTenant } from '@/api/tenant'

const form = reactive({
  id: '',
  code: '',
  name: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  region: '',
  detail_address: '',
  address: '',
  status: 'active',
  expires_at: '',
  logo: '',
  introduction: '',
  user_count: 0
})

const saving = ref(false)

const isActive = computed({
  get: () => form.status === 'active',
  set: (val) => {
    form.status = val ? 'active' : 'inactive'
  }
})

function splitAddress(address) {
  if (!address) return { region: '', detail: '' }
  // 尝试按常见分隔符拆分省市和详细地址
  const parts = address.split(/\s+/)
  if (parts.length >= 2 && parts[0].includes('/')) {
    return { region: parts[0], detail: parts.slice(1).join(' ') }
  }
  return { region: '', detail: address }
}

async function loadData() {
  try {
    const data = await getCurrentTenant()
    if (!data) return
    Object.assign(form, {
      id: data.id || '',
      code: data.code || '',
      name: data.name || '',
      contact_name: data.contact_name || '',
      contact_phone: data.contact_phone || '',
      contact_email: data.contact_email || '',
      status: data.status || 'active',
      expires_at: data.expires_at || '',
      logo: data.logo || '',
      introduction: data.introduction || '',
      user_count: data.user_count || 0
    })
    const { region, detail } = splitAddress(data.address || '')
    form.region = region
    form.detail_address = detail
  } catch (e) {
    console.error('加载诊所信息失败', e)
  }
}

function onStatusChange() {
  form.status = isActive.value ? 'active' : 'inactive'
}

async function onSave() {
  if (!form.name) {
    ElMessage.warning('请输入诊所名称')
    return
  }
  saving.value = true
  try {
    const address = [form.region, form.detail_address].filter(Boolean).join(' ')
    await updateCurrentTenant({
      name: form.name,
      contact_name: form.contact_name,
      contact_phone: form.contact_phone,
      contact_email: form.contact_email,
      address,
      status: form.status,
      logo: form.logo,
      introduction: form.introduction
    })
    ElMessage.success('保存成功')
    await loadData()
  } catch (e) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.clinic-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.clinic-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  padding-left: 12px;
  border-left: 4px solid #5b7cff;
  line-height: 1.2;
}

.clinic-card {
  background: #fff;
  border-radius: 8px;
  padding: 28px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.clinic-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.col-2 {
  grid-column: span 2;
}

.form-item.col-3 {
  grid-column: span 3;
}

.form-item label {
  font-size: 14px;
  color: #4b5563;
}

.form-item.required label::after {
  content: '*';
  color: #ef4444;
  margin-left: 4px;
}

.his-input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  color: #1f2937;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.his-input:focus {
  border-color: #5b7cff;
}

.his-input:disabled {
  background: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

.his-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 10l5 5 5-5z' fill='%239ca3af'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 18px;
  padding-right: 32px;
}

.his-textarea {
  height: auto;
  min-height: 100px;
  padding: 12px;
  resize: vertical;
}

.clinic-footer {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid #f3f4f6;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-label {
  font-size: 14px;
  color: #4b5563;
}

.footer-value {
  font-size: 14px;
  color: #1f2937;
}

.his-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.his-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.his-switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e5e7eb;
  border-radius: 24px;
  transition: 0.3s;
}

.his-switch-slider::before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
}

.his-switch input:checked + .his-switch-slider {
  background-color: #10b981;
}

.his-switch input:checked + .his-switch-slider::before {
  transform: translateX(20px);
}

.his-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 20px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.his-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.his-btn-primary {
  background: #5b7cff;
  color: #fff;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

<template>
  <div
    class="his-upload"
    :class="{ disabled, loading }"
    :style="boxStyle"
    @click="onClick"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      class="his-upload-input"
      @change="onFileChange"
    />

    <template v-if="modelValue">
      <img :src="fullUrl" class="his-upload-preview" alt="preview" />
      <div class="his-upload-mask">
        <span class="his-upload-action" @click.stop="onReUpload">{{ actionText }}</span>
        <span v-if="!disabled" class="his-upload-action danger" @click.stop="onDelete">删除</span>
      </div>
    </template>

    <template v-else>
      <div class="his-upload-placeholder">
        <svg viewBox="0 0 24 24" class="his-upload-icon">
          <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z" fill="currentColor"/>
        </svg>
        <span class="his-upload-text">{{ placeholder }}</span>
      </div>
    </template>

    <div v-if="loading" class="his-upload-loading">
      <svg class="his-upload-spinner" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { uploadImage } from '@/api/upload'

const props = defineProps({
  modelValue: { type: String, default: '' },
  width: { type: [String, Number], default: 80 },
  height: { type: [String, Number], default: 80 },
  placeholder: { type: String, default: '上传图片' },
  actionText: { type: String, default: '修改' },
  accept: { type: String, default: 'image/*' },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'success', 'error'])

const fileInput = ref(null)
const loading = ref(false)

const boxStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))

const fullUrl = computed(() => {
  const url = props.modelValue
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  if (url.startsWith('data:')) return url
  return url
})

function onClick() {
  if (props.disabled || loading.value) return
  fileInput.value?.click()
}

function onReUpload() {
  if (props.disabled || loading.value) return
  fileInput.value?.click()
}

function onDelete() {
  if (props.disabled || loading.value) return
  emit('update:modelValue', '')
}

async function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''

  if (!file.type.startsWith('image/')) {
    emit('error', '请选择图片文件')
    return
  }

  loading.value = true
  try {
    const data = await uploadImage(file)
    const url = data?.file_url || data?.url || data
    emit('update:modelValue', url)
    emit('success', url)
  } catch (err) {
    emit('error', err?.message || '上传失败')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.his-upload {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s;
}

.his-upload:hover {
  border-color: var(--primary, #5b7cff);
  background: #f5f7ff;
}

.his-upload.disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.his-upload-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.his-upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #9ca3af;
}

.his-upload-icon {
  width: 24px;
  height: 24px;
}

.his-upload-text {
  font-size: 12px;
}

.his-upload-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.his-upload-mask {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: rgba(0, 0, 0, 0.45);
  opacity: 0;
  transition: opacity 0.2s;
}

.his-upload:hover .his-upload-mask {
  opacity: 1;
}

.his-upload-action {
  color: #fff;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.15);
}

.his-upload-action.danger {
  color: #ff6b6b;
}

.his-upload-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.75);
}

.his-upload-spinner {
  width: 24px;
  height: 24px;
  animation: his-upload-spin 1s linear infinite;
  color: var(--primary, #5b7cff);
}

.his-upload-spinner circle {
  stroke-dasharray: 60;
  stroke-dashoffset: 20;
}

@keyframes his-upload-spin {
  to { transform: rotate(360deg); }
}
</style>

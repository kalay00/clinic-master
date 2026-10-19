<template>
  <div class="ts-page">
    <div class="ts-card">
      <div class="ts-header">
        <div class="ts-logo">
          <svg viewBox="0 0 24 24" class="ts-logo-icon"><path d="M12 21s-6.5-4.5-6.5-9.5S7.5 3 12 3s6.5 2.5 6.5 8.5S12 21 12 21z" fill="currentColor"/><path d="M11 8h2v3h3v2h-3v3h-2v-3H8v-2h3V8z" fill="#fff"/></svg>
        </div>
      </div>

      <h2 class="ts-title">选择诊所</h2>
      <p class="ts-desc">您的账号关联了多个诊所，请选择一个进入</p>

      <div class="ts-list" v-if="tenants.length">
        <label
          v-for="t in tenants" :key="t.id"
          class="ts-item"
          :class="{ active: selectedId === t.id }"
          @click="selectedId = t.id"
        >
          <span class="ts-radio">
            <span class="ts-radio-dot" v-if="selectedId === t.id"></span>
          </span>
          <span class="ts-item-icon">
            <svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="currentColor"/></svg>
          </span>
          <span class="ts-item-info">
            <span class="ts-item-name">{{ t.name }}</span>
            <span class="ts-item-code">{{ t.code }}</span>
          </span>
          <span class="ts-item-tag" v-if="t.is_primary">主诊所</span>
        </label>
      </div>
      <div class="ts-empty" v-else>
        <svg viewBox="0 0 24 24" class="ts-empty-icon"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z" fill="currentColor"/></svg>
        <p>暂无可选诊所，请确认账号已关联租户</p>
      </div>

      <button class="ts-btn" :disabled="!selectedId || loading" @click="onEnter">
        <span v-if="loading" class="ts-spinner"></span>
        <span>进入系统</span>
      </button>

      <div class="ts-footer">
        <a class="ts-link" @click.prevent="onBack">返回登录</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()

const tenants = ref([])
const selectedId = ref('')
const loading = ref(false)

onMounted(() => {
  tenants.value = userStore.tempTenants || []
  if (tenants.value.length === 1) {
    selectedId.value = tenants.value[0].id
  }
  // 兜底：从后端重新获取租户列表
  if (!tenants.value.length && userStore.tempToken) {
    loadTenants()
  }
})

async function loadTenants() {
  try {
    const { getTenants } = await import('@/api/auth')
    const data = await getTenants()
    tenants.value = data || []
  } catch (e) {
    console.error('获取租户列表失败', e)
  }
}

async function onEnter() {
  if (!selectedId.value) return
  loading.value = true
  try {
    await userStore.selectTenant(selectedId.value)
    router.push('/')
  } catch (e) {
    alert(e?.message || '切换租户失败，请重新登录')
    userStore.resetState()
    router.push('/login')
  } finally {
    loading.value = false
  }
}

function onBack() {
  userStore.tempToken = ''
  userStore.tempTenants = []
  userStore.tempUserId = ''
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.ts-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  padding: 24px;
}

.ts-card {
  width: 440px;
  max-width: 100%;
  background: #fff;
  border-radius: 16px;
  padding: 48px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.ts-header { text-align: center; margin-bottom: 24px; }
.ts-logo {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: #5b7cff;
  display: inline-flex;
  align-items: center; justify-content: center;
  color: #fff;
}
.ts-logo-icon { width: 28px; height: 28px; }

.ts-title {
  font-size: 20px; font-weight: 700;
  color: #1f2937; text-align: center;
  margin: 0 0 8px;
}

.ts-desc {
  font-size: 13px; color: #909399;
  text-align: center; margin: 0 0 24px;
}

.ts-list {
  display: flex; flex-direction: column; gap: 10px;
  margin-bottom: 24px;
}

.ts-item {
  display: flex; align-items: center;
  gap: 12px; padding: 14px 16px;
  border: 1px solid #e4e7ed; border-radius: 10px;
  cursor: pointer; transition: all 0.2s;
  background: #fff;
}

.ts-item:hover { border-color: #8aa4ff; background: #f8faff; }
.ts-item.active { border-color: #5b7cff; background: #eef1ff; }

.ts-radio {
  width: 18px; height: 18px; border-radius: 50%;
  border: 2px solid #d9d9d9; display: flex;
  align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.2s;
}
.ts-item.active .ts-radio { border-color: #5b7cff; }
.ts-radio-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #5b7cff;
}

.ts-item-icon {
  width: 36px; height: 36px; border-radius: 8px;
  background: #eef1ff; display: flex;
  align-items: center; justify-content: center;
  color: #5b7cff; flex-shrink: 0;
}
.ts-item-icon svg { width: 20px; height: 20px; }

.ts-item-info { flex: 1; display: flex; flex-direction: column; }
.ts-item-name { font-size: 14px; font-weight: 500; color: #1f2937; }
.ts-item-code { font-size: 12px; color: #909399; margin-top: 2px; }

.ts-item-tag {
  font-size: 11px; padding: 2px 8px; border-radius: 10px;
  background: #e6f9f0; color: #3ccf8a; flex-shrink: 0;
}

.ts-empty {
  text-align: center; padding: 32px 0; color: #909399; margin-bottom: 24px;
}
.ts-empty-icon { width: 40px; height: 40px; margin-bottom: 8px; opacity: 0.4; }

.ts-btn {
  width: 100%; height: 44px; border: none; border-radius: 8px;
  background: #5b7cff; color: #fff; font-size: 15px; font-weight: 500;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  gap: 8px; transition: background 0.2s;
}
.ts-btn:hover:not(:disabled) { background: #3d5eff; }
.ts-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.ts-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.4); border-top-color: #fff;
  border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.ts-footer { text-align: center; margin-top: 20px; }
.ts-link { color: #5b7cff; cursor: pointer; font-size: 13px; }
.ts-link:hover { color: #3d5eff; }
</style>

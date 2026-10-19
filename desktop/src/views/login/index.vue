<template>
  <div class="login-page">
    <div class="login-logo">
      <div class="logo-circle">
        <svg viewBox="0 0 24 24" class="logo-icon">
          <path d="M12 21s-6.5-4.5-6.5-9.5S7.5 3 12 3s6.5 2.5 6.5 8.5S12 21 12 21z" fill="currentColor" />
          <path d="M11 8h2v3h3v2h-3v3h-2v-3H8v-2h3V8z" fill="#fff" />
        </svg>
      </div>
    </div>

    <div class="login-card">
      <div class="login-illustration">
        <div class="illus-scene">
          <svg viewBox="0 0 400 320" class="illus-svg">
            <defs>
              <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#eef1ff" />
                <stop offset="100%" stop-color="#dbe4ff" />
              </linearGradient>
            </defs>
            <circle cx="200" cy="160" r="130" fill="url(#bgGrad)" />
            <g fill="#c7d2fe">
              <rect x="110" y="120" width="28" height="60" rx="3" />
              <rect x="145" y="90" width="28" height="90" rx="3" />
              <rect x="180" y="110" width="28" height="70" rx="3" />
              <rect x="215" y="80" width="28" height="100" rx="3" />
              <rect x="250" y="100" width="28" height="80" rx="3" />
            </g>
            <path d="M160 250 L240 250 L250 280 L150 280 Z" fill="#a5b4fc" />
            <ellipse cx="200" cy="250" rx="45" ry="8" fill="#818cf8" />
            <g transform="translate(130, 140)">
              <rect x="0" y="35" width="50" height="70" rx="6" fill="#fff" />
              <path d="M15 35 L15 20 Q15 10 25 10 Q35 10 35 20 L35 35" fill="#fff" stroke="#5b7cff" stroke-width="2" />
              <rect x="14" y="50" width="22" height="4" rx="1" fill="#5b7cff" />
              <rect x="14" y="60" width="22" height="4" rx="1" fill="#5b7cff" />
              <rect x="14" y="70" width="18" height="4" rx="1" fill="#5b7cff" />
              <rect x="-8" y="90" width="20" height="20" rx="4" fill="#5b7cff" />
              <rect x="-4" y="95" width="12" height="10" rx="2" fill="#fff" />
              <path d="M8 80 L25 110" stroke="#8aa4ff" stroke-width="3" stroke-linecap="round" />
            </g>
            <g transform="translate(220, 140)">
              <rect x="0" y="35" width="50" height="70" rx="6" fill="#fff" />
              <path d="M15 35 L15 20 Q15 10 25 10 Q35 10 35 20 L35 35" fill="#fff" stroke="#5b7cff" stroke-width="2" />
              <rect x="14" y="50" width="22" height="4" rx="1" fill="#5b7cff" />
              <rect x="14" y="60" width="22" height="4" rx="1" fill="#5b7cff" />
              <rect x="14" y="70" width="18" height="4" rx="1" fill="#5b7cff" />
              <circle cx="45" cy="20" r="10" fill="#ff8fab" />
              <path d="M25 80 L42 110" stroke="#8aa4ff" stroke-width="3" stroke-linecap="round" />
            </g>
            <g transform="translate(170, 100)">
              <path d="M30 55 C10 40 0 20 30 5 C60 20 50 40 30 55Z" fill="#5b7cff" />
              <polyline points="16,30 24,30 28,22 34,38 40,30 48,30" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
            </g>
            <g transform="translate(80, 210)">
              <rect x="10" y="40" width="14" height="40" rx="2" fill="#4b5563" />
              <path d="M0 40 Q17 15 34 40" fill="#3ccf8a" />
              <path d="M10 40 Q22 20 34 40" fill="#3ccf8a" opacity="0.7" />
              <ellipse cx="17" cy="80" rx="18" ry="5" fill="#e5e7eb" />
            </g>
          </svg>
        </div>
      </div>

      <div class="login-form-wrap">
        <h2 class="login-title">登录诊所管理系统</h2>
        <form class="login-form" @submit.prevent="onLogin">
          <div class="login-field">
            <span class="field-icon">
              <svg viewBox="0 0 24 24"><path d="M12 12c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm0 2c-3.33 0-10 1.67-10 5v1h20v-1c0-3.33-6.67-5-10-5z" fill="currentColor"/></svg>
            </span>
            <input v-model="form.mobile" type="text" class="login-input" placeholder="请输入手机号码" />
          </div>

          <div class="login-field">
            <span class="field-icon">
              <svg viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3-9H9V6c0-1.66 1.34-3 3-3s3 1.34 3 3v2z" fill="currentColor"/></svg>
            </span>
            <input v-model="form.password" :type="showPassword ? 'text' : 'password'" class="login-input" placeholder="请输入密码" />
            <span class="field-suffix" @click="showPassword = !showPassword">
              <svg v-if="showPassword" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5C21.27 7.61 17 4.5 12 4.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/></svg>
              <svg v-else viewBox="0 0 24 24"><path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z" fill="currentColor"/></svg>
            </span>
          </div>

          <div class="login-field">
            <span class="field-icon">
              <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z" fill="currentColor"/></svg>
            </span>
            <select v-model="form.clinic" class="login-input login-select">
              <option value="demo">免费演示诊所</option>
            </select>
            <span class="field-suffix field-arrow">
              <svg viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z" fill="currentColor"/></svg>
            </span>
          </div>

          <div class="login-options">
            <label class="login-checkbox">
              <input v-model="remember" type="checkbox" />
              <span class="check-mark"><svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="currentColor"/></svg></span>
              <span class="check-label">1个月内免登陆</span>
            </label>
            <a class="login-link" @click.prevent="$router.push('/retrieve-password')">忘记密码？</a>
          </div>

          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            <span>登 录</span>
          </button>

          <div class="login-footer">
            <a class="login-link" @click.prevent="$router.push('/apply-trial')">申请试用</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const form = reactive({ mobile: '', password: '', clinic: 'demo' })
const remember = ref(false)
const showPassword = ref(false)
const loading = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('login_mobile')
  if (saved) {
    form.mobile = saved
    remember.value = true
  }
})

async function onLogin() {
  if (!form.mobile.trim()) return alert('请输入手机号码')
  if (!form.password) return alert('请输入密码')
  loading.value = true
  try {
    const result = await userStore.login({
      username: form.mobile.trim(),
      password: form.password
    })
    if (remember.value) {
      localStorage.setItem('login_mobile', form.mobile.trim())
    } else {
      localStorage.removeItem('login_mobile')
    }
    if (result.requiresTenantSelection) {
      router.push('/tenant-select')
    } else {
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    }
  } catch (error) {
    alert(error?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #5b7cff;
  padding: 24px;
  position: relative;
}

.login-logo {
  position: absolute;
  top: 24px;
  left: 24px;
}

.logo-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.logo-icon {
  width: 24px;
  height: 24px;
}

.login-card {
  width: 900px;
  max-width: 100%;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: flex;
  overflow: hidden;
}

.login-illustration {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: #f8faff;
}

.illus-scene {
  width: 100%;
  max-width: 360px;
}

.illus-svg {
  width: 100%;
  height: auto;
  display: block;
}

.login-form-wrap {
  flex: 1;
  padding: 56px 64px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 32px;
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.login-field {
  position: relative;
  display: flex;
  align-items: center;
}

.field-icon,
.field-suffix {
  position: absolute;
  width: 20px;
  height: 20px;
  color: #8aa4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.field-icon {
  left: 14px;
}

.field-suffix {
  right: 14px;
  pointer-events: auto;
  cursor: pointer;
  color: #c0c4cc;
  transition: color 0.2s;
}

.field-suffix:hover {
  color: #5b7cff;
}

.field-arrow {
  pointer-events: none;
}

.login-input {
  width: 100%;
  height: 46px;
  padding: 0 42px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: #f5f7fa;
  font-size: 14px;
  color: #1f2937;
  outline: none;
  transition: all 0.2s;
}

.login-input::placeholder {
  color: #909399;
}

.login-input:focus {
  background: #fff;
  border-color: #5b7cff;
  box-shadow: 0 0 0 3px rgba(91, 124, 255, 0.12);
}

.login-select {
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.login-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}

.login-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
}

.login-checkbox input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.check-mark {
  width: 16px;
  height: 16px;
  border: 1px solid #d9d9d9;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
  transition: all 0.2s;
}

.check-mark svg {
  width: 14px;
  height: 14px;
}

.login-checkbox input:checked + .check-mark {
  background: #5b7cff;
  border-color: #5b7cff;
  color: #fff;
}

.login-link {
  color: #5b7cff;
  cursor: pointer;
  text-decoration: none;
}

.login-link:hover {
  color: #3d5eff;
}

.login-btn {
  width: 100%;
  height: 46px;
  border: none;
  border-radius: 8px;
  background: #5b7cff;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.2s;
}

.login-btn:hover:not(:disabled) {
  background: #3d5eff;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  text-align: center;
}

@media (max-width: 820px) {
  .login-card {
    flex-direction: column;
  }
  .login-illustration {
    display: none;
  }
  .login-form-wrap {
    padding: 40px 32px;
  }
}
</style>

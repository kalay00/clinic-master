<template>
  <el-config-provider :locale="locale">
    <div id="app-wrapper" :class="['app-wrapper', { 'is-dark': appStore.isDark }]">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
    <LoadingOverlay :visible="loadingStore.visible" :text="loadingStore.text" />
  </el-config-provider>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useAppStore } from '@/store/modules/app'
import { useLoadingStore } from '@/store/modules/loading'
import LoadingOverlay from '@/components/LoadingOverlay/LoadingOverlay.vue'

const appStore = useAppStore()
const loadingStore = useLoadingStore()
const locale = computed(() => zhCn)

const setHtmlTheme = isDark => {
  const html = document.documentElement
  if (isDark) {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
}

const setThemeColor = color => {
  document.documentElement.style.setProperty('--el-color-primary', color)
}

// 初始化主题：按截图强制使用浅色主题
appStore.setThemeMode('light')

// isDark 变化即应用 html.dark
watch(
  () => appStore.isDark,
  val => {
    setHtmlTheme(val)
  },
  { immediate: true }
)

// 主题模式（含 auto）变化时重新计算
watch(
  () => appStore.themeMode,
  () => {
    appStore.applyTheme()
  }
)

watch(
  () => appStore.themeColor,
  val => {
    setThemeColor(val)
  },
  { immediate: true }
)

// 监听系统主题切换（仅 auto 模式生效）
let mediaQuery = null
function handleSystemThemeChange() {
  if (appStore.themeMode === 'auto') {
    appStore.applyTheme()
  }
}

onMounted(() => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', handleSystemThemeChange)
  }
  setHtmlTheme(appStore.isDark)
  setThemeColor(appStore.themeColor)
})

onUnmounted(() => {
  if (mediaQuery) {
    mediaQuery.removeEventListener('change', handleSystemThemeChange)
  }
})
</script>

<style lang="scss" scoped>
.app-wrapper {
  width: 100%;
  height: 100%;
  min-height: 100vh;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

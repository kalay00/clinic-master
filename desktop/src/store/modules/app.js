import { defineStore } from 'pinia'
import { storage } from '@/utils/storage'

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: false,
    themeMode: 'light', // 'light' | 'dark' | 'auto'（auto 跟随系统）
    isDark: false,
    themeColor: '#409eff',
    loading: false,
    loadingText: '加载中...',
    device: 'desktop',
    size: 'default',
    language: 'zh-cn'
  }),

  getters: {
    sidebarWidth: state => (state.sidebarCollapsed ? '64px' : '220px')
  },

  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },

    setSidebarCollapsed(collapsed) {
      this.sidebarCollapsed = collapsed
    },

    // 根据 themeMode 计算实际 isDark：
    // light -> 亮色；dark -> 暗色；auto -> 跟随系统 prefers-color-scheme
    applyTheme() {
      let dark = false
      if (this.themeMode === 'dark') {
        dark = true
      } else if (this.themeMode === 'auto') {
        dark = !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
      }
      this.isDark = dark
    },

    setThemeMode(mode) {
      this.themeMode = mode
      this.applyTheme()
    },

    toggleDark() {
      const target = !this.isDark
      // 手动切换时退出 auto 模式，固定为对应手动模式
      this.themeMode = target ? 'dark' : 'light'
      this.isDark = target
    },

    setDark(isDark) {
      this.themeMode = isDark ? 'dark' : 'light'
      this.isDark = isDark
    },

    setThemeColor(color) {
      this.themeColor = color
    },

    setLoading(loading, text = '加载中...') {
      this.loading = loading
      this.loadingText = text
    },

    setDevice(device) {
      this.device = device
    },

    setSize(size) {
      this.size = size
    },

    resetState() {
      this.sidebarCollapsed = false
      this.themeMode = 'light'
      this.isDark = false
      this.themeColor = '#409eff'
      this.loading = false
      this.device = 'desktop'
      this.size = 'default'
    }
  },

  persist: {
    key: 'app-store',
    storage: localStorage,
    paths: ['sidebarCollapsed', 'themeMode', 'themeColor', 'size', 'language']
  }
})

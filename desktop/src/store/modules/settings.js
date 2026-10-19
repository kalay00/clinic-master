import { defineStore } from 'pinia'
import config from '@/config'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    title: config.title,
    showTagsView: config.showTagsView,
    showBreadcrumb: config.showBreadcrumb,
    showFooter: config.showFooter,
    fixedHeader: config.fixedHeader,
    sidebarCollapsible: config.sidebarCollapsible,
    defaultRoute: config.defaultRoute
  }),

  actions: {
    updateSettings(settings) {
      Object.assign(this.$state, settings)
    },

    setShowTagsView(val) {
      this.showTagsView = val
    },

    setShowBreadcrumb(val) {
      this.showBreadcrumb = val
    },

    setShowFooter(val) {
      this.showFooter = val
    },

    setFixedHeader(val) {
      this.fixedHeader = val
    },

    resetState() {
      this.title = config.title
      this.showTagsView = config.showTagsView
      this.showBreadcrumb = config.showBreadcrumb
      this.showFooter = config.showFooter
      this.fixedHeader = config.fixedHeader
      this.sidebarCollapsible = config.sidebarCollapsible
    }
  },

  persist: {
    key: 'settings-store',
    storage: localStorage,
    paths: ['showTagsView', 'showBreadcrumb', 'showFooter', 'fixedHeader', 'sidebarCollapsible']
  }
})

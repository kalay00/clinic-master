const config = {
  title: import.meta.env.VITE_APP_TITLE || '华宣诊所管理',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  env: import.meta.env.VITE_APP_ENV || 'development',
  useMock: import.meta.env.VITE_USE_MOCK === 'true',
  updateUrl: import.meta.env.VITE_UPDATE_URL || '',
  tokenKey: 'Authorization',
  tokenPrefix: 'Bearer ',
  timeout: 30000,
  retryCount: 1,
  retryDelay: 1000,
  whiteList: ['/login', '/404', '/403', '/tenant-select'],
  defaultRoute: '/dashboard',
  sidebarCollapsible: true,
  showTagsView: true, // 是否显示 TagsView 页签
  showBreadcrumb: true,
  showFooter: true,
  fixedHeader: true,
  theme: {
    primaryColor: '#409eff',
    isDark: false
  },
  tagsView: {
    enable: true, // 是否启用 TagsView
    affixTags: ['Dashboard'], // 固定标签，不可关闭
    maxCount: 20 // 最大缓存数量
  }
}

export default config

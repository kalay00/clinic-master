export function setupGlobalProperties(app) {
  app.config.globalProperties.$version = __APP_VERSION__
  app.config.globalProperties.$isElectron = !!(window.electronAPI && window.process === undefined)
}

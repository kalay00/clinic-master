// Electron 更新功能 - 通过 preload API 调用
// 注意：此文件只能在 Electron 环境中使用，浏览器环境会返回模拟数据

const isElectron = typeof window !== 'undefined' && window.electronAPI

const electronAPI = isElectron ? window.electronAPI : null

export function checkForUpdates() {
  if (!isElectron) {
    return Promise.resolve({ 
      success: true, 
      message: '当前为浏览器环境，无法检查更新', 
      devMode: true 
    })
  }
  return electronAPI.invokeMsg('checkForUpdates')
}

export function downloadUpdate() {
  if (!isElectron) {
    return Promise.resolve({ success: false, message: '浏览器环境不支持下载更新' })
  }
  return electronAPI.invokeMsg('downloadUpdate')
}

export function installUpdate() {
  if (!isElectron) {
    return Promise.resolve({ success: false, message: '浏览器环境不支持安装更新' })
  }
  return electronAPI.invokeMsg('installUpdate')
}

export function onUpdateAvailable(callback) {
  if (!isElectron) return
  electronAPI.onMsg('updateAvailable', callback)
}

export function onUpdateDownloadProgress(callback) {
  if (!isElectron) return
  electronAPI.onMsg('updateDownloadProgress', callback)
}

export function onUpdateDownloaded(callback) {
  if (!isElectron) return
  electronAPI.onMsg('updateDownloaded', callback)
}

export function onUpdateError(callback) {
  if (!isElectron) return
  electronAPI.onMsg('updateError', callback)
}

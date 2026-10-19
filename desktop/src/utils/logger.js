const LOG_PREFIX = '[App]'

export function logInfo(message, data = null) {
  const logData = { level: 'info', message, data, timestamp: Date.now() }
  console.log(`${LOG_PREFIX}[INFO] ${message}`, data || '')
  sendToMain('info', message, data)
}

export function logWarn(message, data = null) {
  const logData = { level: 'warn', message, data, timestamp: Date.now() }
  console.warn(`${LOG_PREFIX}[WARN] ${message}`, data || '')
  sendToMain('warn', message, data)
}

export function logError(message, data = null) {
  const logData = { level: 'error', message, data, timestamp: Date.now() }
  console.error(`${LOG_PREFIX}[ERROR] ${message}`, data || '')
  sendToMain('error', message, data)
}

function sendToMain(level, message, data) {
  if (window.electronAPI?.sendMsg) {
    try {
      window.electronAPI.sendMsg('log-write', {
        level,
        message,
        args: data ? [data] : []
      })
    } catch (e) {
      console.warn('发送日志到主进程失败:', e)
    }
  }
}

export async function exportLogs() {
  if (window.electronAPI?.invokeMsg) {
    return await window.electronAPI.invokeMsg('log-export')
  }
  return { success: false, message: '非Electron环境' }
}

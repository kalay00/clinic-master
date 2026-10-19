import { ElMessage } from 'element-plus'
import { logError } from './logger'

export function setupErrorHandler(app) {
  app.config.errorHandler = (err, vm, info) => {
    console.error('Vue Error:', err)
    console.error('Error Info:', info)
    logError('Vue Error: ' + (err?.message || 'unknown error'), { info, stack: err?.stack })
    ElMessage.error('页面发生错误，请刷新重试')
  }

  window.addEventListener('error', event => {
    console.error('Window Error:', event.error)
    logError('Window Error: ' + (event.message || 'unknown error'), {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    })
  })

  window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled Rejection:', event.reason)
    logError('Unhandled Rejection: ' + (event.reason?.message || 'unknown error'), {
      stack: event.reason?.stack
    })
  })
}

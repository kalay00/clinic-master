import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

export function toast(message, type = 'info', duration = 3000) {
  ElMessage({
    message,
    type,
    duration,
    showClose: true
  })
}

export function toastSuccess(message) {
  toast(message, 'success')
}

export function toastError(message) {
  toast(message, 'error', 5000)
}

export function toastWarning(message) {
  toast(message, 'warning')
}

export function toastInfo(message) {
  toast(message, 'info')
}

export function confirm(message, title = '提示', options = {}) {
  return ElMessageBox.confirm(message, title, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    ...options
  })
}

export function alert(message, title = '提示', type = 'info') {
  return ElMessageBox.alert(message, title, {
    confirmButtonText: '确定',
    type
  })
}

export function notify(title, message, type = 'info', duration = 4500) {
  ElNotification({
    title,
    message,
    type,
    duration,
    showClose: true,
    position: 'top-right'
  })
}

export function notifySuccess(title, message) {
  notify(title, message, 'success')
}

export function notifyError(title, message) {
  notify(title, message, 'error', 5000)
}

export function notifyWarning(title, message) {
  notify(title, message, 'warning')
}

export default {
  toast,
  toastSuccess,
  toastError,
  toastWarning,
  toastInfo,
  confirm,
  alert,
  notify,
  notifySuccess,
  notifyError,
  notifyWarning
}

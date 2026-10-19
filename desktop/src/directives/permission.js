import { hasPermission } from '@/utils/permission'

function checkPermission(el, binding) {
  const { value } = binding

  if (!value) {
    return
  }

  // 复用统一权限模块：支持 admin/平台管理员快捷放行、带租户前缀匹配、资源级兜底
  const ok = Array.isArray(value)
    ? value.some(p => hasPermission(p))
    : hasPermission(value)

  if (!ok) {
    el.style.display = 'none'
  }
}

export default {
  mounted(el, binding) {
    checkPermission(el, binding)
  },
  updated(el, binding) {
    checkPermission(el, binding)
  }
}

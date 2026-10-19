import { get, post, put } from '@/utils/request'

// 登录：返回 { access_token, refresh_token, token_type, user, tenant_id? }
export function login(data) {
  return post('/auth/login', data).then(res => res.data)
}

export function logout() {
  return post('/auth/logout').then(res => res.data)
}

export function refreshToken(data) {
  return post('/auth/refresh', data).then(res => res.data)
}

// 当前登录用户信息：{ id, username, name, roles:[{id,name,code}], permissions:[code], tenants, is_platform_admin }
export function getMe() {
  return get('/auth/me').then(res => res.data)
}

export function updateMe(data) {
  return put('/auth/me', data).then(res => res.data)
}

// 修改当前用户密码：{ old_password, new_password }
export function changePassword(data) {
  return post('/auth/change-password', data).then(res => res.data)
}

export function getTenants() {
  return get('/auth/tenants').then(res => res.data)
}

export function switchTenant(data) {
  return post('/auth/switch-tenant', data).then(res => res.data)
}

export default {
  login,
  logout,
  refreshToken,
  getMe,
  updateMe,
  changePassword,
  getTenants,
  switchTenant
}

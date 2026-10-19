import { get, post, put, del } from '@/utils/request'

export function getRoles() {
  return get('/roles').then(res => res.data)
}

export function getRole(id) {
  return get(`/roles/${id}`).then(res => res.data)
}

export function createRole(data) {
  return post('/roles', data).then(res => res.data)
}

export function updateRole(id, data) {
  return put(`/roles/${id}`, data).then(res => res.data)
}

export function deleteRole(id) {
  return del(`/roles/${id}`).then(res => res.data)
}

export function assignRolePermissions(id, permissionIds) {
  return post(`/roles/${id}/permissions`, { permission_ids: permissionIds }).then(res => res.data)
}

export function getAllPermissions() {
  return get('/roles/permissions/all').then(res => res.data)
}

export default {
  getRoles,
  getRole,
  createRole,
  updateRole,
  deleteRole,
  assignRolePermissions,
  getAllPermissions
}

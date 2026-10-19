import { get, post, put, del } from '@/utils/request'

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = {
    page,
    page_size: pageSize
  }
  const keyword = params.keyword || params.search
  if (keyword) backend.search = keyword
  if (params.status) backend.status = params.status
  if (params.role) backend.role = params.role
  return backend
}

export function getUsers(params = {}) {
  return get('/users', toBackendListParams(params)).then(res => res.data)
}

export function getUser(id) {
  return get(`/users/${id}`).then(res => res.data)
}

export function createUser(data) {
  return post('/users', data).then(res => res.data)
}

export function updateUser(id, data) {
  return put(`/users/${id}`, data).then(res => res.data)
}

export function deleteUser(id) {
  return del(`/users/${id}`).then(res => res.data)
}

export function assignUserRole(userId, roleId) {
  return post(`/users/${userId}/roles/${roleId}`).then(res => res.data)
}

export default {
  getUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
  assignUserRole
}

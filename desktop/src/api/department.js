import { get, post, put, del } from '@/utils/request'

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 100
  const backend = {
    page,
    page_size: pageSize
  }
  const keyword = params.keyword || params.search
  if (keyword) backend.search = keyword
  return backend
}

export function getDepartments(params = {}) {
  return get('/departments', toBackendListParams(params)).then(res => res.data)
}

export function getDepartment(id) {
  return get(`/departments/${id}`).then(res => res.data)
}

export function createDepartment(data) {
  return post('/departments', data).then(res => res.data)
}

export function updateDepartment(id, data) {
  return put(`/departments/${id}`, data).then(res => res.data)
}

export function deleteDepartment(id) {
  return del(`/departments/${id}`).then(res => res.data)
}

export default {
  getDepartments,
  getDepartment,
  createDepartment,
  updateDepartment,
  deleteDepartment
}

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
  if (params.department_id) backend.department_id = params.department_id
  return backend
}

export function getDoctors(params = {}) {
  return get('/doctors', toBackendListParams(params)).then(res => res.data)
}

export function getDoctor(id) {
  return get(`/doctors/${id}`).then(res => res.data)
}

export function createDoctor(data) {
  return post('/doctors', data).then(res => res.data)
}

export function updateDoctor(id, data) {
  return put(`/doctors/${id}`, data).then(res => res.data)
}

export function deleteDoctor(id) {
  return del(`/doctors/${id}`).then(res => res.data)
}

export default {
  getDoctors,
  getDoctor,
  createDoctor,
  updateDoctor,
  deleteDoctor
}

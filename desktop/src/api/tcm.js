import { get, post, put, del } from '@/utils/request'

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = { page, page_size: pageSize }
  const keyword = params.keyword || params.search
  if (keyword) backend.search = keyword
  if (params.category) backend.category = params.category
  if (params.status) backend.status = params.status
  if (params.prescription_type) backend.prescription_type = params.prescription_type
  return backend
}

// 经典处方（经方）库
export function getTcms(params = {}) {
  return get('/tcm', toBackendListParams(params)).then(res => res.data)
}
export function getTcm(id) {
  return get(`/tcm/${id}`).then(res => res.data)
}
export function createTcm(data) {
  return post('/tcm', data).then(res => res.data)
}
export function updateTcm(id, data) {
  return put(`/tcm/${id}`, data).then(res => res.data)
}
export function deleteTcm(id) {
  return del(`/tcm/${id}`).then(res => res.data)
}

// 中药处方模板（医生个人）
export function getTcmTemplates(params = {}) {
  return get('/tcm/templates', toBackendListParams(params)).then(res => res.data)
}
export function getTcmTemplate(id) {
  return get(`/tcm/templates/${id}`).then(res => res.data)
}
export function createTcmTemplate(data) {
  return post('/tcm/templates', data).then(res => res.data)
}
export function updateTcmTemplate(id, data) {
  return put(`/tcm/templates/${id}`, data).then(res => res.data)
}
export function deleteTcmTemplate(id) {
  return del(`/tcm/templates/${id}`).then(res => res.data)
}

// 协定处方
export function getTcmAgreements(params = {}) {
  return get('/tcm/agreements', toBackendListParams(params)).then(res => res.data)
}

export default {
  getTcms,
  getTcm,
  createTcm,
  updateTcm,
  deleteTcm,
  getTcmTemplates,
  getTcmTemplate,
  createTcmTemplate,
  updateTcmTemplate,
  deleteTcmTemplate,
  getTcmAgreements
}

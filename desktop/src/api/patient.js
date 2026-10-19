import { get, post, put, del } from '@/utils/request'

// 后端 list 接口使用 skip / limit 分页（GET /patients）
function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = {
    skip: (page - 1) * pageSize,
    limit: pageSize
  }
  const keyword = params.keyword || params.search
  if (keyword) backend.search = keyword
  if (params.gender) backend.gender = params.gender
  return backend
}

// 返回 { items, pagination }
export function getPatients(params = {}) {
  return get('/patients', toBackendListParams(params)).then(res => res.data || { items: [], pagination: {} })
}

export function getPatient(id) {
  return get(`/patients/${id}`).then(res => res.data)
}

export function createPatient(data) {
  return post('/patients', data).then(res => res.data)
}

export function updatePatient(id, data) {
  return put(`/patients/${id}`, data).then(res => res.data)
}

// 患者余额充值（含赠送）
export function rechargePatient(id, data) {
  return post(`/patients/${id}/recharge`, data).then(res => res.data)
}

export function deletePatient(id) {
  return del(`/patients/${id}`).then(res => res.data)
}

// 家庭成员
export function getFamilyMembers(patientId, params = {}) {
  return get(`/patients/${patientId}/family-members`, {
    page: params.page || 1,
    page_size: params.page_size || 100,
  }).then(res => res.data)
}

export function createFamilyMember(patientId, data) {
  return post(`/patients/${patientId}/family-members`, data).then(res => res.data)
}

export function updateFamilyMember(patientId, id, data) {
  return put(`/patients/${patientId}/family-members/${id}`, data).then(res => res.data)
}

export function deleteFamilyMember(patientId, id) {
  return del(`/patients/${patientId}/family-members/${id}`).then(res => res.data)
}

export function searchPatients(keyword, limit = 50) {
  return get('/patients', { search: keyword, limit }).then(res => res.data)
}

export function getPatientVisits(id) {
  return get(`/patients/${id}/visits`).then(res => res.data)
}

// 会员等级列表（用于患者表单 member_level_id 选择）
export function getMemberLevels(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || 100
  return get('/member/levels', { page, page_size: pageSize }).then(res => res.data || { items: [] })
}

export default {
  getPatients,
  getPatient,
  createPatient,
  updatePatient,
  deletePatient,
  searchPatients,
  getPatientVisits,
  getMemberLevels
}

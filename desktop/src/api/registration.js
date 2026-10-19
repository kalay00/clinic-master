import { get, post, put, del } from '@/utils/request'

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = {
    page,
    page_size: pageSize
  }
  if (params.keyword || params.search) backend.search = params.keyword || params.search
  if (params.status) backend.status = params.status
  if (params.patient_id) backend.patient_id = params.patient_id
  if (params.doctor_id) backend.doctor_id = params.doctor_id
  if (params.department_id) backend.department_id = params.department_id
  if (params.payment_status) backend.payment_status = params.payment_status
  if (params.start_date) backend.start_date = params.start_date
  if (params.end_date) backend.end_date = params.end_date
  return backend
}

export function getRegistrations(params = {}) {
  return get('/registrations', toBackendListParams(params)).then(res => res.data)
}

export function getRegistration(id) {
  return get(`/registrations/${id}`).then(res => res.data)
}

export function updateRegistration(id, data) {
  return put(`/registrations/${id}`, data).then(res => res.data)
}

export function deleteRegistration(id) {
  return del(`/registrations/${id}`).then(res => res.data)
}

export function createRegistration(data) {
  return post('/registrations', data).then(res => res.data)
}

export function cancelRegistration(id) {
  return post(`/registrations/${id}/cancel`).then(res => res.data)
}

export function payRegistration(id, data) {
  return post(`/registrations/${id}/pay`, data).then(res => res.data)
}

export function refundRegistration(id, data) {
  return post(`/registrations/${id}/refund`, data).then(res => res.data)
}

// 排班
// 注意：该接口分页参数为 skip/limit（非 page/page_size），
// 且返回结构为 { items, pagination: { total, ... } }，这里统一归一化为 { items, total }
export function getSchedules(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = {
    skip: (page - 1) * pageSize,
    limit: pageSize,
  }
  if (params.doctor_id) backend.doctor_id = params.doctor_id
  if (params.department_id) backend.department_id = params.department_id
  if (params.date) backend.schedule_date = params.date
  if (params.start_date) backend.start_date = params.start_date
  if (params.end_date) backend.end_date = params.end_date
  return get('/registrations/schedules', backend).then(res => {
    const data = res.data || {}
    return {
      ...data,
      items: data.items || [],
      total: data.pagination?.total ?? (data.items || []).length,
    }
  })
}

export function getSchedule(id) {
  return get(`/registrations/schedules/${id}`).then(res => res.data)
}

export function createSchedule(data) {
  return post('/registrations/schedules', data).then(res => res.data)
}

export function updateSchedule(id, data) {
  return put(`/registrations/schedules/${id}`, data).then(res => res.data)
}

export function deleteSchedule(id) {
  return del(`/registrations/schedules/${id}`).then(res => res.data)
}

export function pauseSchedule(id) {
  return post(`/registrations/schedules/${id}/pause`).then(res => res.data)
}

export function resumeSchedule(id) {
  return post(`/registrations/schedules/${id}/resume`).then(res => res.data)
}

export function swapSchedule(id, newDoctorId) {
  return post(`/registrations/schedules/${id}/swap?new_doctor_id=${encodeURIComponent(newDoctorId)}`).then(res => res.data)
}

export default {
  getRegistrations,
  getRegistration,
  createRegistration,
  updateRegistration,
  deleteRegistration,
  cancelRegistration,
  payRegistration,
  refundRegistration,
  getSchedules,
  getSchedule,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  pauseSchedule,
  resumeSchedule,
  swapSchedule
}

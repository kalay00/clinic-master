import { get, post, put, del } from '@/utils/request'

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = {
    page,
    page_size: pageSize
  }
  const keyword = params.keyword || params.search
  if (keyword) backend.keyword = keyword
  if (params.patient_id) backend.patient_id = params.patient_id
  if (params.doctor_id) backend.doctor_id = params.doctor_id
  if (params.registration_id) backend.registration_id = params.registration_id
  if (params.start_date) backend.start_date = params.start_date
  if (params.end_date) backend.end_date = params.end_date
  return backend
}

// 病历
export function getMedicalRecords(params = {}) {
  return get('/treatments', toBackendListParams(params)).then(res => res.data)
}

export function getMedicalRecord(id) {
  return get(`/treatments/${id}`).then(res => res.data)
}

export function createMedicalRecord(data) {
  return post('/treatments', data).then(res => res.data)
}

export function updateMedicalRecord(id, data) {
  return put(`/treatments/${id}`, data).then(res => res.data)
}

export function deleteMedicalRecord(id) {
  return del(`/treatments/${id}`).then(res => res.data)
}

// 处方
export function getPrescriptions(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = { page, page_size: pageSize }
  if (params.patient_id) backend.patient_id = params.patient_id
  if (params.doctor_id) backend.doctor_id = params.doctor_id
  if (params.medical_record_id) backend.medical_record_id = params.medical_record_id
  if (params.status) backend.status = params.status
  return get('/treatments/prescriptions', backend).then(res => res.data)
}

export function getPrescription(id) {
  return get(`/treatments/prescriptions/${id}`).then(res => res.data)
}

export function createPrescription(data) {
  return post('/treatments/prescriptions', data).then(res => res.data)
}

export function updatePrescription(id, data) {
  return put(`/treatments/prescriptions/${id}`, data).then(res => res.data)
}

export function deletePrescription(id) {
  return del(`/treatments/prescriptions/${id}`).then(res => res.data)
}

// 处方服务项目
export function getPrescriptionServices(prescriptionId) {
  return get(`/prescriptions/${prescriptionId}/services`).then(res => res.data)
}

export function addPrescriptionService(prescriptionId, data) {
  return post(`/prescriptions/${prescriptionId}/services`, data).then(res => res.data)
}

export function removePrescriptionService(itemId) {
  return del(`/prescriptions/services/${itemId}`).then(res => res.data)
}

export default {
  getMedicalRecords,
  getMedicalRecord,
  createMedicalRecord,
  updateMedicalRecord,
  deleteMedicalRecord,
  getPrescriptions,
  getPrescription,
  createPrescription,
  updatePrescription,
  deletePrescription,
  getPrescriptionServices,
  addPrescriptionService,
  removePrescriptionService
}

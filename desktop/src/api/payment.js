import { get, post, put, del } from '@/utils/request'

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = {
    page,
    page_size: pageSize
  }
  if (params.keyword || params.search) backend.search = params.keyword || params.search
  if (params.registration_id) backend.registration_id = params.registration_id
  if (params.patient_id) backend.patient_id = params.patient_id
  if (params.status) backend.status = params.status
  if (params.bill_type) backend.bill_type = params.bill_type
  return backend
}

// 账单
export function getBills(params = {}) {
  return get('/payments/bills', toBackendListParams(params)).then(res => res.data)
}

export function getBill(id) {
  return get(`/payments/bills/${id}`).then(res => res.data)
}

export function createBill(data) {
  return post('/payments/bills', data).then(res => res.data)
}

export function payBill(id, data) {
  return post(`/payments/bills/${id}/pay`, data).then(res => res.data)
}

export function refundBill(id, data) {
  return post(`/payments/bills/${id}/refund`, data).then(res => res.data)
}

// 支付记录
export function getPayments(params = {}) {
  return get('/payments/payments', params).then(res => res.data)
}

export default {
  getBills,
  getBill,
  createBill,
  payBill,
  refundBill,
  getPayments
}

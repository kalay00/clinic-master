import { get, post, put, del } from '@/utils/request'

// 费用类型常量
export const FEE_TYPE = {
  REGISTRATION: 'registration',
  TREATMENT: 'treatment',
  EXTRA: 'extra',
  OTHER: 'other',
}

function toListParams(params = {}) {
  const backend = {
    page: params.page || 1,
    page_size: params.page_size || params.pageSize || 100,
  }
  if (params.fee_type) backend.fee_type = params.fee_type
  if (params.name) backend.name = params.name
  if (params.status !== undefined && params.status !== null && params.status !== '') {
    backend.status = params.status
  }
  return backend
}

export function getFees(params = {}) {
  return get('/fees', toListParams(params)).then(res => res.data)
}

export function getFee(id) {
  return get(`/fees/${id}`).then(res => res.data)
}

export function createFee(data) {
  return post('/fees', data).then(res => res.data)
}

export function updateFee(id, data) {
  return put(`/fees/${id}`, data).then(res => res.data)
}

export function deleteFee(id) {
  return del(`/fees/${id}`).then(res => res.data)
}

export default {
  getFees,
  getFee,
  createFee,
  updateFee,
  deleteFee,
}

import { get, post, put } from '@/utils/request'

// 会员列表（基于患者资产），后端返回 { items, pagination }
export function getMembers(params = {}) {
  const page = params.page || 1
  const pageSize = params.pageSize || params.page_size || 10
  const backend = {
    page,
    page_size: pageSize,
    keyword: params.keyword || undefined,
    level_id: params.level_id || undefined,
    status: params.status || undefined,
    member_type: params.member_type || undefined
  }
  return get('/member/members', backend).then(res => res.data || { items: [], pagination: {} })
}

export function rechargeMember(id, data = {}) {
  return post(`/member/members/${id}/recharge`, {
    amount: Number(data.amount),
    method: data.payWay || 'cash',
    remark: data.remark || undefined
  }).then(res => res.data)
}

export function refundMember(id, data = {}) {
  return post(`/member/members/${id}/refund`, {
    amount: Number(data.amount),
    method: data.payWay || 'cash',
    remark: data.remark || undefined
  }).then(res => res.data)
}

export function adjustMemberPoints(id, data = {}) {
  return post(`/member/members/${id}/points`, {
    points: Number(data.points),
    remark: data.remark || undefined
  }).then(res => res.data)
}

export function setMemberLevel(id, data = {}) {
  return post(`/member/members/${id}/level`, {
    member_level_id: data.member_level_id,
    remark: data.remark || undefined
  }).then(res => res.data)
}

export function updateMember(id, data = {}) {
  return put(`/member/members/${id}`, data).then(res => res.data)
}

export function getMemberTransactions(id, params = {}) {
  const page = params.page || 1
  const pageSize = params.pageSize || params.page_size || 20
  return get(`/member/members/${id}/transactions`, {
    page,
    page_size: pageSize,
    type: params.type || undefined
  }).then(res => res.data || { items: [], pagination: {} })
}

// 会员等级 CRUD（前缀 /member/levels）
export function getLevels(params = {}) {
  const page = params.page || 1
  const pageSize = params.pageSize || params.page_size || 100
  return get('/member/levels', { page, page_size: pageSize }).then(res => res.data || { items: [] })
}
export function createLevel(data = {}) {
  return post('/member/levels', data).then(res => res.data)
}
export function updateLevel(id, data = {}) {
  return put(`/member/levels/${id}`, data).then(res => res.data)
}

export default {
  getMembers,
  rechargeMember,
  refundMember,
  adjustMemberPoints,
  setMemberLevel,
  updateMember,
  getMemberTransactions,
  getLevels,
  createLevel,
  updateLevel
}

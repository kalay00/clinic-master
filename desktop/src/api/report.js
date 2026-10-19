import { get } from '@/utils/request'

// 收入/收费报表
export function getRevenueReport(params = {}) {
  return get('/reports/revenue', params).then(res => res.data)
}

// 就诊量报表
export function getVisitsReport(params = {}) {
  return get('/reports/visits', params).then(res => res.data)
}

// 药品销售报表
export function getDrugsReport(params = {}) {
  return get('/reports/drugs', params).then(res => res.data)
}

// 每日统计
export function getDailyStatistics(params = {}) {
  return get('/reports/daily', params).then(res => res.data)
}

// 工作台统计
export function getDashboardStats(params = {}) {
  return get('/reports/dashboard', params).then(res => res.data)
}

// 患者报表
export function getPatientsReport(params = {}) {
  return get('/reports/patients', params).then(res => res.data)
}

import { get } from '@/utils/request'

export function getDashboardData() {
  return get('/dashboard/data')
}

export function getChartData(type) {
  return get('/dashboard/chart', { type })
}

export default {
  getDashboardData,
  getChartData
}

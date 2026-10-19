import { get, put } from '@/utils/request'

export function getTenantConfig() {
  return get('/tenant/config').then(res => res.data)
}

export function updateTenantConfig(data) {
  return put('/tenant/config', data).then(res => res.data)
}

export function getPharmacistReviewStatus() {
  return get('/tenant/pharmacist-review-enabled').then(res => res.data)
}

export function getCurrentTenant() {
  return get('/tenant/current').then(res => res.data)
}

export function updateCurrentTenant(data) {
  return put('/tenant/current', data).then(res => res.data)
}

export default {
  getTenantConfig,
  updateTenantConfig,
  getPharmacistReviewStatus,
  getCurrentTenant,
  updateCurrentTenant
}

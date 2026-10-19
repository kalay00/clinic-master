import { get, post, put, del } from '@/utils/request'

export function platformLogin(data) {
  return post('/platform/login', data).then(res => res.data)
}

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 100
  const backend = {
    page,
    page_size: pageSize
  }
  if (params.search) backend.search = params.search
  if (params.status) backend.status = params.status
  return backend
}

export function getTenants(params = {}) {
  return get('/platform/tenants', toBackendListParams(params)).then(res => res.data)
}
export function getTenantDetail(id) {
  return get(`/platform/tenants/${id}`).then(res => res.data)
}
export function createTenant(data) {
  return post('/platform/tenants', data).then(res => res.data)
}
export function updateTenant(id, data) {
  return put(`/platform/tenants/${id}`, data).then(res => res.data)
}
export function deleteTenant(id) {
  return del(`/platform/tenants/${id}`).then(res => res.data)
}
export function getStatistics() {
  return get('/platform/statistics').then(res => res.data)
}
export function getAuditLogs(params = {}) {
  const queryParams = {}
  if (params.tenant_id) queryParams.tenant_id = params.tenant_id
  if (params.user_id) queryParams.user_id = params.user_id
  if (params.resource_type) queryParams.resource_type = params.resource_type
  if (params.operation_type) queryParams.operation_type = params.operation_type
  if (params.start_date) queryParams.start_date = params.start_date
  if (params.end_date) queryParams.end_date = params.end_date
  if (params.page) queryParams.skip = (params.page - 1) * (params.page_size || 100)
  if (params.page_size) queryParams.limit = params.page_size
  return get('/platform/audit-logs', queryParams).then(res => res.data)
}
export function updateTenantAdminPassword(tenantId, newPassword) {
  return post(`/platform/tenants/${tenantId}/admin-password`, { new_password: newPassword }).then(res => res.data)
}

export default {
  platformLogin,
  getTenants,
  getTenantDetail,
  createTenant,
  updateTenant,
  deleteTenant,
  getStatistics,
  getAuditLogs,
  updateTenantAdminPassword
}

import { get, del } from '@/utils/request'

// 操作日志
export function getLogs(params = {}) {
  const backend = {
    page: params.page || 1,
    page_size: params.page_size || params.pageSize || 20,
  }
  if (params.operation_type) backend.operation_type = params.operation_type
  if (params.resource_type) backend.resource_type = params.resource_type
  if (params.status) backend.status = params.status
  if (params.keyword) backend.keyword = params.keyword
  return get('/logs', backend).then(res => res.data)
}

export function getLog(id) {
  return get(`/logs/${id}`).then(res => res.data)
}

export function deleteLog(id) {
  return del(`/logs/${id}`).then(res => res.data)
}
